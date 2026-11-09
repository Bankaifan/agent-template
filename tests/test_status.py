import datetime
import importlib.util
import json
import pathlib
import subprocess

_path = pathlib.Path(__file__).parent.parent / "tools" / "status.py"
_spec = importlib.util.spec_from_file_location("status", _path)
st = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(st)

NOW = datetime.datetime(2026, 11, 9, 12, 0, tzinfo=datetime.UTC)
UTC = datetime.UTC


def ago(minutes):
    return (NOW - datetime.timedelta(minutes=minutes)).isoformat()


def at(h, m):
    return datetime.datetime(2026, 1, 1, h, m, tzinfo=UTC)


def pr(number=1, branch="agent/1-x", labels=(), **kw):
    base = {"number": number, "title": "T", "url": f"u/{number}", "headRefName": branch, "headRefOid": f"sha{number}",
            "labels": [{"name": n} for n in labels], "reviewRequests": [], "statusCheckRollup": [],
            "author": {"login": "app/author"}, "createdAt": ago(60), "mergeStateStatus": "CLEAN",
            "isCrossRepository": False, "commits": [{"committedDate": ago(60)}]}
    base.update(kw)
    return base


def issue(number=1, labels=("agent:dev",), title="Do it"):
    return {"number": number, "title": title, "labels": [{"name": n} for n in labels], "createdAt": ago(500)}


class Recorder:
    def __init__(self):
        self.calls = []

    def __call__(self, *args):
        self.calls.append(args)
        return json.dumps({"author": {"login": "app/author"}})


def test_interval_defaults_and_rounding():
    assert st.interval_minutes("", False) == 30
    assert st.interval_minutes("", True) == 60
    assert st.interval_minutes("45", False) == 60
    assert st.interval_minutes("junk", True) == 60


def test_should_run_gate():
    assert st.should_run("workflow_dispatch", True, "", at(10, 37))
    assert st.should_run("workflow_run", True, "", at(10, 37))
    assert st.should_run("schedule", False, "", at(10, 37))
    assert st.should_run("schedule", True, "", at(10, 7))
    assert not st.should_run("schedule", True, "", at(10, 37))


def test_ci_state():
    assert st.ci_state([]) == "none"
    assert st.ci_state([{"conclusion": "SUCCESS"}]) == "green"
    assert st.ci_state([{"conclusion": "SUCCESS"}, {"conclusion": "FAILURE"}]) == "red"
    assert st.ci_state([{"status": "IN_PROGRESS", "conclusion": ""}]) == "running"


def test_waits_for_daniel():
    assert st.waits_for(pr(labels=["needs-human"]), "Bankaifan") == "needs-human"
    assert st.waits_for(pr(reviewRequests=[{"login": "Bankaifan"}]), "Bankaifan") == "waiting for Daniel"
    ready = pr(reviewDecision="REVIEW_REQUIRED", statusCheckRollup=[{"conclusion": "SUCCESS"}])
    assert st.waits_for(ready, "Bankaifan") == "waiting for code owner review"


def test_orphan_issue_needs_age_no_job_no_pr():
    def old(i):
        return ago(31)

    def young(i):
        return ago(5)

    i = issue(7)
    assert st.orphan_issues([i], [], [], old, NOW) == [i]
    assert st.orphan_issues([i], [], [], young, NOW) == []
    assert st.orphan_issues([i], [pr(branch="agent/7-x")], [], old, NOW) == []
    job = {"workflowName": "agent-dev", "displayTitle": "Do it"}
    assert st.orphan_issues([i], [], [job], old, NOW) == []
    assert st.orphan_issues([issue(7, ("agent:dev", "needs-human"))], [], [], old, NOW) == []


def test_orphan_pr_needs_age_and_no_validate_run():
    p = pr(commits=[{"committedDate": ago(11)}])
    assert st.orphan_prs([p], lambda sha: 0, NOW) == [p]
    assert st.orphan_prs([p], lambda sha: 1, NOW) == []
    assert st.orphan_prs([pr(commits=[{"committedDate": ago(5)}])], lambda sha: 0, NOW) == []
    assert st.orphan_prs([pr(branch="dependabot/x", commits=[{"committedDate": ago(30)}])], lambda s: 0, NOW) == []
    assert st.orphan_prs([pr(mergeStateStatus="DIRTY", commits=[{"committedDate": ago(30)}])], lambda s: 0, NOW) == []


def test_handle_orphan_first_retriggers_second_escalates():
    run = Recorder()
    assert st.handle_orphan("pr", pr(7, "agent/7-x"), "Bankaifan", run) == "retriggered"
    assert ("workflow", "run", "validate.yml", "--ref", "agent/7-x") in run.calls
    run = Recorder()
    assert st.handle_orphan("pr", pr(7, labels=[st.RETRIGGER]), "Bankaifan", run) == "escalated"
    assert ("pr", "edit", "7", "--add-reviewer", "Bankaifan") in run.calls
    assert any(c[:3] == ("pr", "comment", "7") for c in run.calls)
    assert any("needs-human" in c for c in run.calls)


def test_handle_orphan_issue_readds_label():
    run = Recorder()
    assert st.handle_orphan("issue", issue(4), "Bankaifan", run) == "retriggered"
    assert ("issue", "edit", "4", "--remove-label", "agent:dev") in run.calls
    assert ("issue", "edit", "4", "--add-label", "agent:dev") in run.calls


