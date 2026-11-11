"""Design 0013 step 1: tools/rebump.py re-bumps VERSION on top of main and moves the PR's changelog lines.

Cases (a) to (c) of design section 6 are pure-function tests. The git tests run main() on a throwaway repo.
"""
import subprocess

import pytest
import rebump


def changelog(*blocks):
    """CHANGELOG.md text: an empty [Unreleased] block, then each (heading, bullets) block, newest first."""
    text = "# Changelog\n\n## [Unreleased]\n\n"
    for heading, bullets in blocks:
        text += f"## {heading}\n" + "".join(f"{b}\n" for b in bullets) + "\n"
    return text


BASE_CL = changelog(("[1.4] - 2026-11-10", ["- old"]))
PR_CL_15 = changelog(("[1.5] - 2026-11-11", ["- PR line"]), ("[1.4] - 2026-11-10", ["- old"]))
PR_CL_20 = changelog(("[2.0] - 2026-11-11", ["- PR line"]), ("[1.4] - 2026-11-10", ["- old"]))
MAIN_CL_15 = changelog(("[1.5] - 2026-11-11", ["- other line"]), ("[1.4] - 2026-11-10", ["- old"]))
MAIN_CL_20 = changelog(("[2.0] - 2026-11-11", ["- sync line"]), ("[1.5] - 2026-11-10", ["- other line"]))


def test_case_a_main_1_5_pr_step_y_gives_1_6():
    version, cl = rebump.rebump("1.4\n", "1.5\n", "1.5\n", BASE_CL, PR_CL_15, MAIN_CL_15)
    assert version == "1.6\n"
    assert "## [1.6] - 2026-11-11\n- PR line\n\n## [1.5] - 2026-11-11\n- other line\n" in cl


def test_case_b_main_2_0_pr_step_y_gives_2_1():
    version, cl = rebump.rebump("1.4\n", "1.5\n", "2.0\n", BASE_CL, PR_CL_15, MAIN_CL_20)
    assert version == "2.1\n"
    assert "## [2.1] - 2026-11-11\n- PR line\n\n## [2.0] - 2026-11-11\n- sync line\n" in cl


def test_case_c_main_1_5_pr_step_x_gives_2_0():
    version, cl = rebump.rebump("1.4\n", "2.0\n", "1.5\n", BASE_CL, PR_CL_20, MAIN_CL_15)
    assert version == "2.0\n"
    assert "## [2.0] - 2026-11-11\n- PR line\n\n## [1.5] - 2026-11-11\n- other line\n" in cl


def test_step_is_x_when_major_grows_and_y_when_minor_grows():
    assert rebump.step("1.4\n", "2.0\n") == "x"
    assert rebump.step("1.4\n", "1.5\n") == "y"


@pytest.mark.parametrize("pr_version", ["1.4\n", "1.3\n", "0.9\n"])
def test_pr_that_does_not_raise_version_is_refused(pr_version):
    with pytest.raises(rebump.Refused):
        rebump.rebump("1.4\n", pr_version, "1.5\n", BASE_CL, PR_CL_15, MAIN_CL_15)


def test_main_with_heading_already_present_is_refused():
    main_cl = changelog(("[1.6] - 2026-11-10", ["- x"]), ("[1.5] - 2026-11-10", ["- other line"]))
    with pytest.raises(rebump.Refused):
        rebump.rebump("1.4\n", "1.5\n", "1.5\n", BASE_CL, PR_CL_15, main_cl)


def test_conflict_outside_version_and_changelog_is_refused():
    assert rebump.refusal({"VERSION", "tools/train.py"}) == ["conflict outside VERSION and CHANGELOG.md: tools/train.py"]
    assert rebump.refusal({"VERSION", "CHANGELOG.md"}) == []
    assert rebump.refusal(set()) == []


def git(cwd, *args):
    subprocess.run(
        ["git", "-C", str(cwd), "-c", "user.name=t", "-c", "user.email=t@example.invalid", *args],
        check=True,
        capture_output=True,
    )


def commit(repo, files, message):
    for name, text in files.items():
        path = repo / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", message)


def make_repo(path, pr_extra=None, main_extra=None):
    """main: VERSION 1.4. Branch pr (checked out) bumps to 1.5 and adds a line; main bumps to 1.5 with its own line."""
    git(path, "init", "-q", "-b", "main")
    commit(path, {"VERSION": "1.4\n", "CHANGELOG.md": BASE_CL, "tools/train.py": "x = 1\n"}, "base")
    git(path, "checkout", "-q", "-b", "pr")
    commit(path, {"VERSION": "1.5\n", "CHANGELOG.md": PR_CL_15, **(pr_extra or {})}, "pr")
    git(path, "checkout", "-q", "main")
    commit(path, {"VERSION": "1.5\n", "CHANGELOG.md": MAIN_CL_15, **(main_extra or {})}, "main bump")
    git(path, "checkout", "-q", "pr")


def test_main_rebumps_on_top_of_main(tmp_path, monkeypatch, capsys):
    make_repo(tmp_path)
    monkeypatch.chdir(tmp_path)
    assert rebump.main(["main"]) == 0
    assert (tmp_path / "VERSION").read_text(encoding="utf-8") == "1.6\n"
    cl = (tmp_path / "CHANGELOG.md").read_text(encoding="utf-8")
    assert "## [1.6] - 2026-11-11\n- PR line\n\n## [1.5] - 2026-11-11\n- other line\n" in cl
    assert "VERSION 1.5 -> 1.6" in capsys.readouterr().out


def test_main_refuses_conflict_on_another_file(tmp_path, monkeypatch, capsys):
    make_repo(tmp_path, pr_extra={"tools/train.py": "x = 2\n"}, main_extra={"tools/train.py": "x = 3\n"})
    monkeypatch.chdir(tmp_path)
    assert rebump.main(["main"]) == 1
    assert "tools/train.py" in capsys.readouterr().out
    assert (tmp_path / "VERSION").read_text(encoding="utf-8") == "1.5\n"
