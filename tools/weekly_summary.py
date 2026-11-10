"""Create or update the issue "Weekly summary" without a model.

Sections: merged PRs of the last 7 days, PRs labelled needs-human, rule-keeper PRs,
ideas without `approved`, failure watch (open, closed and reopened failure issues, design 0008).
Also appends one row per week to docs/metrics.csv (the workflow opens a PR for it). Needs the gh CLI
(GH_TOKEN, GH_REPO).
"""
import csv
import datetime
import json
import os
import pathlib
import statistics
import subprocess
import sys

import failure_watch
import friction
import guard_mark
import liveness
import run_stats

TITLE = "Weekly summary"
PROPOSAL_TITLE = "Capacity proposal"
QUEUE_WAIT = 3  # approved issues waiting while no agent:dev slot is free: threshold for the proposal (design 0014)
METRICS = pathlib.Path("docs/metrics.csv")
COLUMNS = ["week", "code_lines", "modules", "lines_by_lang", "modules_by_lang", "max_parallel_agent_prs",
           "conflicts_rebuilt", "avg_review_rounds", "median_ci_minutes", "actions_minutes"]
LANGS = {".py": "python", ".sh": "shell", ".js": "javascript", ".ts": "typescript", ".go": "go",
         ".rs": "rust", ".java": "java", ".rb": "ruby", ".c": "c", ".h": "c", ".cpp": "cpp"}
GENERATED = ("package-lock.json", "yarn.lock", "poetry.lock", "uv.lock", "Cargo.lock", "go.sum")
GENERATED_DIRS = ("dist/", "build/", "vendor/", "node_modules/", "generated/")


def section(heading, rows):
    lines = [f"## {heading}"]
    lines += [f"- #{r['number']} {r['title']}" for r in rows] or ["- none"]
    return "\n".join(lines)


def failure_section(watch):
    """Open, closed this week and reopened this week; None (gh could not read them) prints unknown."""
    if watch is None:
        return "## Failure watch\n- unknown"
    parts = ["## Failure watch"]
    # "reopened" = Reopened counter >= 1 and updated this week: an approximation (design 0008 4.7), not the reopen date
    for key, label in (("open", "open"), ("closed", "closed this week"),
                       ("reopened", "reopened at least once, updated this week")):
        parts.append(f"- {label}: {len(watch[key])}")
        parts += [f"  - #{r['number']} {r['title']}" for r in watch[key]]
    return "\n".join(parts)


def build_body(merged, needs_human, rule_keeper, ideas, today, status_stale=False, failures=None, capacity=None):
    parts = [f"Updated {today}.", section("Merged in the last 7 days", merged),
             section("PRs labelled needs-human", needs_human),
             section("Rule-keeper PRs", rule_keeper),
             section("Ideas waiting for approval", ideas),
             failure_section(failures)]
    if capacity:
        parts += list(capacity)
    if status_stale:
        parts.append("## Warning\n- The status run has no successful run in the last 3 hours.")
    return "\n\n".join(parts) + "\n"


def is_generated(path):
    name = path.rsplit("/", 1)[-1]
    return name in GENERATED or ".min." in name or any(path.startswith(d) or "/" + d in path for d in GENERATED_DIRS)


def count_code(files, read_lines):
    """Lines and modules (= source files) per language; generated files are skipped."""
    lines, modules = {}, {}
    for path in files:
        lang = LANGS.get(pathlib.PurePosixPath(path).suffix)
        if not lang or is_generated(path):
            continue
        lines[lang] = lines.get(lang, 0) + read_lines(path)
        modules[lang] = modules.get(lang, 0) + 1
    return lines, modules


def max_parallel(prs, week_start, week_end):
    """Max number of agent PRs open at the same time inside [week_start, week_end] (ISO strings)."""
    events = []
    for p in prs:
        if not p["headRefName"].startswith("agent/"):
            continue
        start, end = max(p["createdAt"], week_start), min(p.get("closedAt") or week_end, week_end)
        if start <= end:
            events += [(start, 1), (end, -1)]
    best = cur = 0
    for _, delta in sorted(events):  # closes (-1) sort before opens (+1) at the same time
        cur += delta
        best = max(best, cur)
    return best


