"""Design 0017 step 6 (free shell for dev and fix runs) is held: no DEV_SHELL switch and no bare Bash grant ship yet.

The switch needs owner decision 1 ("ja") and steps 2 and 3 merged first. Until then the dev and fix model
steps keep the command list. This test fails when either part is added without that review."""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
WORKFLOWS = ROOT / ".github" / "workflows"
PATCHES = ROOT / ".agents" / "workflow-patches"
MODEL_JOBS = ("agent-dev.yml", "agent-fix.yml")
# A bare Bash tool: "Bash" not followed by "(" (a scoped form) or another word character.
BARE_BASH = re.compile(r"Bash(?![(\w])")


def allowed_tools_values(name):
    text = (WORKFLOWS / name).read_text()
    return re.findall(r'--allowedTools "([^"]*)"', text)


def test_no_switch_is_wired():
    for path in WORKFLOWS.glob("*.yml"):
        assert "DEV_SHELL" not in path.read_text(), path.name


def test_no_bare_bash_in_dev_or_fix():
    for name in MODEL_JOBS:
        values = allowed_tools_values(name)
        assert values, f"{name}: no --allowedTools found"
        for value in values:
            assert not BARE_BASH.search(value), f"{name}: bare Bash grant in --allowedTools"


def test_no_patch_grants_bare_bash():
    for patch in PATCHES.glob("*.patch"):
        for line in patch.read_text().splitlines():
            if line.startswith("+") and "--allowedTools" in line:
                assert not BARE_BASH.search(line), f"{patch.name}: bare Bash grant"
