"""Actions watcher entry (design 0012, sections 4.1-4.2): one failed workflow run -> rerun once or one signed issue.

`actions_watch.py` handles the run in RUN_ID (a `workflow_run` event); without RUN_ID it sweeps the runs of the last
SWEEP_HOURS hours (schedule / workflow_dispatch, for events GitHub did not deliver). Everything is idempotent, so a
replaced pending run loses nothing. A startup failure, or a cancelled run whose job never started, is rerun once (only
while run_attempt is 1, no state); anything else opens or updates the signed `Failing workflow:` issue through
tools/failure_watch.py. Bodies are fixed script text. DRY_RUN=1 prints the actions and writes nothing.
FAILURE_WATCH=off skips it. Needs the gh CLI (GH_TOKEN, GH_REPO) and GUARD_KEY (script step only).
"""
import datetime
import os
import sys

import failure_watch as fw
import guard_mark
import liveness

SELF_WF = "watch.yml"  # the watcher never watches its own runs (no loop)
SWEEP_HOURS = 2
RERUN_CONCLUSIONS = ("startup_failure", "cancelled")
WRITES = ("create", "edit", "comment", "close", "reopen", "rerun")  # gh subcommands that change state


def readonly(run):
    """gh wrapper for DRY_RUN: any write subcommand is a bug, not a silent no-op."""
    def guarded(*args):
        if any(a in WRITES for a in args[:2]):
            raise RuntimeError(f"dry run must not write: gh {args[0]} {args[1]}")
        return run(*args)
    return guarded


def wants_rerun(run_obj, started):
    """Infrastructure-shaped ending, first attempt only: `gh run rerun` once, no state, no second rerun."""
    return (run_obj.get("conclusion") in RERUN_CONCLUSIONS and not started
            and int(run_obj.get("run_attempt") or 1) == 1)


def handle(r, key, dry=False, run=liveness.gh):
    """Act on one failed run R; returns a one-line action text."""
    if not fw.keep(r, SELF_WF):
        return f"run {r['id']}: not watched"
    sig, started = fw.analyse(r, run)
    if fw.expected_cancel(r, started, run):
        return f"run {r['id']}: expected cancellation"
    if wants_rerun(r, started):
        if not dry:
            run("run", "rerun", str(r["id"]))
        return f"run {r['id']}: {'would rerun' if dry else 'rerun'} once ({sig})"
    issues = fw.load_issues(key, run)
    title = fw.title_for(sig)
    issue = issues.get(title)
    if issue and fw.parse_body(issue["body"])["last_id"] >= r["id"]:
        return f"run {r['id']}: already counted in #{issue['number']}"
    if dry:
        return f"run {r['id']}: would {'update #' + str(issue['number']) if issue else 'open'} {title}"
    if issue is None:
        return f"run {r['id']}: opened failure issue #{fw._create(sig, r, key, run)['number']}"
    return f"run {r['id']}: {fw._recur(issue, sig, r, key, run)} failure issue #{issue['number']}"


def sweep(now, key, dry=False, run=liveness.gh):
    """Every kept failed run of the last SWEEP_HOURS hours, oldest first, at most MAX_NEW new issues."""
    since = now - datetime.timedelta(hours=SWEEP_HOURS)
    out, new = [], 0
    for r in fw.collect(since, now, run, SELF_WF):
        if new >= fw.MAX_NEW:
            out.append("sweep: flood cap reached, rest waits for the next tick")
            break
        line = handle(r, key, dry, run)
        new += "opened" in line or "would open" in line
        out.append(line)
    if not dry:
        out += [f"closed expected-cancel issue #{n}"
                for n in fw.close_expected(fw.load_issues(key, run), set(), key, run)]
    return out


def main(env=None, run=liveness.gh, now=None):
    env = os.environ if env is None else env
    if env.get("FAILURE_WATCH", "").strip().lower() == "off":
        return ["failure watch is off"]
    key = guard_mark.key_from_env()
    if not key:
        raise SystemExit("GUARD_KEY is not set: nothing can be signed")
    dry = env.get("DRY_RUN", "").strip().lower() in ("1", "true", "yes", "on")
    run = readonly(run) if dry else run
    run_id = (env.get("RUN_ID") or "").strip()
    if not run_id:
        return sweep(now or datetime.datetime.now(datetime.UTC), key, dry, run)
    if not run_id.isdigit():
        raise SystemExit("RUN_ID must be a number")
    r = fw._api(f"repos/{{owner}}/{{repo}}/actions/runs/{run_id}", run)
    return [handle(r, key, dry, run)]


if __name__ == "__main__":
    for line in main():
        print(line)
    sys.exit(0)