def avg_review_rounds(merged):
    """Average of 1 + CHANGES_REQUESTED reviews over merged agent PRs; None without any."""
    rounds = [1 + sum(r["state"] == "CHANGES_REQUESTED" for r in p.get("reviews", []))
              for p in merged if p["headRefName"].startswith("agent/")]
    return round(sum(rounds) / len(rounds), 2) if rounds else None


def _ts(value):
    return datetime.datetime.fromisoformat(value)


def median_ci_minutes(runs):
    """Median duration in minutes of finished runs (startedAt/updatedAt ISO strings); None without runs."""
    secs = [(_ts(r["updatedAt"]) - _ts(r["startedAt"])).total_seconds()
            for r in runs if r.get("startedAt") and r.get("updatedAt") and r.get("conclusion")]
    return round(statistics.median(secs) / 60, 1) if secs else None


def fmt(by_lang):
    return ";".join(f"{k}={v}" for k, v in sorted(by_lang.items()))


def metrics_row(week, lines, modules, parallel, rounds, ci, actions):
    """One CSV row; unknown values stay empty. conflicts_rebuilt has no cheap source yet and stays empty."""
    def blank(v):
        return "" if v is None else v
    return {"week": week, "code_lines": sum(lines.values()), "modules": sum(modules.values()),
            "lines_by_lang": fmt(lines), "modules_by_lang": fmt(modules), "max_parallel_agent_prs": parallel,
            "conflicts_rebuilt": "", "avg_review_rounds": blank(rounds), "median_ci_minutes": blank(ci),
            "actions_minutes": blank(actions)}


def append_metrics(path, row):
    """Append the row unless the week is already in the file (re-runs are idempotent)."""
    path = pathlib.Path(path)
    if path.exists():
        with path.open(newline="") as f:
            if any(r["week"] == row["week"] for r in csv.DictReader(f)):
                return False
    new = not path.exists() or path.stat().st_size == 0
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", newline="") as f:
        w = csv.DictWriter(f, COLUMNS, lineterminator="\n")
        if new:
            w.writeheader()
        w.writerow(row)
    return True


def read_lines(path):
    try:
        with open(path, "rb") as f:
            return sum(1 for line in f if line.strip())
    except OSError:
        return 0


def gh(*args):
    return subprocess.run(["gh", *args], check=True, capture_output=True, text=True).stdout


def actions_minutes():
    """Actions minutes used this month if the API gives them (user billing endpoint), else None."""
    owner = os.environ.get("GH_REPO", "").split("/")[0]
    try:
        return json.loads(gh("api", f"users/{owner}/settings/billing/actions")).get("total_minutes_used")
    except (subprocess.CalledProcessError, ValueError, OSError, AttributeError):
        return None


def collect_metrics(today):
    week_end = today.isoformat() + "T23:59:59Z"
    week_start = (today - datetime.timedelta(days=7)).isoformat() + "T00:00:00Z"
    files = subprocess.run(["git", "ls-files"], check=True, capture_output=True, text=True).stdout.splitlines()
    lines, modules = count_code(files, read_lines)
    prs = json.loads(gh("pr", "list", "--state", "all", "--limit", "200",
                        "--json", "headRefName,createdAt,closedAt,mergedAt,reviews"))
    merged = [p for p in prs if p.get("mergedAt") and p["mergedAt"] >= week_start]
    runs = json.loads(gh("run", "list", "--workflow", "validate.yml", "--limit", "100",
                         "--created", ">=" + week_start[:10], "--json", "startedAt,updatedAt,conclusion"))
    return metrics_row(today.isoformat(), lines, modules, max_parallel(prs, week_start, week_end),
                       avg_review_rounds(merged), median_ci_minutes(runs), actions_minutes())


def status_stale_safe(run=gh):
    """The status-run warning; if gh cannot list the runs, skip the warning instead of aborting the summary."""
    try:
        return liveness.status_run_stale(run)
    except (subprocess.CalledProcessError, ValueError, OSError):
        return False


def failure_watch_summary(run, today, key):
    """Signed failure issues (failure_watch.load_issues): open, closed in the last 7 days, reopened (see failure_section).
    None without GUARD_KEY (nothing verifies), or if gh cannot list them or the output is not as expected."""
    if not key:
        return None
    week_start = (today - datetime.timedelta(days=7)).isoformat() + "T00:00:00Z"
    try:
        failing = list(failure_watch.load_issues(key, run).values())
        reopened = [i for i in failing if failure_watch.parse_body(i["body"])["reopened"] >= 1
                    and i["updatedAt"] >= week_start]
        return {"open": [i for i in failing if i["state"] == "OPEN"],
                "closed": [i for i in failing if i["state"] == "CLOSED" and (i["closedAt"] or "") >= week_start],
                "reopened": reopened}
    except (subprocess.CalledProcessError, ValueError, OSError, KeyError, TypeError):
        return None


