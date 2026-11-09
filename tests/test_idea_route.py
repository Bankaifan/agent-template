import importlib.util
import pathlib

_path = pathlib.Path(__file__).parent.parent / "tools" / "idea_route.py"
_spec = importlib.util.spec_from_file_location("idea_route", _path)
mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(mod)

CFG = {"template": "Bankaifan/agent-template", "managed": ["tools/", "AGENTS.md"]}


def test_all_managed_goes_to_template():
    assert mod.route(["tools/a.py", "AGENTS.md"], CFG, "me/proj") == "template"


def test_any_project_path_stays_in_project():
    assert mod.route(["tools/a.py", "src/app.py"], CFG, "me/proj") == "project"


def test_no_template_json_stays_in_project():
    assert mod.route(["tools/a.py"], None, "me/proj") == "project"
    assert mod.load_config("/nonexistent/template.json") is None


def test_edge_cases_stay_in_project():
    assert mod.route([], CFG) == "project"
    assert mod.route(["tools/../src/x.py"], CFG) == "project"
    assert mod.route(["tools/a.py"], CFG, "bankaifan/Agent-Template") == "project"
    assert mod.route(["tools/a.py"], {**CFG, "managed": []}) == "project"


def test_load_config_rejects_bad_repo(tmp_path):
    f = tmp_path / "t.json"
    f.write_text('{"template": "a b/c; rm", "managed": ["tools/"]}')
    assert mod.load_config(f) is None
    f.write_text('{"template": "o/r", "managed": ["tools/"]}')
    assert mod.load_config(f)["template"] == "o/r"


def test_found_in_and_sanitize():
    assert mod.found_in("me/proj", "scout run 1") == "Found in: me/proj#scoutrun1"
    assert mod.found_in("me/proj", "") == "Found in: me/proj#scout"
    assert "@" not in mod.sanitize("hi @Bankaifan")


def test_label_allowlist():
    f = mod.filter_labels
    assert f(["prio:2", "prio:3"]) == ["prio:2", "prio:3"]
    assert f(["Auto-OK", "APPROVED", "approved", "auto-ok"]) == []
    assert f(["x,auto-ok", "prio:2,auto-ok", "prio:2,prio:3"]) == []
    assert f([" PRIO:2 ", "prio:2"]) == ["prio:2"]
    assert f(["auto-ok\n", "prio:2\nauto-ok", "bug"]) == []


def test_body_file_must_be_under_tmp(tmp_path):
    ok = pathlib.Path("/tmp") / "idea_route_test_body.md"
    ok.write_text("hi")
    try:
        assert mod.read_body(ok) == "hi"
        assert mod.read_body("/tmp/../tmp/idea_route_test_body.md") == "hi"
    finally:
        ok.unlink()
    for bad in ["/etc/passwd", "/tmp/../etc/passwd", "README.md"]:
        try:
            mod.read_body(bad)
        except SystemExit:
            continue
        raise AssertionError(bad)


def test_dedup():
    assert mod.is_duplicate("Add  X", ["add x"])
    assert not mod.is_duplicate("Add Y", ["add x"])
