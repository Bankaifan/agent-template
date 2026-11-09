import importlib.util
import json
import pathlib

spec = importlib.util.spec_from_file_location(
    "post_verdict", pathlib.Path(__file__).resolve().parents[1] / "tools" / "ci" / "post_verdict.py")
pv = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pv)

SHA = "b9f7de0afcbe86090adf5f4673bbe3826bbb06ee"


def exec_file(result, denials=()):
    return json.dumps([{"type": "assistant", "message": {"content": [{"type": "text", "text": "thinking"}]}},
                       {"type": "result", "result": result, "permission_denials": list(denials)}])


def test_changes_posts_comment_and_requests_changes(tmp_path):
    calls = []
    text = f"Looked at it.\n\nsecurity-review: changes {SHA[:7]}\n\n- a.yml:3: Write is unscoped"
    assert pv.post(5, SHA, exec_file(text), lambda *a: calls.append(a), tmp_path) == 0
    assert calls[0][:3] == ("pr", "comment", "5")
    body = pathlib.Path(calls[0][4]).read_text()
    assert body.startswith(f"security-review: changes {SHA}\n\n- a.yml:3")
    assert calls[1][:3] == ("pr", "review", "5") and "--request-changes" in calls[1]


def test_approve_posts_only_the_comment(tmp_path):
    calls = []
    assert pv.post(5, SHA, exec_file(f"`security-review: approve {SHA}`\n- fine"), lambda *a: calls.append(a),
                   tmp_path) == 0
    assert len(calls) == 1


def test_no_verdict_or_other_sha_logs_denials(tmp_path, capsys):
    calls = []
    denied = [{"tool_name": "Bash", "tool_input": {"command": "gh pr comment 5 --body x"}}]
    assert pv.post(5, SHA, exec_file("security-review: approve 1234567", denied), lambda *a: calls.append(a),
                   tmp_path) == 1
    assert calls == []
    assert "denied: Bash: gh pr comment 5 --body x" in capsys.readouterr().out
