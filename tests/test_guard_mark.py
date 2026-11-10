import importlib.util
import pathlib

import pytest

_path = pathlib.Path(__file__).parent.parent / "tools" / "guard_mark.py"
_spec = importlib.util.spec_from_file_location("guard_mark", _path)
mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(mod)


def test_mark_roundtrip():
    assert mod.marked_line("x\n" + mod.mark("liveness") + "\ny")


def test_unknown_kind_refused():
    with pytest.raises(ValueError):
        mod.mark("evil")


@pytest.mark.parametrize("text", ["<!-- guard: liveness -->", "a <!--guard:x--> b", "<!-- GUARD: Status -->"])
def test_has_mark_catches_variants(text):
    assert mod.has_mark(text)


def test_has_mark_clean_text():
    assert not mod.has_mark("normal text") and not mod.has_mark(None)
