"""Phase 48/49: standalone packaging and plugin entrypoint hardening tests."""

import importlib
import importlib.resources
import os
from pathlib import Path
import subprocess
import sys
import tarfile
import textwrap
import tomllib
from unittest.mock import ANY
from urllib.parse import urlparse
import venv
import zipfile


class FakePluginContext:
    def __init__(self):
        self.hooks: list = []

    def register_hook(self, hook_name: str, callback) -> None:
        self.hooks.append((hook_name, callback))


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def _load_pyproject() -> dict:
    return tomllib.loads((_repo_root() / "pyproject.toml").read_text(encoding="utf-8"))


def _load_plugin_manifest() -> dict:
    import yaml

    manifest = _repo_root() / "src" / "hermes_tavern" / "plugin.yaml"
    return yaml.safe_load(manifest.read_text(encoding="utf-8"))


def _offline_package_env() -> dict[str, str]:
    return {
        **os.environ,
        "PYTHONPATH": "",
        "PIP_DISABLE_PIP_VERSION_CHECK": "1",
        "PIP_NO_INDEX": "1",
    }


def _build_package_artifacts(tmp_path: Path) -> tuple[Path, Path, Path]:
    """Build package artifacts offline into tmp_path and return the first wheel."""
    repo_root = _repo_root()
    outdir = tmp_path / "dist"
    outdir.mkdir()

    env = _offline_package_env()
    build_probe = subprocess.run(
        [sys.executable, "-m", "build", "--version"],
        cwd=repo_root,
        capture_output=True,
        text=True,
        env=env,
    )
    if build_probe.returncode == 0:
        command = [
            sys.executable,
            "-m",
            "build",
            "--no-isolation",
            "--wheel",
            "--sdist",
            "--outdir",
            str(outdir),
        ]
    else:
        command = [
            sys.executable,
            "-m",
            "pip",
            "wheel",
            ".",
            "--no-build-isolation",
            "--no-deps",
            "--wheel-dir",
            str(outdir),
        ]

    result = subprocess.run(
        command,
        cwd=repo_root,
        capture_output=True,
        text=True,
        env=env,
    )
    assert result.returncode == 0, (
        f"Package artifact build failed.\ncommand: {' '.join(command)}\n"
        f"stdout: {result.stdout}\nstderr: {result.stderr}"
    )

    wheels = sorted(outdir.glob("hermes_tavern-*.whl"))
    assert wheels, f"No hermes_tavern wheel produced in {outdir}; got {sorted(outdir.iterdir())}"
    return repo_root, outdir, wheels[0]


def _install_wheel_in_isolated_venv(tmp_path: Path, wheel_path: Path) -> tuple[Path, Path, dict[str, str]]:
    """Install wheel into a temporary venv and return (python, outside cwd, env)."""
    outside = tmp_path / "outside"
    outside.mkdir()

    venv_dir = tmp_path / "venv"
    venv.EnvBuilder(with_pip=True).create(venv_dir)
    venv_python = venv_dir / ("Scripts/python.exe" if os.name == "nt" else "bin/python")

    env = {**_offline_package_env(), "PYTHONNOUSERSITE": "1"}
    install_result = subprocess.run(
        [
            str(venv_python),
            "-m",
            "pip",
            "install",
            "--no-index",
            "--no-deps",
            str(wheel_path),
        ],
        cwd=outside,
        capture_output=True,
        text=True,
        env=env,
    )
    assert install_result.returncode == 0, (
        "Wheel install into isolated venv failed.\n"
        f"stdout: {install_result.stdout}\nstderr: {install_result.stderr}"
    )

    return venv_python, outside, env


def test_direct_hermes_tavern_register_hooks_without_legacy_namespace():
    """hermes_tavern.register works via the standalone package import path."""
    import hermes_tavern

    ctx = FakePluginContext()
    hermes_tavern.register(ctx)

    assert ctx.hooks == [("pre_gateway_dispatch", ANY)]
    assert callable(ctx.hooks[0][1])


def test_register_uses_canonical_gateway_hook_callback_identity():
    """register wires the canonical gateway hook function, not a legacy alias."""
    import hermes_tavern
    from hermes_tavern.gateway_hook import pre_gateway_dispatch

    ctx = FakePluginContext()
    hermes_tavern.register(ctx)

    assert ctx.hooks == [("pre_gateway_dispatch", pre_gateway_dispatch)]
    assert ctx.hooks[0][1] is pre_gateway_dispatch
    assert ctx.hooks[0][1].__module__ == "hermes_tavern.gateway_hook"


