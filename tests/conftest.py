import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent.parent / "tools"))

import pytest


@pytest.fixture(autouse=True)
def _no_ci_repo(monkeypatch):
    """CI sets GH_REPO; tests that need it set it themselves, so local and CI runs match."""
    monkeypatch.delenv("GH_REPO", raising=False)
