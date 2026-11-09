import importlib.util
import pathlib

import pytest

_path = pathlib.Path(__file__).parent.parent / "tools" / "trusted_issues.py"
_spec = importlib.util.spec_from_file_location("trusted_issues", _path)
mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(mod)


def ev(kind, label, actor):
    return {"event": kind, "label": {"name": label}, "actor": {"login": actor}}


def issue(author, *labels):
    return {"number": 1, "title": "t", "author": {"login": author}, "labels": [{"name": n} for n in labels]}


def test_label_set_by_owner():
    assert mod.label_set_by([ev("labeled", "approved", "Bankaifan")], "approved", "Bankaifan")


def test_label_set_by_other_is_rejected():
    assert not mod.label_set_by([ev("labeled", "approved", "mallory")], "approved", "Bankaifan")


def test_latest_event_wins():
    events = [ev("labeled", "approved", "Bankaifan"), ev("unlabeled", "approved", "Bankaifan"),
              ev("labeled", "approved", "mallory")]
    assert not mod.label_set_by(events, "approved", "Bankaifan")


def test_other_label_events_ignored():
    assert not mod.label_set_by([ev("labeled", "idea", "Bankaifan")], "approved", "Bankaifan")


def test_owner_issue_is_trusted():
    r = mod.classify(issue("Bankaifan", "agent:dev"), [], "Bankaifan")
    assert r["authored_by_owner"] and r["labels"] == ["agent:dev"]


def test_stranger_issue_is_dropped():
    assert mod.classify(issue("mallory", "idea"), [], "Bankaifan") is None


def test_stranger_issue_forged_label_is_dropped():
    events = [ev("labeled", "approved", "mallory")]
    assert mod.classify(issue("mallory", "approved"), events, "Bankaifan") is None


def test_idea_approved_by_owner():
    events = [ev("labeled", "approved", "Bankaifan")]
    r = mod.classify(issue("author-app[bot]", "idea", "approved"), events, "Bankaifan")
    assert r["approved"] and not r["auto_ok"] and "approved" in r["labels"]


BOT = "author-app[bot]"
DESIGN = "Part 1 of 3.\n\nDesign: docs/design/0001-big-thing.md\n"


def derived(author=BOT, body=DESIGN, labels=("agent:dev",)):
    d = issue(author, *labels)
    d["body"] = body
    return d


def exists(path):
    return path == "docs/design/0001-big-thing.md"


def test_design_derived_issue_is_trusted():
    r = mod.classify(derived(), [], "Bankaifan", BOT, exists)
    assert r["design"] == "docs/design/0001-big-thing.md"
    assert not r["authored_by_owner"] and not r["approved"] and not r["auto_ok"]


def test_design_ref_from_stranger_is_dropped():
    assert mod.classify(derived(author="mallory"), [], "Bankaifan", BOT, exists) is None


def test_design_ref_without_configured_bot_is_dropped():
    assert mod.classify(derived(), [], "Bankaifan", "", exists) is None


def test_design_ref_to_missing_file_is_dropped():
    body = "Design: docs/design/0002-other.md\n"
    assert mod.classify(derived(body=body), [], "Bankaifan", BOT, exists) is None


def test_design_ref_must_be_its_own_line_in_docs_design():
    for body in ("see Design: docs/design/0001-big-thing.md", "Design: ../docs/design/0001-big-thing.md",
                 "Design: docs/design/0001-big-thing.md/../../x.md", "no ref"):
        assert mod.classify(derived(body=body), [], "Bankaifan", BOT, lambda p: True) is None


def test_bot_idea_with_design_line_is_not_trusted():
    assert mod.classify(derived(labels=("idea",)), [], "Bankaifan", BOT, exists) is None


def test_missing_body_is_dropped():
    d = derived()
    d["body"] = None
    assert mod.classify(d, [], "Bankaifan", BOT, exists) is None


@pytest.mark.parametrize("form", ["author-app", "app/author-app", "author-app[bot]"])
def test_design_issue_author_in_any_login_form(form):
    assert mod.classify(derived(author=form), [], "Bankaifan", BOT, exists)["design"]


@pytest.mark.parametrize("form", ["Bankaifan", "app/Bankaifan", "Bankaifan[bot]"])
def test_owner_in_any_login_form(form):
    assert mod.classify(issue(form), [], "Bankaifan")["authored_by_owner"]
    assert mod.label_set_by([ev("labeled", "approved", form)], "approved", "Bankaifan")


def test_auto_ok_only_counts_from_owner():
    scout = [ev("labeled", "auto-ok", "author-app[bot]")]
    assert mod.classify(issue("author-app[bot]", "idea", "auto-ok"), scout, "Bankaifan") is None
    owner = [ev("labeled", "auto-ok", "Bankaifan")]
    assert mod.classify(issue("author-app[bot]", "idea", "auto-ok"), owner, "Bankaifan")["auto_ok"]
