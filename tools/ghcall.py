"""Run gh. A read call is retried on a transient failure, a write never; the final error carries stderr."""

import subprocess
import time

DELAYS = (2, 5)  # seconds before retry 1 and retry 2
READ_GROUPS = {"pr": {"view", "diff", "list"}, "issue": {"view", "list"}, "run": {"view", "list"}, "label": {"list"}}
WRITE_FLAGS = ("-f", "-F", "--input", "--field", "--raw-field")


class GhError(subprocess.CalledProcessError):
    """CalledProcessError whose message ends with the last 300 chars of stderr."""

    def __str__(self):
        err = (self.stderr or "").strip()[-300:] or "(no stderr)"
        return f"{super().__str__()} stderr: {err}"


def is_read(args):
    """True for a call that changes nothing on GitHub (safe to repeat)."""
    args = [str(a) for a in args]
    if not args:
        return False
    if args[0] == "api":
        rest = args[1:]
        for i, a in enumerate(rest):
            if a in ("-X", "--method") and i + 1 < len(rest) and rest[i + 1].upper() != "GET":
                return False
            if a.startswith("--method=") and a.split("=", 1)[1].upper() != "GET":
                return False
            if a.startswith("-X") and len(a) > 2 and a[2:].upper() != "GET":
                return False
            if a in WRITE_FLAGS or a.startswith(("--input=", "--field=", "--raw-field=")):
                return False
        return True
    return len(args) > 1 and args[1] in READ_GROUPS.get(args[0], ())


def gh(*args, sleep=time.sleep):
    """Return gh stdout. Read calls get up to two retries; a write runs once."""
    delays = DELAYS if is_read(args) else ()
    attempt = 0
    while True:
        try:
            return subprocess.run(["gh", *args], check=True, capture_output=True, text=True).stdout
        except subprocess.CalledProcessError as e:
            if attempt >= len(delays):
                raise GhError(e.returncode, e.cmd, output=e.output, stderr=e.stderr) from e
            sleep(delays[attempt])
            attempt += 1