def test_plugin_yaml_available_as_package_data():
    """plugin.yaml is readable via importlib.resources (works installed or from src/)."""
    text = (
        importlib.resources.files("hermes_tavern")
        .joinpath("plugin.yaml")
        .read_text(encoding="utf-8")
    )
    assert "hermes-tavern" in text
    assert "version" in text


def test_legacy_plugins_register_delegates_to_hermes_tavern():
    """plugins.hermes_tavern.register is the same function object as hermes_tavern.register."""
    import hermes_tavern
    import plugins.hermes_tavern as legacy

    assert legacy.register is hermes_tavern.register


def test_legacy_plugins_register_wires_canonical_gateway_hook_callback_identity():
    """The legacy shim delegates to the same canonical hook callback object."""
    from hermes_tavern.gateway_hook import pre_gateway_dispatch
    import plugins.hermes_tavern as legacy

    ctx = FakePluginContext()
    legacy.register(ctx)

    assert ctx.hooks == [("pre_gateway_dispatch", pre_gateway_dispatch)]
    assert ctx.hooks[0][1] is pre_gateway_dispatch
    assert ctx.hooks[0][1].__module__ == "hermes_tavern.gateway_hook"


def test_editable_install_isolation_smoke():
    """Editable install works without conftest.py sys.path injection.

    Launches a fresh subprocess with PYTHONPATH cleared so conftest.py's src/
    injection is not active. The hermes_tavern package must be discoverable
    solely through the editable install (.pth or direct-url). This test fails
    if the packaging is broken and the in-process tests pass only due to conftest.
    """
    script = (
        "import hermes_tavern, importlib.resources, yaml;"
        " ctx = type('C', (), {'hooks': [], 'register_hook': lambda s, n, f: s.hooks.append((n, f))})();"
        " hermes_tavern.register(ctx);"
        " assert ctx.hooks[0][0] == 'pre_gateway_dispatch';"
        " text = importlib.resources.files('hermes_tavern').joinpath('plugin.yaml').read_text();"
        " data = yaml.safe_load(text);"
        " assert data.get('entry_point') == 'hermes_tavern:register', repr(data);"
        " print('isolation-smoke: PASS')"
    )
    env = {**os.environ, "PYTHONPATH": ""}
    result = subprocess.run(
        [sys.executable, "-c", script],
        capture_output=True,
        text=True,
        env=env,
    )
    assert result.returncode == 0, (
        f"Isolation smoke failed.\nstdout: {result.stdout}\nstderr: {result.stderr}"
    )
    assert "isolation-smoke: PASS" in result.stdout


def test_version_attribute_matches_package_metadata():
    """hermes_tavern.__version__ is set and matches importlib.metadata."""
    import importlib.metadata

    import hermes_tavern

    assert hasattr(hermes_tavern, "__version__"), "__version__ not defined"
    assert isinstance(hermes_tavern.__version__, str)
    assert hermes_tavern.__version__, "__version__ is empty"
    meta_version = importlib.metadata.version("hermes-tavern")
    assert hermes_tavern.__version__ == meta_version, (
        f"__version__ {hermes_tavern.__version__!r} != metadata {meta_version!r}"
    )


def test_plugin_yaml_declares_entry_point():
    """plugin.yaml entry_point key points at the canonical register function."""
    import yaml

    text = (
        importlib.resources.files("hermes_tavern")
        .joinpath("plugin.yaml")
        .read_text(encoding="utf-8")
    )
    data = yaml.safe_load(text)
    assert data["entry_point"] == "hermes_tavern:register"


