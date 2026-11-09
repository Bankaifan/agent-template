"""Guards for the unblocker workflow (design 0002, section 6): trigger, permissions, model tools, checkout."""

import re
from pathlib import Path

WORKFLOWS = Path(__file__).resolve().parent.parent / ".github" / "workflows"


def _text(name="unblocker.yml") -> str:
    return (WORKFLOWS / name).read_text(encoding="utf-8")


def _step(name: str) -> str:
    """The text of one step (from its `- name:`/`- id:` line to the next step at the same indent)."""
    text = _text()
    start = text.index(name)
    start = text.rfind("\n      - ", 0, start) + 1
    end = text.find("\n      - ", start + 10)
    return text[start : end if end != -1 else len(text)]


def test_job_if_names_only_needs_human():
    text = _text()
    ifs = re.search(r"\n    if: >-\n(.*?)\n    concurrency:", text, re.DOTALL).group(1)
    assert "github.event.label.name == 'needs-human'" in ifs
    assert re.findall(r"label\.name\s*==\s*'([^']*)'", ifs) == ["needs-human"]
    assert "(vars.UNBLOCKER || 'on') != 'off'" in ifs


def test_triggers_are_labeled_events_of_issues_and_prs_only():
    head = _text().split("\npermissions:")[0]
    assert "  issues:\n    types: [labeled]" in head
    assert "  pull_request:\n    types: [labeled]" in head
    assert "pull_request_target" not in head and "workflow_run" not in head and "issue_comment" not in head


def test_workflow_permissions_are_contents_read_only():
    text = _text()
    assert "\npermissions:\n  contents: read\njobs:" in text
    assert "permissions:" not in text.split("jobs:", 1)[1]


def test_runs_are_serialised_per_item_without_cancelling():
    text = _text()
    assert "group: unblocker-${{ github.event.issue.number || github.event.pull_request.number }}" in text
    assert "cancel-in-progress: false" in text


def test_checkout_is_main_without_persisted_credentials():
    step = _step("actions/checkout@")
    assert "persist-credentials: false" in step
    assert "ref: ${{ github.event.repository.default_branch }}" in step
    assert "token:" not in step


def test_model_step_has_no_edit_write_or_write_capable_bash():
    step = _step("id: claude")
    tools = re.search(r'--allowedTools "([^"]*)"', step).group(1).split(",")
    assert tools == ["Read", "Glob", "Grep", "Bash(gh issue view:*)", "Bash(gh pr view:*)", "Bash(gh run view:*)"]
    assert "--model sonnet" in step


def test_secret_reaches_only_the_gated_model_step():
    text = _text()
    assert text.count("secrets.CLAUDE_CODE_OAUTH_TOKEN") == 1
    assert "if: steps.gate.outputs.run == 'true'" in _step("id: claude")
    assert "steps.claude.outcome == 'success'" in _step("name: Apply the verdict")


def test_model_step_gets_only_the_read_only_token():
    step = _step("id: claude")
    assert "steps.app.outputs" not in step
    assert step.count("steps.app_ro.outputs.token") == 2
    ro = _step("id: app_ro")
    assert "permission-issues: read" in ro and "permission-pull-requests: read" in ro and "permission-actions: read" in ro
    assert "write" not in ro


def test_class_2_issue_with_token_shaped_text_becomes_class_3():
    import sys

    sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
    import unblock

    v = {"class": 2, "reason": "x", "issue": {"title": "Fix the thing", "body": "Details ghs_" + "A1b2C3d4E5f6G7h8"}}
    assert unblock.validate(v)["class"] == 3


def test_no_untrusted_text_in_run_blocks():
    """Every ${{ }} inside a run: block would be script injection; they must go through env."""
    lines = _text().splitlines()
    in_run = False
    indent = 0
    for line in lines:
        stripped = line.strip()
        if in_run and stripped and len(line) - len(line.lstrip()) <= indent:
            in_run = False
        if in_run:
            assert "${{" not in line, line
        if stripped.startswith("run: |"):
            in_run, indent = True, len(line) - len(line.lstrip())
    assert "github.event.comment" not in _text() and "github.event.issue.title" not in _text()
    assert "github.event.issue.body" not in _text() and "head_ref" not in _text()


def test_failed_run_escalates_and_apply_reads_the_verdict_as_data():
    text = _text()
    assert "if: ${{ failure() && steps.app.outcome == 'success' }}" in text
    assert "agent_guard.escalate(" in text
    assert 'tools/unblock.py apply "$KIND" "$NUMBER" "$VERDICT"' in text


def test_setup_creates_label_and_lists_variable():
    setup = _text("setup.yml")
    assert "needs-human unblock:1 " in setup
    assert 'row UNBLOCKER on "$UNBLOCKER"' in setup


def test_orchestrator_step_2_skips_items_the_unblocker_owns():
    text = _text("orchestrator.yml")
    assert "`unblock:1`" in text and "<!-- unblocker -->" in text
    assert "the unblocker" in text.split("2. For each other PR labeled needs-human", 1)[1].split("3. If HANDOVER", 1)[0]