def friction_issues(run=gh):
    """Create one issue per friction item seen in 2+ merged agent PRs; the summary must not fail because of it."""
    try:
        return friction.create_issues(friction.collect(), run)
    except (subprocess.CalledProcessError, ValueError, OSError, KeyError, TypeError):
        return []


def env_int(name, default):
    try:
        return int(os.environ.get(name) or default)
    except ValueError:
        return default


def model_section(results):
    """results: {workflow file: run_stats.workflow_stats() or None (unknown)}."""
    lines = ["## Model runs, last 7 days"]
    done = {f: r for f, r in results.items() if r}
    for f, r in results.items():
        role = run_stats.ROLES.get(f, f)
        if r is None:
            lines.append(f"- {f} ({role}): unknown")
            continue
        median = "n/a" if r["median_min"] is None else f"{r['median_min']} min"
        lines.append(f"- {f} ({role}): {r['model_runs']} runs, {r['model_runs'] / r['days']:.2f} per day, "
                     f"median {median}, failed {r['failed']}, limit or rate errors {r['limit_failed']}")
    if done:
        top = max(done, key=lambda f: done[f]["model_runs"])
        lines.append(f"- most model runs: {run_stats.ROLES.get(top, top)} ({done[top]['model_runs']})")
    lines.append("- turns and denied calls: open (the execution file stays on the runner; not measured here)")
    return "\n".join(lines)


def queue_numbers(issues, prs, max_dev, max_prs, now):
    """Approved issues waiting for a slot, free agent:dev and agent PR slots (an approximation of prefilter.py),
    and the median days since the last update of needs-human items (label times are not read: open)."""
    def names(item):
        return {lab["name"] for lab in item.get("labels", [])}
    dev = [i for i in issues if "agent:dev" in names(i)]
    waiting = [i for i in issues if "approved" in names(i) and "agent:dev" not in names(i)]
    agent_prs = [p for p in prs if p["headRefName"].startswith("agent/") and "needs-human" not in names(p)]
    human = [x for x in issues + prs if "needs-human" in names(x)]
    ages = [(now - datetime.datetime.fromisoformat(x["updatedAt"])).days for x in human]
    return {"waiting": len(waiting), "free_dev": max(0, max_dev - len(dev)),
            "free_prs": max(0, max_prs - len(agent_prs)), "max_dev": max_dev, "max_prs": max_prs,
            "needs_human": len(human), "human_median_days": statistics.median(ages) if ages else None}


def queue_section(q):
    median = "n/a" if q["human_median_days"] is None else f"{q['human_median_days']} days"
    return "\n".join([
        "## Queue",
        f"- approved issues waiting for a slot: {q['waiting']}",
        f"- free slots: agent:dev {q['free_dev']} of {q['max_dev']}, agent PRs {q['free_prs']} of {q['max_prs']}",
        f"- needs-human items: {q['needs_human']}, median days since last update: {median} (approximation)"])


def capacity_sections(today, run=gh, max_dev=2, max_prs=3, now=None):
    """(model section, queue section, threshold reasons). gh failures give 'unknown' sections, never an abort."""
    now = now or datetime.datetime.now(datetime.UTC)
    since = (today - datetime.timedelta(days=7)).isoformat()
    try:
        files = run_stats.claude_workflows()
        runs, jobs_of, log_of = run_stats.fetch_all(files, since, run=run)
        results = {f: run_stats.workflow_stats(runs[f], jobs_of, log_of, now=now) for f in files}
        issues = json.loads(run("issue", "list", "--state", "open", "--limit", "200",
                                "--json", "number,title,labels,updatedAt"))
        prs = json.loads(run("pr", "list", "--state", "open", "--limit", "100",
                             "--json", "number,title,headRefName,labels,updatedAt"))
        queue = queue_numbers(issues, prs, max_dev, max_prs, now)
    except (subprocess.CalledProcessError, ValueError, OSError, KeyError, TypeError):
        return "## Model runs, last 7 days\n- unknown", "## Queue\n- unknown", []
    reasons = []
    limit_errors = sum(r["limit_failed"] for r in results.values())
    if limit_errors:
        reasons.append(f"{limit_errors} failed model run(s) with a limit or rate error (last 7 days)")
    if queue["waiting"] >= QUEUE_WAIT and queue["free_dev"] == 0:
        reasons.append(f"{queue['waiting']} approved issues wait while no agent:dev slot is free")
    return model_section(results), queue_section(queue), reasons