def test_plugin_manifest_entrypoint_consistency_matrix():
    """pyproject, plugin.yaml, import package, and README contracts stay aligned."""
    import hermes_tavern

    repo_root = _repo_root()
    pyproject = _load_pyproject()
    plugin = _load_plugin_manifest()
    readme = (repo_root / "README.md").read_text(encoding="utf-8")

    project = pyproject["project"]
    project_name = project["name"]
    project_version = project["version"]
    plugin_entry_point = plugin["entry_point"]
    plugin_entry_module, plugin_entry_function = plugin_entry_point.split(":", 1)
    entry_point_group = project.get("entry-points", {}).get("hermes_agent.plugins")

    assert project_name == plugin["name"] == "hermes-tavern"
    assert project_version == plugin["version"] == hermes_tavern.__version__
    assert plugin_entry_point == "hermes_tavern:register"
    assert plugin_entry_module == "hermes_tavern"
    assert plugin_entry_function == "register"
    assert entry_point_group is not None, "missing hermes_agent.plugins entry point group"
    assert entry_point_group.get("hermes-tavern") == "hermes_tavern"
    assert project_name.replace("-", "_") == plugin_entry_module
    assert "-" in project_name and "_" not in project_name
    assert "_" in plugin_entry_module and "-" not in plugin_entry_module
    assert hermes_tavern.__name__ == plugin_entry_module
    assert callable(getattr(hermes_tavern, plugin_entry_function))

    assert f"python -m pip install -e /path/to/{project_name} --no-deps" in readme
    assert "python -m pip install -e . --no-deps" in readme
    assert f'entry_point: "{plugin_entry_point}"' in readme
    assert f'{project_name} = "{plugin_entry_module}"' in readme
    assert f"hermes plugins enable {project_name}" in readme


def test_plugin_yaml_entry_point_resolves_and_registers_hook():
    """plugin.yaml entry_point can be resolved the same way as the plugin loader."""
    import yaml

    text = (
        importlib.resources.files("hermes_tavern")
        .joinpath("plugin.yaml")
        .read_text(encoding="utf-8")
    )
    data = yaml.safe_load(text)
    module_name, function_name = data["entry_point"].split(":", 1)
    entry_module = importlib.import_module(module_name)
    entry_point = getattr(entry_module, function_name)

    ctx = FakePluginContext()
    entry_point(ctx)

    assert ctx.hooks == [("pre_gateway_dispatch", ANY)]
    assert callable(ctx.hooks[0][1])


def test_hermes_constants_importable_for_standalone_tests():
    """hermes_constants is importable (real or conftest stub) so tests run without hermes-agent.

    conftest.py injects a minimal stub when the real hermes_constants module is not in
    the host environment.  The contract: get_hermes_home() must return a Path so that
    db.py, images.py, and runtime_lifecycle.py can all import and call it at module level.
    """
    from pathlib import Path

    import hermes_constants

    assert callable(hermes_constants.get_hermes_home)
    result = hermes_constants.get_hermes_home()
    assert isinstance(result, Path), (
        f"get_hermes_home() returned {type(result).__name__}, expected Path"
    )


def test_package_metadata_is_complete():
    """Installed dist-info METADATA contains classifiers, license, author, and readme.

    pyproject.toml accumulated classifiers/keywords/author in phases 49-50 but the
    editable install was not refreshed, so METADATA stayed at 4 bare lines.  This test
    detects a stale dist-info METADATA so ``pip install -e .`` is not accidentally
    skipped after pyproject.toml updates.
    """
    import importlib.metadata

    md = importlib.metadata.metadata("hermes-tavern")

    assert md["Author"], "Author field missing from METADATA"
    assert md["License"], "License field missing from METADATA"
    assert md["Keywords"], "Keywords field missing from METADATA"
    assert md["Description-Content-Type"], "Description-Content-Type missing (README not embedded)"

    classifiers = md.get_all("Classifier") or []
    assert any("Programming Language :: Python" in c for c in classifiers), (
        f"No Python classifier found; got: {classifiers}"
    )
    assert any("License :: OSI Approved" in c for c in classifiers), (
        f"No license classifier found; got: {classifiers}"
    )


def test_plugin_yaml_version_matches_package_version():
    """plugin.yaml version stays in sync with the installed package version.

    When pyproject.toml version is bumped, plugin.yaml must be updated too.
    This test catches drift between the two files before it reaches production.
    """
    import yaml

    import hermes_tavern
    text = (
        importlib.resources.files("hermes_tavern")
        .joinpath("plugin.yaml")
        .read_text(encoding="utf-8")
    )
    data = yaml.safe_load(text)
    assert "version" in data, "plugin.yaml is missing the 'version' field"
    assert data["version"] == hermes_tavern.__version__, (
        f"plugin.yaml version {data['version']!r} != "
        f"package __version__ {hermes_tavern.__version__!r}"
    )


def test_source_uses_canonical_hermes_tavern_imports():
    """Standalone source must not regress to legacy plugins.hermes_tavern imports.

    The compatibility namespace is intentionally kept for old callers and tests, but
    production source under src/hermes_tavern/ should import through the canonical
    hermes_tavern package. This keeps editable installs and wheel installs independent
    from the legacy repo-root plugins/ shim.
    """
    source_root = Path(__file__).resolve().parents[1] / "src" / "hermes_tavern"
    offenders: list[str] = []
    for path in sorted(source_root.rglob("*.py")):
        text = path.read_text(encoding="utf-8")
        if "plugins.hermes_tavern" in text or "from plugins" in text or "import plugins" in text:
            offenders.append(str(path.relative_to(source_root.parents[1])))

    assert offenders == []


