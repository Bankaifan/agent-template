"""Quota baseline (design 0007, section 4.7): model runs per day of the orchestrator workflow.

A run counts as a model run when its conclusion is not `skipped` and a job step named like `claude` ran
(step conclusion not `skipped`, from the jobs API). Runs with conclusion `skipped` are gate-skipped runs.

CLI (env: GH_REPO optional): run_stats.py [DAYS (default 14)] [WORKFLOW_FILE (default orchestrator.yml)]
"""
import datetime
import json
import sys

import liveness

WORKFLOW = "orchestrator.yml"
LIMIT = 1000


def parse_time(text):
    return datetime.datetime.strptime(text, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=datetime.UTC)


def ran_model(jobs):
    """True if any step whose name contains `claude` was not skipped."""
    for job in jobs:
        for step in job.get("steps") or []:
            if "claude" in str(step.get("name", "")).lower() and step.get("conclusion") not in (None, "skipped"):
                return True
    return False


def stats(runs, jobs_of, days=14, now=None):
    """runs: dicts with conclusion, createdAt, databaseId. jobs_of(run_id) -> list of jobs.
    Returns {"days", "model_runs", "gate_skipped", "per_day": {date: model runs}}."""
    now = now or datetime.datetime.now(datetime.UTC)
    cutoff = now - datetime.timedelta(days=days)
    per_day, skipped = {}, 0
    for run in runs:
        created = parse_time(run["createdAt"])
        if created < cutoff:
            continue
        if run.get("conclusion") == "skipped":
            skipped += 1
        elif ran_model(jobs_of(run["databaseId"])):
            day = created.date().isoformat()
            per_day[day] = per_day.get(day, 0) + 1
    total = sum(per_day.values())
    return {"days": days, "model_runs": total, "gate_skipped": skipped, "per_day": dict(sorted(per_day.items()))}


def format_stats(result):
    lines = [f"Model runs per day, last {result['days']} days:"]
    lines += [f"  {d}: {n}" for d, n in result["per_day"].items()]
    lines.append(f"Model runs: {result['model_runs']}, gate-skipped runs: {result['gate_skipped']}")
    lines.append(f"Model runs per day (average): {result['model_runs'] / result['days']:.2f}")
    return "\n".join(lines)


def fetch(workflow=WORKFLOW, repo=None, run=liveness.gh):
    base = ["--repo", repo] if repo else []
    runs = json.loads(run("run", "list", "--workflow", workflow, *base, "--limit", str(LIMIT),
                          "--json", "databaseId,conclusion,createdAt"))
    slug = repo or "{owner}/{repo}"

    def jobs_of(run_id):
        return json.loads(run("api", f"repos/{slug}/actions/runs/{run_id}/jobs", "--paginate",
                              "--jq", "{jobs: .jobs}")).get("jobs", [])
    return runs, jobs_of


def main(argv):
    import os
    days = int(argv[1]) if len(argv) > 1 else 14
    workflow = argv[2] if len(argv) > 2 else WORKFLOW
    runs, jobs_of = fetch(workflow, os.environ.get("GH_REPO"))
    print(format_stats(stats(runs, jobs_of, days)))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
