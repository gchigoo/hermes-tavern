"""Phase 90: repo hygiene release preflight checks."""

import re

from pathlib import Path

import yaml


REPO_ROOT = Path(__file__).resolve().parents[1]

LICENSE_FILE = REPO_ROOT / "LICENSE"
WORKFLOW_FILE = REPO_ROOT / ".github/workflows/test.yml"
PATCH_FILE = REPO_ROOT / "patches/hermes-agent-core-changes.patch"
REQUIREMENTS_TEST_FILE = REPO_ROOT / "requirements-test.txt"
CONTRIBUTING_FILE = REPO_ROOT / "CONTRIBUTING.md"
ISSUE_TEMPLATES_ROOT = REPO_ROOT / ".github" / "ISSUE_TEMPLATE"
PR_TEMPLATE_FILE = REPO_ROOT / ".github" / "pull_request_template.md"
BUG_REPORT_TEMPLATE = ISSUE_TEMPLATES_ROOT / "bug_report.yml"
DOCS_TESTS_READINESS_TEMPLATE = ISSUE_TEMPLATES_ROOT / "docs_tests_readiness.yml"
ISSUE_TEMPLATE_CONFIG = ISSUE_TEMPLATES_ROOT / "config.yml"

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


FORBIDDEN_VALIDATION_PATTERNS = [
    "gateway restart",
    "gateway reload",
    "gateway kill",
    "gateway manage",
    "gateway start",
    "systemctl",
    "docker compose",
    "service start",
    "service restart",
    "curl",
]

SECRET_SHARING_PATTERNS = [
    re.compile(r"\bshare\s+(?:your\s+)?(?:api[_\\s-]*key|api[_\\s-]*token|secret|credential|password|token|pat)\b", re.I),
    re.compile(r"\bprovide\s+(?:your\s+)?(?:api[_\\s-]*key|api[_\\s-]*token|secret|credential|password|token|pat)\b", re.I),
    re.compile(r"\bpaste\s+(?:your\s+)?(?:api[_\\s-]*key|api[_\\s-]*token|secret|credential|password|token|pat)\b", re.I),
]


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _load_yaml_template(path: Path) -> dict:
    data = yaml.safe_load(_read_text(path))
    assert isinstance(data, dict), f"{path} must be YAML object mapping"
    return data


def _issue_field_ids(template: dict) -> set[str]:
    body = template.get("body")
    assert isinstance(body, list), f"{template.get('name', '<unknown>')} body must be a list"
    return {
        field.get("id")
        for field in body
        if isinstance(field, dict) and "id" in field
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


def test_pull_request_template_exists_and_includes_phase104_fields():
    assert PR_TEMPLATE_FILE.is_file(), "pull request template is missing"

    text = _read_text(PR_TEMPLATE_FILE).lower()
    required_fragments = [
        "scope and summary",
        "changed area type",
        "runtime behavior changed",
        "provider behavior changed",
        "gateway behavior changed",
        "credential handling changed",
        "safe offline validation",
        "side effects",
        "secret handling",
        "contributing.md",
    ]

    for fragment in required_fragments:
        assert fragment in text, f"PR template missing required fragment: {fragment}"


def test_issue_templates_exist_and_are_valid_yaml():
    issue_templates = [
        BUG_REPORT_TEMPLATE,
        DOCS_TESTS_READINESS_TEMPLATE,
        ISSUE_TEMPLATE_CONFIG,
    ]

    for template in issue_templates:
        assert template.is_file(), f"missing template: {template}"
        _load_yaml_template(template)


def test_bug_report_template_contains_expected_fields_and_redaction_language():
    template = _load_yaml_template(BUG_REPORT_TEMPLATE)
    assert template.get("name") == "Bug report"
    assert template.get("description")
    field_ids = _issue_field_ids(template)
    required_fields = {
        "actual_behavior",
        "expected_behavior",
        "reproduction",
        "environment_context",
        "offline_validation",
        "attachments_and_logs",
    }

    assert required_fields <= field_ids
    text = _read_text(BUG_REPORT_TEMPLATE).lower()

    for fragment in [
        "actual behavior",
        "expected behavior",
        "reproduction",
        "environment and context",
        "safe offline validation",
        "attachments / logs",
        "redact",
        "contributing.md",
    ]:
        assert fragment in text, f"bug report template missing expected content: {fragment}"


def test_docs_tests_readiness_template_contains_expected_fields():
    template = _load_yaml_template(DOCS_TESTS_READINESS_TEMPLATE)
    assert template.get("name") == "Docs / tests / public readiness"
    assert template.get("description")

    field_ids = _issue_field_ids(template)
    required_fields = {
        "changed_area",
        "docs_tests_scope",
        "ci_readiness",
        "public_readiness",
        "safety_and_secrets",
    }

    assert required_fields <= field_ids
    text = _read_text(DOCS_TESTS_READINESS_TEMPLATE).lower()
    for fragment in [
        "docs / tests / public readiness",
        "docs / tests",
        "ci readiness",
        "public-readiness report",
        "safety and secret handling",
        "contributing.md",
    ]:
        assert fragment in text, f"docs/tests readiness template missing required content: {fragment}"


def test_issue_template_config_keeps_blank_issues_enabled_and_links_contributing():
    data = _load_yaml_template(ISSUE_TEMPLATE_CONFIG)
    assert data.get("blank_issues_enabled") is True

    contact_links = data.get("contact_links")
    assert isinstance(contact_links, list) and contact_links, "config.yml must define at least one contact link"
    assert any(
        "contributing.md" in str(link.get("url", "")).lower() and link.get("url", "").startswith("https://github.com/")
        for link in contact_links
        if isinstance(link, dict)
    ), "config.yml must link to CONTRIBUTING.md"


def test_github_templates_do_not_contain_operational_runtime_or_secret_sharing_instructions():
    template_files = [
        PR_TEMPLATE_FILE,
        BUG_REPORT_TEMPLATE,
        DOCS_TESTS_READINESS_TEMPLATE,
        ISSUE_TEMPLATE_CONFIG,
    ]

    for template in template_files:
        text = _read_text(template).lower()
        for pattern in FORBIDDEN_VALIDATION_PATTERNS:
            assert pattern not in text, f"{template} contains forbidden pattern: {pattern}"

        for regex in SECRET_SHARING_PATTERNS:
            assert not regex.search(text), f"{template} appears to ask for credential-like sharing"
