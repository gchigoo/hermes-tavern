"""Phase 90: repo hygiene release preflight checks."""

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]

LICENSE_FILE = REPO_ROOT / "LICENSE"
WORKFLOW_FILE = REPO_ROOT / ".github/workflows/test.yml"
PATCH_FILE = REPO_ROOT / "patches/hermes-agent-core-changes.patch"
REQUIREMENTS_TEST_FILE = REPO_ROOT / "requirements-test.txt"
CONTRIBUTING_FILE = REPO_ROOT / "CONTRIBUTING.md"

REQUIRED_GITIGNORE_PATTERNS = {
    "Python bytecode/cache": [
        "__pycache__/",
        "*.pyc",
        ".pytest_cache/",
    ],
    "virtualenv/env": [
        ".venv/",
        "venv/",
        ".env",
    ],
    "package artifacts": [
        "*.egg-info/",
        "build/",
        "dist/",
    ],
    "local phase runner/log artifacts": [
        "logs/continuous-phases/",
        "*.log",
    ],
}


def _gitignore_patterns() -> set[str]:
    gitignore = REPO_ROOT / ".gitignore"
    return {
        line.strip()
        for line in gitignore.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    }


def test_gitignore_covers_standalone_plugin_generated_artifacts():
    """Release preflight keeps local/generated standalone plugin artifacts ignored."""
    patterns = _gitignore_patterns()
    missing_by_category = {
        category: sorted(set(required) - patterns)
        for category, required in REQUIRED_GITIGNORE_PATTERNS.items()
        if set(required) - patterns
    }

    assert missing_by_category == {}


def test_license_and_ci_workflow_exist_for_public_preflight():
    assert LICENSE_FILE.is_file(), "LICENSE file required for public distribution"
    assert WORKFLOW_FILE.is_file(), "CI workflow file required for public repo preflight"


def test_workflow_has_no_publish_or_deploy_or_secrets_commands():
    workflow_text = WORKFLOW_FILE.read_text(encoding="utf-8").lower()
    forbidden = [
        "publish",
        "deploy",
        "twine",
        "ghp_",
        "upload",
    ]

    for marker in forbidden:
        assert marker not in workflow_text, f"found forbidden workflow marker: {marker}"


def test_workflow_installs_release_preflight_dependencies_in_runner_env():
    """Public CI installs every test/build dependency needed from a clean runner."""
    workflow_text = WORKFLOW_FILE.read_text(encoding="utf-8").lower()

    required_dependencies = [
        "setuptools>=68",
        "wheel",
        "build",
        "pytest",
        "pytest-asyncio",
        "pyyaml",
    ]
    requirements_text = REQUIREMENTS_TEST_FILE.read_text(encoding="utf-8").lower()
    for dependency in required_dependencies:
        assert dependency in requirements_text, f"missing dependency in requirements-test.txt: {dependency}"

    assert "python -m pip install --upgrade -r requirements-test.txt" in workflow_text
    assert "pip install --upgrade \"setuptools>=68\"" not in workflow_text
    assert "pip install --upgrade setuptools>=68" not in workflow_text
    assert "pip install --upgrade pyyaml" not in workflow_text
    assert "pip install --upgrade pytest-asyncio" not in workflow_text

    assert "--user" not in workflow_text
    assert "force_javascript_actions_to_node24" in workflow_text


def test_requirements_test_file_exists_and_has_expected_dependencies():
    assert REQUIREMENTS_TEST_FILE.is_file()

    expected_dependencies = {
        "setuptools>=68",
        "wheel",
        "build",
        "pytest",
        "pytest-asyncio",
        "pyyaml",
    }

    observed_dependencies = {
        line.strip().lower()
        for line in REQUIREMENTS_TEST_FILE.read_text(encoding="utf-8").splitlines()
        if line.strip()
    }

    assert observed_dependencies == expected_dependencies


def test_contributing_guide_exists():
    assert CONTRIBUTING_FILE.is_file()


def test_patch_placeholder_contains_no_real_sk_secret_pattern():
    patch_text = PATCH_FILE.read_text(encoding="utf-8")
    assert "sk-" not in patch_text, "found sk- secret-pattern text in patch file"


def test_contributing_guide_has_required_commands_and_scope_rules():
    text = CONTRIBUTING_FILE.read_text(encoding="utf-8").lower()
    required_phrases = [
        "requirements-test.txt",
        "python -m pip install -r requirements-test.txt",
        "python -m pip install -e . --no-deps",
        "py_compile",
        "tests/test_hermes_tavern_repo_hygiene.py",
        "tests/test_hermes_tavern_readme_docs.py",
        "tests/test_hermes_tavern_packaging.py",
        "tests/test_hermes_tavern_*.py",
        "scope",
        "contribution",
        "secret handling",
        "safe validation rules",
        "ordinary contributions",
    ]

    for phrase in required_phrases:
        assert phrase in text, f"missing contributing guide phrase: {phrase}"


def test_contributing_guide_prohibits_gateway_and_external_endpoint_calls():
    text = CONTRIBUTING_FILE.read_text(encoding="utf-8").lower()
    forbidden_patterns = [
        "hermes gateway start",
        "hermes gateway restart",
        "hermes gateway reload",
        "hermes gateway kill",
        "hermes gateway manage",
        "gateway start",
        "gateway restart",
        "gateway reload",
        "gateway kill",
        "gateway manage",
        "systemctl start",
        "systemctl restart",
        "docker compose",
        "service start",
    ]

    for pattern in forbidden_patterns:
        assert pattern not in text, f"found forbidden operational pattern in CONTRIBUTING: {pattern}"
