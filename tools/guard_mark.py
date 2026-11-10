"""Marker that the guard scripts (no model) write into the issues they create, so trusted_issues.py can trust them.

Only scripts import `mark`. Model-written text must never carry a marker: `has_mark` is used to reject it.
"""
import re

KINDS = ("liveness", "orchestrator", "unblocker")
_MARK = re.compile(r"<!--\s*guard:\s*[a-z-]+\s*-->", re.IGNORECASE)
_LINE = re.compile(r"^<!-- guard: (" + "|".join(KINDS) + r") -->\s*$", re.MULTILINE)


def mark(kind):
    """The marker line for a guard kind."""
    if kind not in KINDS:
        raise ValueError(f"unknown guard kind {kind!r}")
    return f"<!-- guard: {kind} -->"


def has_mark(text):
    """True if `text` holds anything that looks like a guard marker (any spacing or case)."""
    return bool(_MARK.search(text or ""))


def marked_line(body):
    """True if the body has a valid marker on a line of its own."""
    return bool(_LINE.search(body or ""))
