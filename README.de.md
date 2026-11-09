# agent-template

Privates GitHub-Template für Projekte, in denen KI-Agenten Code schreiben und Menschen die Kontrolle behalten.

Leitidee: Regeln, die ein Skript prüfen kann, gehören in CI, nicht in Prompts. Die Agenten lesen eine kurze
`AGENTS.md`, die Strenge liefert CI (`make check`, Ruleset auf `main`).

- Rollen: Orchestrator, Entwickler, Reviewer, Tester (`.agents/roles/`). Agenten laufen in GitHub Actions mit
  `claude-code-action@v1` über das Claude-Abo (OAuth-Token, kein API-Key).
- Zwei GitHub-Apps: Autor pusht und öffnet PRs, Approver reviewt. Auto-Merge (rebase) nach Approve und grüner CI. Der Entwickler fasst seinen Branch vor dem Review zu einem Commit von Daniel zusammen, so ist Daniel einziger Autor auf `main`.
- Fix-Runden starten automatisch bei `CHANGES_REQUESTED` (max. 2, dann `needs-human`). Dependabot-PRs prüft keine KI: ein Workflow ohne Modell approved Patch/Minor nach grüner CI, Majors bekommen `needs-human`.
- `.github/CODEOWNERS`: `@Bankaifan` besitzt `AGENTS.md`, `CLAUDE.md`, `.agents/`, `.github/`, `tools/check/` (Ruleset verlangt Code-Owner-Review).
- Wöchentlicher Rule Keeper (ein PR mit Regelvorschlägen, Daniel merged) und täglicher `branch-cleanup` (löscht veraltete `agent/*`-Branches, Dry-Run bei manuellem Start).
- Kontingent knapp: höchstens 2 Agenten-Jobs gleichzeitig, Modell je Rolle (haiku Routine, sonnet Kern und Review).
- Autonomer `orchestrator` (Push auf `main`, täglich, manuell; nur mit Variable `ORCHESTRATOR_ENABLED=true`): schreibt Aufträge, hält max. 2 `agent:dev`-Issues, bearbeitet `needs-human`-PRs, aktualisiert HANDOVER.md per PR und pflegt das Issue "Weekly summary". Wöchentlicher `scout` (haiku) eröffnet höchstens `IDEAS_PER_WEEK` (Standard 3, 0 = aus) `idea`-Issues; kleine bekommen `auto-ok`, der Rest wartet auf Daniels Label `approved`. Beide Variablen steuern das Kontingent.

## Einrichtung

1. Template nutzen (privat), Auto-Merge aktivieren, nur Rebase-Merge erlauben.
2. Zwei GitHub-Apps anlegen und installieren (Autor: Contents, Pull requests, Issues schreiben; Approver: Pull requests schreiben).
3. Fünf Secrets, in jedem Repo neu zu setzen (werden nicht vom Template geerbt): `CLAUDE_CODE_OAUTH_TOKEN` (`claude setup-token`), `AUTHOR_APP_ID`, `AUTHOR_APP_KEY`, `APPROVER_APP_ID`, `APPROVER_APP_KEY`.
4. Ruleset `.github/rulesets/main.json` importieren (nach jeder Änderung der Datei erneut importieren).
5. Workflow `setup` manuell starten: legt die Labels an und listet fehlende Secrets (nur Namen).
6. Ersten Auftrag als Issue mit Label `agent:dev` anlegen (oder Kommentar `/dev`; `model:sonnet` für Kernarbeit).

Details und Grenzen: [README.md](README.md).
