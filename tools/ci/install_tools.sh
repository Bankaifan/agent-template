#!/usr/bin/env bash
# Install the pinned tools that `make check` and CI use. Used by validate, agent-dev and agent-fix.
# Bump versions here only; one place for every workflow.
set -euo pipefail
RUFF=0.17.4
ZIZMOR=1.5.2
ACTIONLINT=1.7.7
pip install "ruff==$RUFF" "zizmor==$ZIZMOR" pytest pytest-timeout
for f in requirements.txt requirements_test.txt; do
  if [ -f "$f" ]; then pip install -r "$f"; fi
done
dir="${RUNNER_TEMP:-/tmp}/actionlint"
mkdir -p "$dir"
curl -fsSL "https://github.com/rhysd/actionlint/releases/download/v${ACTIONLINT}/actionlint_${ACTIONLINT}_linux_amd64.tar.gz" \
  | tar -xz -C "$dir" actionlint
if [ -n "${GITHUB_PATH:-}" ]; then echo "$dir" >> "$GITHUB_PATH"; fi
