# Changelog

## [Unreleased]

## [1.1] - 2026-11-11
- `template-sync.yml` polls daily, gated by the template `x` version; `force` input and `TEMPLATE_SYNC_MODE=all` skip the gate.

## [1.0] - 2026-11-11
- First template version: `VERSION`, bump check for managed paths (`.agents/managed.json`), `x.y` accepted by `check_version.py`.
Sync: first versioned template; downstream repos record `synced_version` from here on.
