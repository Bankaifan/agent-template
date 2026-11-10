import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent.parent / "tools"))

import pytest


def pytest_configure(config):
    config.addinivalue_line(
        "markers",
        "slow: expensive test (over about 5 s, or needs a network or service); "
        "see docs/design/0009-test-scoping.md",
    )


@pytest.fixture(autouse=True)
def _no_ci_repo(monkeypatch):
    """CI sets GH_REPO; tests that need it set it themselves, so local and CI runs match."""
    monkeypatch.delenv("GH_REPO", raising=False)