def test_package_build_artifacts_include_plugin_data_and_metadata(tmp_path):
    """Build wheel/sdist artifacts offline and inspect their contents directly."""
    repo_root, outdir, wheel_path = _build_package_artifacts(tmp_path)
    pyproject = tomllib.loads((repo_root / "pyproject.toml").read_text(encoding="utf-8"))
    package_version = pyproject["project"]["version"]

    with zipfile.ZipFile(wheel_path) as wheel:
        names = set(wheel.namelist())
        assert "hermes_tavern/__init__.py" in names
        assert "hermes_tavern/plugin.yaml" in names
        metadata_names = sorted(
            name for name in names if name.endswith(".dist-info/METADATA")
        )
        assert len(metadata_names) == 1, metadata_names
        metadata = wheel.read(metadata_names[0]).decode("utf-8")
        assert "Name: hermes-tavern" in metadata
        assert f"Version: {package_version}" in metadata

    sdists = sorted(outdir.glob("*.tar.gz"))
    if sdists:
        with tarfile.open(sdists[0], "r:gz") as sdist:
            names = set(sdist.getnames())
        assert any(name.endswith("/pyproject.toml") for name in names), sdists[0]
        assert any(
            name.endswith("/src/hermes_tavern/plugin.yaml") for name in names
        ), sdists[0]


def test_wheel_payload_boundary_excludes_repo_root_artifacts(tmp_path):
    """Built wheel should only include intended package payload and metadata."""
    _, _, wheel_path = _build_package_artifacts(tmp_path)

    with zipfile.ZipFile(wheel_path) as wheel:
        names = set(wheel.namelist())

        # Required payload.
        assert "hermes_tavern/__init__.py" in names
        assert "hermes_tavern/plugin.yaml" in names

        # Entry point metadata contract.
        entry_points = [
            name for name in names if name.endswith(".dist-info/entry_points.txt")
        ]
        assert len(entry_points) == 1, entry_points
        entry_points_text = wheel.read(entry_points[0]).decode("utf-8")
        assert "[hermes_agent.plugins]" in entry_points_text
        assert "hermes-tavern = hermes_tavern" in entry_points_text

        forbidden_path_prefixes = ("plugins/", "tests/", "design/", "patches/", "__pycache__/")
        for forbidden in forbidden_path_prefixes:
            assert not any(name.startswith(forbidden) for name in names), (
                f"forbidden top-level payload present: {forbidden}"
            )

        assert not any(
            name == "conftest.py" or name.endswith("/conftest.py") for name in names
        ), "forbidden payload present: conftest.py"
        assert not any(
            name == "smoke_turn_controls.py" or name.endswith("/smoke_turn_controls.py")
            for name in names
        ), "forbidden payload present: smoke_turn_controls.py"
        assert not any("__pycache__/" in name for name in names), "forbidden payload present: __pycache__/"
        assert not any(name.endswith(".pyc") for name in names), "forbidden payload present: .pyc"


