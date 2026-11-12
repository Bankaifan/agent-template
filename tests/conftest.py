import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent.parent / "tools"))

import pytest

ROOT = pathlib.Path(__file__).resolve().parent.parent


def is_downstream(root=ROOT):
    """A downstream project has .agents/template.json (design 0011 section 2); the template repo does not."""
    return (root / ".agents" / "template.json").is_file()


def pytest_configure(config):
    config.addinivalue_line(
        "markers",
        "slow: expensive test (over about 5 s, or needs a network or service); "
        "see docs/design/0009-test-scoping.md",
    )
    config.addinivalue_line(
        "markers",
        "template_only: test of template-only files; skipped in downstream projects (design 0014 section 4.4)",
    )


def pytest_collection_modifyitems(config, items):
    if not is_downstream():
        return
    skip = pytest.mark.skip(reason="template_only: this is a downstream project (.agents/template.json exists)")
    for item in items:
        if item.get_closest_marker("template_only"):
            item.add_marker(skip)


@pytest.fixture(autouse=True)
def _no_ci_repo(monkeypatch):
    """CI sets GH_REPO; tests that need it set it themselves, so local and CI runs match."""
    monkeypatch.delenv("GH_REPO", raising=False)
