# agent-template

Privates GitHub-Template für Projekte, in denen KI-Agenten Code schreiben und Menschen die Kontrolle behalten.

Leitidee: Regeln, die ein Skript prüfen kann, gehören in CI, nicht in Prompts. Die Agenten lesen eine kurze
`AGENTS.md`, die Strenge liefert CI (`make check`, Ruleset auf `main`).

- Rollen: Orchestrator, Entwickler, Reviewer, Tester (`.agents/roles/`). Agenten laufen in GitHub Actions mit
  `claude-code-action@v1` über das Claude-Abo (OAuth-Token, kein API-Key).
- Zwei GitHub-Apps: Autor pusht und öffnet PRs, Approver reviewt. Auto-Merge (squash) nach Approve und grüner CI.
- Kontingent knapp: höchstens 2 Agenten-Jobs gleichzeitig, Modell je Rolle (haiku Routine, sonnet Kern und Review).

## Einrichtung

1. Template nutzen (privat), Auto-Merge aktivieren, nur Squash erlauben.
2. Zwei GitHub-Apps anlegen und installieren (Autor: Contents, Pull requests, Issues schreiben; Approver: Pull requests schreiben).
3. Fünf Secrets: `CLAUDE_CODE_OAUTH_TOKEN` (`claude setup-token`), `AUTHOR_APP_ID`, `AUTHOR_APP_KEY`, `APPROVER_APP_ID`, `APPROVER_APP_KEY`.
4. Ruleset `.github/rulesets/main.json` importieren.
5. Labels anlegen (Befehl in `README.md`).
6. Ersten Auftrag als Issue mit Label `agent:dev` anlegen (oder Kommentar `/dev`; `model:sonnet` für Kernarbeit).

Details und Grenzen: [README.md](README.md).