def test_wheel_install_isolated_smoke_uses_installed_package_only(tmp_path):
    """Wheel install works from outside the repo without path injection or legacy shim."""
    repo_root, _, wheel_path = _build_package_artifacts(tmp_path)
    venv_python, outside, env = _install_wheel_in_isolated_venv(tmp_path, wheel_path)

    script = outside / "wheel_smoke.py"
    script.write_text(
        textwrap.dedent(
            """
            import importlib.resources
            import pathlib
            import sys

            repo_root = pathlib.Path(sys.argv[1]).resolve()
            cwd = pathlib.Path.cwd().resolve()
            assert cwd != repo_root and repo_root not in cwd.parents, (cwd, repo_root)

            for raw_path in sys.path:
                if not raw_path:
                    continue
                path = pathlib.Path(raw_path).resolve()
                assert path != repo_root and repo_root not in path.parents, sys.path

            import hermes_tavern

            module_file = pathlib.Path(hermes_tavern.__file__).resolve()
            assert repo_root not in module_file.parents, module_file

            plugin_text = (
                importlib.resources.files("hermes_tavern")
                .joinpath("plugin.yaml")
                .read_text(encoding="utf-8")
            )
            assert 'entry_point: "hermes_tavern:register"' in plugin_text, plugin_text

            class Context:
                def __init__(self):
                    self.hooks = []

                def register_hook(self, name, callback):
                    self.hooks.append((name, callback))

            ctx = Context()
            hermes_tavern.register(ctx)

            assert len(ctx.hooks) == 1, ctx.hooks
            assert ctx.hooks[0][0] == "pre_gateway_dispatch", ctx.hooks
            assert callable(ctx.hooks[0][1]), ctx.hooks
            assert ctx.hooks[0][1].__module__ == "hermes_tavern.gateway_hook"
            print("wheel-install-isolated-smoke: PASS")
            """
        ).lstrip(),
        encoding="utf-8",
    )
    smoke_result = subprocess.run(
        [str(venv_python), str(script), str(repo_root)],
        cwd=outside,
        capture_output=True,
        text=True,
        env=env,
    )
    assert smoke_result.returncode == 0, (
        "Wheel install isolation smoke failed.\n"
        f"stdout: {smoke_result.stdout}\nstderr: {smoke_result.stderr}"
    )
    assert "wheel-install-isolated-smoke: PASS" in smoke_result.stdout


def test_wheel_entrypoint_metadata_loader_smoke_uses_installed_distribution(tmp_path):
    """Hermes-style loader discovers the installed wheel entry point metadata."""
    repo_root, _, wheel_path = _build_package_artifacts(tmp_path)
    venv_python, outside, env = _install_wheel_in_isolated_venv(tmp_path, wheel_path)

    script = outside / "entrypoint_smoke.py"
    script.write_text(
        textwrap.dedent(
            """
            import importlib.metadata
            import os
            import pathlib
            import sys

            repo_root = pathlib.Path(sys.argv[1]).resolve()
            cwd = pathlib.Path.cwd().resolve()
            assert cwd != repo_root and repo_root not in cwd.parents, (cwd, repo_root)
            assert os.environ.get("PYTHONPATH", "") == "", os.environ.get("PYTHONPATH")
            assert os.environ.get("PYTHONNOUSERSITE") == "1"

            for raw_path in sys.path:
                path = cwd if not raw_path else pathlib.Path(raw_path).resolve()
                assert path != repo_root and repo_root not in path.parents, sys.path

            try:
                group_entry_points = importlib.metadata.entry_points(
                    group="hermes_agent.plugins"
                )
            except TypeError:
                all_entry_points = importlib.metadata.entry_points()
                if hasattr(all_entry_points, "select"):
                    group_entry_points = all_entry_points.select(
                        group="hermes_agent.plugins"
                    )
                else:
                    group_entry_points = all_entry_points.get("hermes_agent.plugins", [])

            candidates = [
                entry_point
                for entry_point in group_entry_points
                if entry_point.name == "hermes-tavern"
            ]
            assert len(candidates) == 1, candidates
            entry_point = candidates[0]
            assert entry_point.group == "hermes_agent.plugins", entry_point

            loaded = entry_point.load()
            if hasattr(loaded, "register"):
                register = loaded.register
            elif callable(loaded):
                register = loaded
            else:
                raise AssertionError(f"Entry point is not register-like: {loaded!r}")
            assert callable(register), register

            import hermes_tavern

            module_file = pathlib.Path(hermes_tavern.__file__).resolve()
            assert module_file != repo_root and repo_root not in module_file.parents, (
                module_file,
                repo_root,
            )

            class Context:
                def __init__(self):
                    self.hooks = []

                def register_hook(self, name, callback):
                    self.hooks.append((name, callback))

            ctx = Context()
            register(ctx)

            assert len(ctx.hooks) == 1, ctx.hooks
            hook_name, callback = ctx.hooks[0]
            assert hook_name == "pre_gateway_dispatch", ctx.hooks
            assert callable(callback), callback
            assert callback.__module__.startswith("hermes_tavern.gateway_hook"), (
                callback,
                callback.__module__,
            )
            print("entrypoint-metadata-loader-smoke: PASS")
            """
        ).lstrip(),
        encoding="utf-8",
    )
    smoke_result = subprocess.run(
        [str(venv_python), str(script), str(repo_root)],
        cwd=outside,
        capture_output=True,
        text=True,
        env=env,
    )
    assert smoke_result.returncode == 0, (
        "Wheel entry point metadata loader smoke failed.\n"
        f"stdout: {smoke_result.stdout}\nstderr: {smoke_result.stderr}"
    )
    assert "entrypoint-metadata-loader-smoke: PASS" in smoke_result.stdout


