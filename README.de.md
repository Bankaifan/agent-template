# agent-template

Privates GitHub-Template für Projekte, in denen KI-Agenten Code schreiben und Menschen die Kontrolle behalten.

Leitidee: Regeln, die ein Skript prüfen kann, gehören in CI, nicht in Prompts. Die Agenten lesen eine kurze
`AGENTS.md`, die Strenge liefert CI (`make check`, Ruleset auf `main`).

- Rollen: Orchestrator, Entwickler, Reviewer (`.agents/roles/`). Agenten laufen in GitHub Actions mit
  `claude-code-action@v1` über das Claude-Abo (OAuth-Token, kein API-Key).
- Zwei GitHub-Apps: Autor pusht und öffnet PRs, Approver reviewt. Auto-Merge (rebase) nach Approve und grüner CI. Der Entwickler fasst seinen Branch vor dem Review zu einem Commit von Daniel zusammen, so ist Daniel einziger Autor auf `main`.
- Der Reviewer läuft nur bei grüner CI (`workflow_run` von `validate`) und führt nie PR-Code aus (Checkout von `main`, PR per `gh`). Fix-Runden starten automatisch bei `CHANGES_REQUESTED` oder roter CI (max. 2, dann `needs-human`). Nach dem Push stellt ein Skript-Schritt sicher, dass `validate` auf dem Head-SHA läuft. Dependabot-PRs prüft keine KI: ein Workflow ohne Modell approved Patch/Minor nach grüner CI, Majors bekommen `needs-human`; den Update-Typ liefert `dependabot/fetch-metadata` (Gruppen: höchster Typ gilt), Fallback ist der Titel. Jedes `needs-human` an einem PR fordert zusätzlich Daniels Review an (erscheint unter "Needs your review"). Grosse Arbeit (Architektur, Breaking, Release, mehrere PRs) beginnt mit einer Design-Studie `docs/design/NNNN-<slug>.md`, die ein Design-Reviewer prüft; nur der Abschnitt *Owner decisions* braucht Daniel, ist er leer, wird ohne ihn gemergt. Danach legt der Orchestrator die Umsetzungs-Issues an (Zeile `Design: docs/design/...`, vertrauenswürdig über `tools/trusted_issues.py`).
- `.github/CODEOWNERS`: `@Bankaifan` besitzt nur sicherheitsrelevante Dateien: `AGENTS.md`, CODEOWNERS, `.github/rulesets/`, `tools/trusted_issues.py`, `tools/agent_guard.py`, `tools/ci/risk.py`, `risk.yml`.
- Risikoklassen (`tools/ci/risk.py`, Workflow `risk`): Ein Diff an `permissions:`, `allowedTools`, `allowed_bots`, Secrets/Tokens, Vertrauenslogik, Rulesets, CODEOWNERS oder den Limits in AGENTS.md ist `security` (Label `risk:security`; der Pflicht-Check `risk` bleibt rot, bis Daniel den Head-Commit freigibt). Andere Aenderungen an der Agenten-Infrastruktur sind `infra`. Jeder `infra`/`security`-Agenten-PR braucht zusaetzlich den Security-Reviewer (`.agents/roles/security-reviewer.md`, Status `security-review`), danach Auto-Merge. Was auf Daniel wartet, endet mit einer kurzen deutschen Erklaerung (was, schlimmster Fall, Empfehlung, Ja/Nein-Frage). `risk` und `security-review` ins Ruleset als Pflicht-Checks eintragen.
- Ein Entsperrer (`.agents/roles/unblocker.md`, `.github/workflows/unblocker.yml`) prüft jedes `needs-human` vor Daniel: eine falsche Annahme bekommt eine Korrektur und einen automatischen Neustart (`unblock:1`), ein Fehler in der Agenten-Infrastruktur wird als `prio:1`-Issue gemeldet, nur eine echte Owner-Entscheidung bleibt bei Daniel. Das Modell hat kein Token und keine Shell und liest maskierte Dateien; ein Skript prüft sein Ergebnis und führt alle Aktionen aus (`docs/decisions/0010-unblocker.md`). `UNBLOCKER=off` schaltet ihn ab.
- Wöchentlicher Rule Keeper (ein PR mit Regelvorschlägen, Daniel merged) und täglicher `branch-cleanup` (löscht veraltete `agent/*`-Branches, Dry-Run bei manuellem Start).
- Kontingent knapp: höchstens 2 Agenten-Jobs gleichzeitig, Modell je Rolle (haiku Routine, sonnet Kern und Review).
- Autonomer `orchestrator` (nach Merge auf `main` per `workflow_run` von `validate`, täglich, manuell; nur mit Variable `ORCHESTRATOR_ENABLED=true`): schreibt Aufträge, hält max. 2 `agent:dev`-Issues, bearbeitet `needs-human`-PRs, aktualisiert HANDOVER.md per PR ; ein Skript (`tools/prefilter.py`) überspringt den Modelllauf, wenn nichts zu tun ist. Das Issue "Weekly summary" pflegt montags ein Skript ohne Modell; es ergänzt auch per PR eine Zeile in `docs/metrics.csv` (Stufen S/M/L: `docs/decisions/0008-tiers.md`). Actions-Minuten sind in öffentlichen Repos kostenlos; private Repos haben ein monatliches Kontingent, Zeitpläne laufen dort daher langsamer. Monatlicher `scout` (haiku, auch aus Dependabot/CodeQL-Meldungen) eröffnet höchstens `IDEAS_PER_WEEK` (Standard 3, 0 = aus) `idea`-Issues; er setzt nur `idea`. Nur vertrauenswürdige Eingaben steuern Agenten: der Orchestrator sieht nur Issues von Daniel oder mit `approved`/`auto-ok` von Daniel (Skript `tools/trusted_issues.py`). Beide Variablen steuern das Kontingent.

