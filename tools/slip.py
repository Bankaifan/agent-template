"""Slip detection for the dispatcher (design 0015, step 1): does an issue already carry a task slip, and which model?

A slip is a `Files:` line (`overlap.parse_files`) in the body of an issue written by a trusted author (the owner or
the author app) or in a comment by one of them. A body by a stranger never counts, even when the owner labelled the
issue `approved`: such an issue has no slip and goes to the model. Text is untrusted: only paths and the model word
are parsed, nothing is opened or run.
"""
import re

import overlap

_MODEL = re.compile(r"^[\s>*_-]*Model\**\s*:\**\s*(sonnet|haiku)\b", re.IGNORECASE | re.MULTILINE)


def slip_texts(issue, authors):
    """Texts of ISSUE (a `gh issue view --json body,author,comments` dict) that may hold a slip, trusted authors only."""
    texts = [issue.get("body") or ""] if overlap.trusted(issue, authors) else []
    return texts + [c.get("body") or "" for c in issue.get("comments", []) if overlap.trusted(c, authors)]


def slip_files(issue, authors):
    """Paths of the slip of ISSUE, [] when it has none."""
    paths = []
    for t in slip_texts(issue, authors):
        paths += [p for p in overlap.parse_files(t) if p not in paths]
    return paths


def has_slip(issue, authors=overlap.DEFAULT_TRUSTED):
    return bool(slip_files(issue, authors))


def model_of(issue, authors=overlap.DEFAULT_TRUSTED):
    """`sonnet` or `haiku`: the last `Model:` line of a trusted text, else an existing `model:` label, else `haiku`.
    `opus` is never set by script (it needs the owner's OK)."""
    found = [m.lower() for t in slip_texts(issue, authors) for m in _MODEL.findall(t)]
    if found:
        return found[-1]
    labels = {lab["name"] for lab in issue.get("labels", [])}
    return "sonnet" if "model:sonnet" in labels else "haiku"
