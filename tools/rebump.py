"""Re-bump VERSION on top of main and move the PR's changelog lines (design 0013 step 1, no model).

Usage: rebump.py [MAIN_REF]   (MAIN_REF default: origin/main; run on the PR branch, HEAD = the PR)
Refused (exit 1) unless the files changed on both sides since the merge base are only VERSION and CHANGELOG.md.
On success it writes the re-bumped VERSION and CHANGELOG.md into the working tree. The caller (step 2, train.py)
rebases the branch onto MAIN_REF and keeps those two files.

The PR's step is the bump it makes over its base: x (major grows, minor resets to 0) or y (minor grows).
It is applied to main's VERSION: x gives (m+1).0, y gives m.(n+1), so an x step always raises x.
"""
import pathlib
import re
import subprocess
import sys

VERSION_FILE = "VERSION"
CHANGELOG = "CHANGELOG.md"
ALLOWED = {VERSION_FILE, CHANGELOG}
HEADING = re.compile(r"^## \[([^\]]+)\](.*)$")


class Refused(Exception):
    """The PR cannot be re-bumped on main; the message says why."""


def parse(text):
    """(x, y) of an `x.y` VERSION text (one optional trailing newline), else Refused."""
    m = re.fullmatch(r"([0-9]+)\.([0-9]+)", (text or "").removesuffix("\n"), flags=re.ASCII)
    if not m:
        raise Refused(f"VERSION {(text or '').strip()!r} is not x.y (digits, one dot, no prefix)")
    return int(m.group(1)), int(m.group(2))


def fmt(version):
    return f"{version[0]}.{version[1]}"


def step(base_text, pr_text):
    """'x' or 'y': the bump the PR makes over its base. Refused when the PR does not raise VERSION."""
    base, pr = parse(base_text), parse(pr_text)
    if pr[0] > base[0]:
        return "x"
    if pr[0] == base[0] and pr[1] > base[1]:
        return "y"
    raise Refused(f"PR VERSION {fmt(pr)} does not raise the base {fmt(base)}")


def apply(main_text, bump):
    """main's VERSION with the PR's step applied."""
    x, y = parse(main_text)
    return f"{x + 1}.0" if bump == "x" else f"{x}.{y + 1}"


def new_lines(base_cl, pr_cl):
    """Bullet lines the PR adds to CHANGELOG.md (not in the base), in PR order."""
    old = set(base_cl.split("\n"))
    return [line for line in pr_cl.split("\n") if line.startswith("- ") and line not in old]


def pr_heading_suffix(pr_cl, pr_version):
    """The text after `## [pr_version]` in the PR's changelog (for example ` - 2026-11-11`), or ''."""
    for line in pr_cl.split("\n"):
        m = HEADING.match(line)
        if m and m.group(1) == pr_version:
            return m.group(2)
    return ""


def move_lines(main_cl, lines, version, suffix):
    """main's CHANGELOG.md with a `## [version]` block holding `lines`, above the newest released heading."""
    out = main_cl.split("\n")
    if any((m := HEADING.match(line)) and m.group(1) == version for line in out):
        raise Refused(f"CHANGELOG.md on main already has a [{version}] heading")
    have = set(out)
    block = [f"## [{version}]{suffix}", *[line for line in lines if line not in have], ""]
    idx = next(
        (i for i, line in enumerate(out) if (m := HEADING.match(line)) and m.group(1).lower() != "unreleased"),
        len(out),
    )
    return "\n".join(out[:idx] + block + out[idx:])


def rebump(base_version, pr_version, main_version, base_cl, pr_cl, main_cl):
    """(VERSION text, CHANGELOG.md text) for the PR rebased onto main. Raises Refused."""
    bump = step(base_version, pr_version)
    version = apply(main_version, bump)
    suffix = pr_heading_suffix(pr_cl, fmt(parse(pr_version)))
    lines = move_lines(main_cl, new_lines(base_cl, pr_cl), version, suffix)
    return f"{version}\n", lines


def refusal(conflicts):
    """Error lines for conflicting files other than VERSION and CHANGELOG.md; empty list: the re-bump may run."""
    return [f"conflict outside VERSION and CHANGELOG.md: {f}" for f in sorted(conflicts) if f not in ALLOWED]


def git(*args):
    return subprocess.run(["git", *args], check=True, capture_output=True, text=True).stdout


def show(rev, path):
    """File text at a revision, None when it does not exist there."""
    try:
        return git("show", f"{rev}:{path}")
    except subprocess.CalledProcessError:
        return None


def changed(base, rev):
    return {f for f in git("diff", "--name-only", base, rev).split("\n") if f}


def main(argv=None) -> int:
    args = sys.argv[1:] if argv is None else argv
    main_ref = args[0] if args else "origin/main"
    try:
        base = git("merge-base", main_ref, "HEAD").strip()
        errs = refusal(changed(base, "HEAD") & changed(base, main_ref))
        if not errs:
            texts = {
                "base_version": show(base, VERSION_FILE),
                "pr_version": show("HEAD", VERSION_FILE),
                "main_version": show(main_ref, VERSION_FILE),
            }
            missing = [k for k, v in texts.items() if v is None]
            if missing:
                errs = [f"VERSION missing ({', '.join(missing)})"]
            else:
                version, cl = rebump(
                    texts["base_version"],
                    texts["pr_version"],
                    texts["main_version"],
                    show(base, CHANGELOG) or "",
                    show("HEAD", CHANGELOG) or "",
                    show(main_ref, CHANGELOG) or "",
                )
                pathlib.Path(VERSION_FILE).write_text(version, encoding="utf-8")
                pathlib.Path(CHANGELOG).write_text(cl, encoding="utf-8")
                print(f"rebump: VERSION {fmt(parse(texts['pr_version']))} -> {version.strip()} on {main_ref}")
                return 0
    except Refused as e:
        errs = [str(e)]
    except (OSError, subprocess.CalledProcessError) as e:
        print(f"rebump: cannot run: {e}", file=sys.stderr)
        return 2
    for e in errs:
        print(f"rebump: refused: {e}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
