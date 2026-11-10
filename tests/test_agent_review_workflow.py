"""Guards for agent-review.yml: the script re-approval sits before the model and runs from the default branch."""

from pathlib import Path

WORKFLOW = Path(__file__).resolve().parent.parent / ".github" / "workflows" / "agent-review.yml"


def _text() -> str:
    return WORKFLOW.read_text(encoding="utf-8")


def test_reapprove_step_is_before_the_model_step():
    text = _text()
    assert text.index("id: reapprove") < text.index("id: claude")
    assert text.index("id: round") < text.index("id: reapprove")
    assert "python3 tools/reapprove.py" in text


def test_model_step_is_skipped_after_a_script_approval():
    assert "steps.reapprove.outputs.done != 'true'" in _text()


def test_checkout_is_the_default_branch_and_trigger_is_workflow_run():
    text = _text()
    assert "ref: ${{ github.event.repository.default_branch }}" in text
    assert "workflow_run:" in text
    assert "pull_request" not in text.split("permissions:")[0]


def test_no_step_uses_pull_request_events_for_approval():
    text = _text()
    assert "pull_request_target" not in text
    assert "on:\n  pull_request" not in text