def proposal_body(reasons, model, queue_text, today):
    """Text of the Capacity proposal. It names the levers and the numbers; Daniel decides, the script does not."""
    levers = [
        "- `IDEAS_PER_WEEK`: scout cap per run (default 3, 0 = off)",
        "- `ORCHESTRATOR_EVENTS`: on or off for non-label events",
        "- `MAX_DEV` / `MAX_PRS`: agent jobs at once and open agent PRs (current values in Queue above; defaults 2 and 3, agent-template 4 and 5)",
        "- model per role: haiku by default, sonnet for core and security, opus only with Daniel's OK",
        "- a separate seat or token for selected roles: open, not measured here",
    ]
    parts = [f"Updated {today}. Written by the weekly summary (design 0014). No variable and no secret is changed.",
             "## Why\n" + "\n".join(f"- {r}" for r in reasons), model, queue_text,
             "## Levers (Daniel decides)\n" + "\n".join(levers)]
    return "\n\n".join(parts) + "\n"


def upsert_proposal(body, run=gh):
    """One open issue titled PROPOSAL_TITLE: updated if it exists, created otherwise."""
    found = json.loads(run("issue", "list", "--state", "open", "--search", f'"{PROPOSAL_TITLE}" in:title',
                           "--json", "number,title"))
    found = [i for i in found if i["title"] == PROPOSAL_TITLE]
    if found:
        number = str(found[0]["number"])
        run("issue", "edit", number, "--body", body)
        print(f"updated proposal #{number}")
    else:
        url = run("issue", "create", "--title", PROPOSAL_TITLE, "--body", body).strip()
        print(url)
        number = url.rsplit("/", 1)[-1]
    liveness.verify_body("issue", number, body, run)


def main() -> int:
    today = datetime.date.today()
    since = (today - datetime.timedelta(days=7)).isoformat()
    merged = json.loads(gh("pr", "list", "--state", "merged", "--limit", "100",
                           "--search", f"merged:>={since}", "--json", "number,title"))
    human = json.loads(gh("pr", "list", "--state", "open", "--label", "needs-human", "--json", "number,title"))
    prs = json.loads(gh("pr", "list", "--state", "open", "--limit", "100", "--json", "number,title,headRefName"))
    keeper = [p for p in prs if p["headRefName"].startswith("agent/rule-keeper-")]
    ideas = [i for i in json.loads(gh("issue", "list", "--state", "open", "--label", "idea", "--limit", "100",
                                      "--json", "number,title,labels"))
             if "approved" not in {lab["name"] for lab in i["labels"]}]
    if append_metrics(METRICS, collect_metrics(today)):
        print(f"appended a row to {METRICS}")
    for title in friction_issues():
        print(f"created friction issue: {title}")
    model, queue_text, reasons = capacity_sections(today, gh, env_int("MAX_DEV", 2), env_int("MAX_PRS", 3))
    body = build_body(merged, human, keeper, ideas, today.isoformat(), status_stale_safe(),
                      failures=failure_watch_summary(gh, today, guard_mark.key_from_env()),
                      capacity=[model, queue_text])
    found = json.loads(gh("issue", "list", "--state", "open", "--search", f'"{TITLE}" in:title',
                          "--json", "number,title"))
    found = [i for i in found if i["title"] == TITLE]
    if found:
        number = str(found[0]["number"])
        gh("issue", "edit", number, "--body", body)
        print(f"updated #{number}")
    else:
        url = gh("issue", "create", "--title", TITLE, "--body", body).strip()
        print(url)
        number = url.rsplit("/", 1)[-1]
    liveness.verify_body("issue", number, body, gh)
    if reasons:
        upsert_proposal(proposal_body(reasons, model, queue_text, today.isoformat()))
    return 0


def run_main() -> int:
    try:
        return main()
    except liveness.ReadbackError as e:
        print(f"read-back failed: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(run_main())