def test_held_runs_only_author_app_head():
    prs = [pr(1, "agent/1-x"), pr(2, "agent/2-x", author={"login": "someone"}),
           pr(3, "agent/3-x", isCrossRepository=True)]
    held = [{"databaseId": 10, "headSha": "sha1"}, {"databaseId": 11, "headSha": "sha2"},
            {"databaseId": 12, "headSha": "sha3"}, {"databaseId": 13, "headSha": "other"}]
    assert st.held_run_ids(held, prs, "author[bot]") == [10]


def test_fix_round_mirrors_agent_fix():
    assert st.fix_round(set()) == ("review:1", False)
    assert st.fix_round({"review:1"}) == ("review:2", False)
    assert st.fix_round({"review:2"}) == ("review:3", True)
    assert st.fix_round({"review:3"}) == (None, True)


def test_conflict_dispatches_fix_then_escalates():
    run = Recorder()
    assert st.handle_conflict(pr(9, mergeStateStatus="DIRTY"), "Bankaifan", run) == "fix dispatched"
    assert ("workflow", "run", "agent-fix.yml", "-f", "pr=9") in run.calls
    assert ("pr", "edit", "9", "--add-label", "review:1") in run.calls
    run = Recorder()
    assert st.handle_conflict(pr(9, labels=["review:2"]), "Bankaifan", run) == "escalated"
    assert not any(c[:2] == ("workflow", "run") for c in run.calls)


def test_conflict_prs_skip_needs_human_and_clean():
    dirty = pr(1, mergeStateStatus="DIRTY")
    assert st.conflict_prs([dirty, pr(2), pr(3, mergeStateStatus="DIRTY", labels=["needs-human"])]) == [dirty]


def test_build_body_sections():
    job = {"workflowName": "agent-dev", "url": "r", "displayTitle": "Do it", "status": "in_progress",
           "createdAt": ago(5)}
    body = st.build_body([job], [pr(5, mergeStateStatus="DIRTY")], [issue(7)], {7: "40 min"}, None, [], [], NOW,
                         "Bankaifan")
    assert "[agent-dev](r)" in body
    assert "merge conflict" in body
    assert "- #7 Do it (agent:dev for 40 min)" in body
    assert "no run yet" in body
    assert body.count("- none") == 2


def test_update_issue_creates_or_edits():
    calls = []
    found = []

    def run(*args):
        calls.append(args)
        if args[:2] == ("issue", "list"):
            return json.dumps(found)
        return "https://github.com/o/r/issues/12\n"

    assert st.update_issue("b", run) == "12"
    assert calls[1][:2] == ("issue", "create")
    found.append({"number": 3, "title": st.TITLE})
    assert st.update_issue("b", run) == "3"
    assert ("issue", "edit", "3", "--body", "b") in calls
    assert ("issue", "pin", "3") in calls


def test_gate_writes_output(tmp_path):
    out = tmp_path / "o"
    st.gate({"EVENT": "schedule", "PRIVATE": "true", "GITHUB_OUTPUT": str(out)}, at(10, 37))
    assert out.read_text() == "run=false\n"


def test_gh_prints_stderr_before_raising(monkeypatch, capsys):
    def fake_run(cmd, **kw):
        raise subprocess.CalledProcessError(1, cmd, output="", stderr='Unknown JSON field: "bogus"\n')

    monkeypatch.setattr(st.subprocess, "run", fake_run)
    try:
        st.gh("pr", "list", "--json", "bogus")
    except subprocess.CalledProcessError:
        pass
    else:
        raise AssertionError("expected CalledProcessError")
    err = capsys.readouterr().err
    assert "gh pr list exited 1" in err and "Unknown JSON field" in err


def _main_runs(*items):
    return [{"conclusion": c, "createdAt": ago(m)} for c, m in items]  # newest first


def _agent_pr(**kw):
    c = [{"authors": [{"login": "Bankaifan"}], "committedDate": ago(60)}]
    return pr(7, "agent/7-x", mergeStateStatus="BEHIND", commits=c, **kw)


def _failed(sha):
    return [{"conclusion": "failure", "createdAt": ago(50)}]


def test_pr_limit_keeps_graphql_query_small():
    assert st.PR_LIMIT <= 20


def test_pr_red_on_old_red_main_is_rebased():
    main = _main_runs(("success", 10), ("failure", 90))
    assert st.rebase_candidates([_agent_pr()], main, _failed, "Bankaifan") != []


def test_pr_red_on_green_main_is_left_alone():
    main = _main_runs(("success", 10), ("success", 90))
    assert st.rebase_candidates([_agent_pr()], main, _failed, "Bankaifan") == []


def test_no_rebase_while_main_is_red_or_for_foreign_prs():
    assert st.rebase_candidates([_agent_pr()], _main_runs(("failure", 10)), _failed, "Bankaifan") == []
    main = _main_runs(("success", 10), ("failure", 90))
    assert st.rebase_candidates([_agent_pr(isCrossRepository=True)], main, _failed, "Bankaifan") == []
    dependabot = pr(8, "dependabot/x", mergeStateStatus="BEHIND")
    assert st.rebase_candidates([dependabot], main, _failed, "Bankaifan") == []
    two = _agent_pr()
    two["commits"] = two["commits"] * 2
    assert st.rebase_candidates([two], main, _failed, "Bankaifan") == []
