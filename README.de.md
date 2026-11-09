# agent-template

Privates GitHub-Template für Projekte, in denen KI-Agenten Code schreiben und Menschen die Kontrolle behalten.

Leitidee: Regeln, die ein Skript prüfen kann, gehören in CI, nicht in Prompts. Die Agenten lesen eine kurze
`AGENTS.md`, die Strenge liefert CI (`make check`, Ruleset auf `main`).

- Rollen: Orchestrator, Entwickler, Reviewer (`.agents/roles/`). Agenten laufen in GitHub Actions mit
  `claude-code-action@v1` über das Claude-Abo (OAuth-Token, kein API-Key).
- Zwei GitHub-Apps: Autor pusht und öffnet PRs, Approver reviewt. Auto-Merge (rebase) nach Approve und grüner CI. Der Entwickler fasst seinen Branch vor dem Review zu einem Commit von Daniel zusammen, so ist Daniel einziger Autor auf `main`.
- Der Reviewer läuft nur bei grüner CI (`workflow_run` von `validate`) und führt nie PR-Code aus (Checkout von `main`, PR per `gh`). Fix-Runden starten automatisch bei `CHANGES_REQUESTED` oder roter CI (max. 2, dann `needs-human`). Nach dem Push stellt ein Skript-Schritt sicher, dass `validate` auf dem Head-SHA läuft. Dependabot-PRs prüft keine KI: ein Workflow ohne Modell approved Patch/Minor nach grüner CI, Majors bekommen `needs-human`; den Update-Typ liefert `dependabot/fetch-metadata` (Gruppen: höchster Typ gilt), Fallback ist der Titel. Jedes `needs-human` an einem PR fordert zusätzlich Daniels Review an (erscheint unter "Needs your review"). Grosse Arbeit (Architektur, Breaking, Release, mehrere PRs) beginnt mit einer Design-Studie `docs/design/NNNN-<slug>.md`, die ein Design-Reviewer prüft; nur der Abschnitt *Owner decisions* braucht Daniel, ist er leer, wird ohne ihn gemergt. Danach legt der Orchestrator die Umsetzungs-Issues an (Zeile `Design: docs/design/...`, vertrauenswürdig über `tools/trusted_issues.py`).
- `.github/CODEOWNERS`: `@Bankaifan` besitzt `AGENTS.md`, `CLAUDE.md`, `.agents/`, `.github/`, `.claude/`, `.mcp.json`, `tools/check/` (Ruleset verlangt Code-Owner-Review).
- Wöchentlicher Rule Keeper (ein PR mit Regelvorschlägen, Daniel merged) und täglicher `branch-cleanup` (löscht veraltete `agent/*`-Branches, Dry-Run bei manuellem Start).
- Kontingent knapp: höchstens 2 Agenten-Jobs gleichzeitig, Modell je Rolle (haiku Routine, sonnet Kern und Review).
- Autonomer `orchestrator` (nach Merge auf `main` per `workflow_run` von `validate`, täglich, manuell; nur mit Variable `ORCHESTRATOR_ENABLED=true`): schreibt Aufträge, hält max. 2 `agent:dev`-Issues, bearbeitet `needs-human`-PRs, aktualisiert HANDOVER.md per PR ; ein Skript (`tools/prefilter.py`) überspringt den Modelllauf, wenn nichts zu tun ist. Das Issue "Weekly summary" pflegt montags ein Skript ohne Modell. Monatlicher `scout` (haiku, auch aus Dependabot/CodeQL-Meldungen) eröffnet höchstens `IDEAS_PER_WEEK` (Standard 3, 0 = aus) `idea`-Issues; er setzt nur `idea`. Nur vertrauenswürdige Eingaben steuern Agenten: der Orchestrator sieht nur Issues von Daniel oder mit `approved`/`auto-ok` von Daniel (Skript `tools/trusted_issues.py`). Beide Variablen steuern das Kontingent.

## Einrichtung

1. Template nutzen (privat), Auto-Merge aktivieren, nur Rebase-Merge erlauben.
2. Zwei GitHub-Apps anlegen und installieren (Autor: Contents, Pull requests, Issues, Actions und Workflows schreiben; Approver: Pull requests schreiben).
3. Fünf Secrets, in jedem Repo neu zu setzen (werden nicht vom Template geerbt): `CLAUDE_CODE_OAUTH_TOKEN` (`claude setup-token`), `AUTHOR_APP_ID`, `AUTHOR_APP_KEY`, `APPROVER_APP_ID`, `APPROVER_APP_KEY`. Dazu zwei Variablen: `AUTHOR_BOT` und `APPROVER_BOT` (Bot-Logins der Apps, z. B. `my-author[bot]`); `setup` prüft sie.
4. Ruleset `.github/rulesets/main.json` importieren (nach jeder Änderung der Datei erneut importieren).
5. Workflow `setup` manuell starten: legt die Labels an und listet fehlende Secrets (nur Namen).
6. Ersten Auftrag als Issue mit Label `agent:dev` anlegen (oder Kommentar `/dev`; `model:sonnet` für Kernarbeit).

## Grün heißt: die Agenten funktionieren auch

Bei PRs, die `.github/workflows/`, `.github/actions/` oder `tools/ci/` ändern, erzeugt der Pflicht-Check `agent-smoke`
mit den Workflow-Versionen des PRs beide App-Tokens, ruft damit `gh api /installation/repositories` auf und prüft, ob das
Claude-OAuth-Secret existiert (kein Modellaufruf). Ohne solche Pfade wird er übersprungen (= Erfolg). Dependabot-PRs
bekommen keine Actions-Secrets: die fünf Secrets (und die Variablen `AUTHOR_BOT`, `APPROVER_BOT`) auch als
**Dependabot-Secrets** anlegen, sonst schlägt `agent-smoke` dort mit klarer Meldung fehl. `setup` meldet, ob sie existieren
(best effort). Ruleset danach neu importieren.

Details und Grenzen: [README.md](README.md).