## Einrichtung

1. Template nutzen (privat), Auto-Merge aktivieren, nur Rebase-Merge erlauben.
2. Zwei GitHub-Apps anlegen und installieren (Autor: Contents, Pull requests, Issues, Actions und Workflows schreiben; Approver: Pull requests schreiben).
3. Drei Secrets, in jedem Repo neu zu setzen (werden nicht vom Template geerbt): `CLAUDE_CODE_OAUTH_TOKEN` (`claude setup-token`), `AUTHOR_APP_KEY`, `APPROVER_APP_KEY`. Dazu vier Variablen: `AUTHOR_CLIENT_ID` und `APPROVER_CLIENT_ID` (Client-IDs der Apps, nicht geheim), `AUTHOR_BOT` und `APPROVER_BOT` (Bot-Logins der Apps, z. B. `my-author[bot]`); `setup` prüft sie.
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

## Projekte synchron halten

Projekte aus diesem Template bekommen spätere Template-Änderungen über einen wöchentlichen Bericht, nicht über blindes
Kopieren. `template-sync.yml` (montags oder `workflow_dispatch`; ohne Modell) startet `tools/template_sync.py`. Das Skript
vergleicht `main` des Templates mit `synced_sha` aus `.agents/template.json` und listet geänderte Dateien, die zu `managed`
passen. Es legt das eine offene Issue `Template sync <kurze sha>` an (Labels `agent:dev`, `model:sonnet`) oder bearbeitet
es, falls schon eines offen ist. Dateien unter `overrides` stehen getrennt, mit ihrem `why`. Das Issue endet mit
`Template-Sync: <40 hex>`; der Orchestrator vertraut ihm nur, wenn die Autor-App (`AUTHOR_BOT`) es geschrieben hat. Der
Entwickler übernimmt `clean`-Dateien unverändert, `overridden`-Dateien von Hand unter Beachtung der Absicht, setzt
`synced_sha` auf diese SHA und öffnet einen PR mit `Closes #<Sync-Issue>`. Der PR berührt `.github/`, also muss Daniel als
Code-Owner freigeben.

Beispiel `.agents/template.json` für ein Projekt (einmal von Hand anlegen; die Datei gehört nicht zum Template, damit neue
Projekte nicht darauf zurückzeigen):

```json
{
  "template": "Bankaifan/agent-template",
  "synced_sha": "<40 hex: der Template-Commit, mit dem du zuletzt übereinstimmst>",
  "managed": [".github/workflows/", ".github/dependabot.yml", ".github/CODEOWNERS", ".github/rulesets/",
              ".agents/roles/", "tools/", "tests/", "AGENTS.md", "CLAUDE.md", "Makefile", "docs/design/README.md"],
  "overrides": [
    {"path": ".github/workflows/agent-fix.yml", "why": "workflow_run.workflows braucht den CI-Namen 'Validate'"},
    {"path": "AGENTS.md", "why": "Projektsatz und Projektregeln"}
  ]
}
```

- `managed`: Pfadpräfixe, die dem Template gehören (`/` am Ende = Verzeichnis). Andere Pfade werden nie gemeldet.
- `overrides`: exakter `path` plus Freitext `why` für den Entwickler.
- Eine zu alte `synced_sha` macht nur das erste Issue größer. Ohne Datei oder bei leerer `synced_sha` meldet der Lauf
  `template-sync: no .agents/template.json, skipped` und endet erfolgreich. Im Template-Repo selbst wird ebenfalls übersprungen.
- Listet der Vergleich 300 oder mehr Dateien, kann er abgeschnitten sein. Der Lauf schlägt dann mit Meldung fehl, legt
  kein Issue an und ändert keines.
- Ein privates Template lesen kann nur, wenn die Autor-App auf dem Template-Repo installiert ist.

**Projektwerte.** Lieber Repo-Variablen als geänderte Dateien: `PYTHON_VERSION` (Standard `3.x`), `EXTRA_INSTALL` (Shell-Befehl,
den `tools/ci/install_tools.sh` nach den üblichen Tools ausführt; nur aus der Repo-Variable, nie aus einer Datei im PR-Branch)
und `RUNNER`. `TEMPLATE_SYNC=off` schaltet den Sync ab. Nur der CI-Name in `workflow_run.workflows` kann keine Variable sein
(GitHub erlaubt dort keine Ausdrücke). Er steht als `[validate]` in `agent-fix.yml`, `agent-review.yml`,
`dependabot-automerge.yml` und `orchestrator.yml`. Heißt die CI eines Projekts anders (z. B. `Validate`), passt es diese
Zeilen an und trägt die Dateien unter `overrides` ein.

Begründung: [docs/decisions/0007-template-sync.md](docs/decisions/0007-template-sync.md).

Details und Grenzen: [README.md](README.md).
