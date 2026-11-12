import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent.parent.parent / "tools"))

import slip

BOT = {"login": "bankaifan-agent-author"}
OWNER = {"login": "Bankaifan"}
STRANGER = {"login": "mallory"}


def issue(body="", author=BOT, comments=(), labels=()):
    return {"body": body, "author": author, "comments": list(comments), "labels": [{"name": n} for n in labels]}


def test_slip_in_body_of_author_app_issue():
    assert slip.has_slip(issue("Files: tools/a.py, tests/test_a.py"))


def test_stranger_body_is_no_slip_even_when_approved():
    i = issue("Files: tools/a.py", author=STRANGER, labels=["approved"])
    assert not slip.has_slip(i)


def test_slip_in_trusted_comment_counts_stranger_comment_does_not():
    assert slip.has_slip(issue("idea", author=OWNER, comments=[{"author": BOT, "body": "Files: tools/a.py"}]))
    assert not slip.has_slip(issue("idea", author=OWNER, comments=[{"author": STRANGER, "body": "Files: tools/a.py"}]))


def test_model_line_label_and_default():
    assert slip.model_of(issue("Files: a.py\nModel: sonnet")) == "sonnet"
    assert slip.model_of(issue("Files: a.py\nModel: haiku", labels=["model:sonnet"])) == "haiku"
    assert slip.model_of(issue("Files: a.py", labels=["model:sonnet"])) == "sonnet"
    assert slip.model_of(issue("Files: a.py")) == "haiku"


def test_opus_is_never_chosen_and_stranger_model_ignored():
    assert slip.model_of(issue("Files: a.py\nModel: opus")) == "haiku"
    assert slip.model_of(issue("Model: sonnet", author=STRANGER)) == "haiku"
