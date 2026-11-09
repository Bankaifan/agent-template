"""Route a scout idea to the template repo or the project (no model).

An idea whose files are all under the `managed` paths of .agents/template.json belongs to the
template and is opened there (label `idea`, body ends with 'Found in: <project>#<context>').
Anything else, or a missing/invalid template.json, stays in the project.

  python3 tools/idea_route.py repo                      # print the template repo (for the workflow)
  python3 tools/idea_route.py create --title T --body-file F --files a,b [--context C] [--label L ...]

`create` needs GH_REPO and GH_TOKEN (project). The template issue uses TEMPLATE_GH_TOKEN only,
set as GH_TOKEN for that one `gh issue create -R <template>` call. Labels are an allowlist
(prio:2, prio:3), so approved/auto-ok can never be set. --body-file must be under /tmp.
"""
import argparse
import os
import pathlib
import re
import subprocess
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from template_sync import CONFIG, ConfigError, is_managed, parse_config

REPO_RE = re.compile(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+")
ALLOWED_LABELS = {"prio:2", "prio:3"}
BODY_DIR = pathlib.Path("/tmp")


def filter_labels(labels):
    """Allowlist: only exact prio:2 / prio:3 after strip+lower; commas and anything else are dropped."""
    out = []
    for lb in labels:
        norm = lb.strip().lower()
        if norm in ALLOWED_LABELS and norm not in out:
            out.append(norm)
    return out


def read_body(path):
    """Read the body file only from under /tmp (no runner files in a public repo)."""
    p = pathlib.Path(path).resolve()
    if BODY_DIR.resolve() not in p.parents:
        raise SystemExit(f"idea-route: --body-file must be under {BODY_DIR}")
    return p.read_text()


def load_config(path=CONFIG):
    """Return the parsed config, or None when missing, invalid or not a valid repo name."""
    try:
        cfg = parse_config(pathlib.Path(path).read_text())
    except (OSError, ConfigError):
        return None
    return cfg if REPO_RE.fullmatch(cfg["template"]) else None


def route(files, cfg, project=""):
    """Return 'template' or 'project'."""
    if not cfg or not files:
        return "project"
    if project.lower() == cfg["template"].lower():
        return "project"
    managed = cfg.get("managed", [])
    if not managed or not all(isinstance(m, str) for m in managed):
        return "project"
    clean = [f.strip() for f in files if f.strip()]
    if not clean or any(f.startswith("/") or ".." in f.split("/") for f in clean):
        return "project"
    return "template" if all(is_managed(f, managed) for f in clean) else "project"


def sanitize(text):
    """No mentions: '@' would notify people in another repo."""
    return text.replace("@", "")


def found_in(project, context):
    ctx = re.sub(r"[^A-Za-z0-9_.-]", "", context) or "scout"
    return f"Found in: {project}#{ctx}"


def is_duplicate(title, open_titles):
    norm = lambda s: " ".join(s.lower().split())
    return norm(title) in {norm(t) for t in open_titles}


def gh(*args, token=None):
    env = {**os.environ, "GH_TOKEN": token} if token else None
    return subprocess.run(["gh", *args], check=True, capture_output=True, text=True, env=env).stdout


def create(args):
    project = os.environ.get("GH_REPO", "")
    cfg = load_config()
    files = [f for f in args.files.split(",") if f.strip()]
    body = sanitize(read_body(args.body_file)).rstrip()
    title = sanitize(args.title)
    labels = filter_labels(args.label)
    if route(files, cfg, project) == "template":
        token = os.environ.get("TEMPLATE_GH_TOKEN", "")
        if not token:
            print("idea-route: no TEMPLATE_GH_TOKEN, opening in the project", file=sys.stderr)
        else:
            repo = cfg["template"]
            open_titles = [t for t in gh("issue", "list", "-R", repo, "--state", "open", "--label", "idea",
                                         "--limit", "200", "--json", "title", "--jq", ".[].title",
                                         token=token).splitlines()]
            if is_duplicate(title, open_titles):
                print(f"idea-route: duplicate in {repo}, nothing created")
                return 0
            print(gh("issue", "create", "-R", repo, "--label", "idea", "--title", title, "--body",
                     f"{body}\n\n{found_in(project, args.context)}", token=token).strip())
            return 0
    cmd = ["issue", "create", "--label", "idea", "--title", title, "--body", body]
    for lb in labels:
        cmd += ["--label", lb]
    print(gh(*cmd).strip())
    return 0


def main(argv=None):
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("repo")
    c = sub.add_parser("create")
    c.add_argument("--title", required=True)
    c.add_argument("--body-file", required=True)
    c.add_argument("--files", required=True)
    c.add_argument("--context", default="scout")
    c.add_argument("--label", action="append", default=[])
    args = p.parse_args(argv)
    if args.cmd == "repo":
        cfg = load_config()
        if cfg and cfg["template"].lower() != os.environ.get("GH_REPO", "").lower():
            print(cfg["template"])
        return 0
    return create(args)


if __name__ == "__main__":
    sys.exit(main())