def test_declared_hermes_tavern_package_data_is_resource_readable():
    """Declared hermes_tavern package-data remains readable from the canonical package."""
    import yaml

    repo_root = Path(__file__).resolve().parents[1]
    pyproject = tomllib.loads((repo_root / "pyproject.toml").read_text(encoding="utf-8"))
    declared = (
        pyproject.get("tool", {})
        .get("setuptools", {})
        .get("package-data", {})
        .get("hermes_tavern", [])
    )

    assert "plugin.yaml" in declared, "plugin.yaml must be declared as hermes_tavern package data"

    package_root = importlib.resources.files("hermes_tavern")
    resource_text: dict[str, str] = {}
    for resource_name in declared:
        resource = package_root.joinpath(resource_name)
        assert resource.is_file(), f"{resource_name} is not readable as package data"
        resource_text[resource_name] = resource.read_text(encoding="utf-8")
        assert resource_text[resource_name].strip(), f"{resource_name} package data is empty"

    plugin = yaml.safe_load(resource_text["plugin.yaml"])
    for field in ("name", "version", "entry_point"):
        assert plugin.get(field), f"plugin.yaml is missing loader contract field {field!r}"
    assert plugin["entry_point"] == "hermes_tavern:register"


def test_readme_installation_commands_match_packaging_metadata():
    """README install/dev commands and plugin references stay aligned with package metadata."""
    import yaml

    repo_root = Path(__file__).resolve().parents[1]
    readme = (repo_root / "README.md").read_text(encoding="utf-8")
    pyproject = tomllib.loads((repo_root / "pyproject.toml").read_text(encoding="utf-8"))
    plugin = yaml.safe_load(
        (repo_root / "src" / "hermes_tavern" / "plugin.yaml").read_text(encoding="utf-8")
    )

    project = pyproject["project"]
    project_name = project["name"]
    display_name = project_name.replace("-", " ").title()

    assert project_name == plugin["name"]
    assert project["version"] == plugin["version"]
    assert project["readme"] == "README.md"
    assert f"# {display_name}" in readme
    assert f"python -m pip install -e /path/to/{project_name}" in readme
    assert "python -m pip install -e ." in readme
    assert "python -m pytest tests/test_hermes_tavern_*.py" in readme
    assert f'entry_point: "{plugin["entry_point"]}"' in readme
    entry_points = project.get("entry-points", {}).get("hermes_agent.plugins", {})
    assert entry_points.get(project_name) == "hermes_tavern"
    assert f"{project_name} = \"hermes_tavern\"" in readme
    assert f"hermes plugins enable {project_name}" in readme


def test_pyproject_declares_package_urls_metadata():
    """Public package metadata includes required project URLs for docs and issue tracking."""
    project = _load_pyproject().get("project", {})
    urls = project.get("urls", {})

    expected = {
        "Homepage",
        "Repository",
        "Issues",
        "Changelog",
        "Security",
    }
    assert expected == set(urls), f"project.urls missing or extra keys: {set(urls)}"


def test_pyproject_urls_are_publicly_reachable_docs_and_not_operational_instructions():
    """URL metadata must be HTTPS GitHub/docs links and not contain operational guidance."""
    project_urls = _load_pyproject().get("project", {}).get("urls", {})

    forbidden_terms = (
        "gateway",
        "service",
        "restart",
        "reload",
        "start",
        "stop",
        "systemctl",
        "docker compose",
        "curl",
        "api key",
        "token",
        "credential",
        "password",
    )
    required_targets = {
        "Homepage": "README.md",
        "Changelog": "CHANGELOG.md",
        "Security": "SECURITY.md",
        "Issues": "/issues",
    }

    for key, value in project_urls.items():
        parsed = urlparse(value)
        assert parsed.scheme == "https", f"{key} must be https: {value!r}"
        assert parsed.netloc == "github.com", f"{key} must be GitHub URL: {value!r}"

        normalized = value.lower()
        assert " " not in normalized, f"{key} URL contains whitespace: {value!r}"

        for phrase in forbidden_terms:
            assert phrase not in normalized, (
                f"{key} URL contains forbidden phrase {phrase!r}: {value!r}"
            )

    for key, marker in required_targets.items():
        assert marker.lower() in project_urls[key].lower(), (
            f"{key} URL does not point to expected doc area: {project_urls[key]!r}"
        )
