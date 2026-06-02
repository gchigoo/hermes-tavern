"""Phase 90: repo hygiene release preflight checks."""

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]

LICENSE_FILE = REPO_ROOT / "LICENSE"
WORKFLOW_FILE = REPO_ROOT / ".github/workflows/test.yml"
PATCH_FILE = REPO_ROOT / "patches/hermes-agent-core-changes.patch"

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


def test_patch_placeholder_contains_no_real_sk_secret_pattern():
    patch_text = PATCH_FILE.read_text(encoding="utf-8")
    assert "sk-" not in patch_text, "found sk- secret-pattern text in patch file"
