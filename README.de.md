# agent-template

Privates GitHub-Template für Projekte, in denen KI-Agenten Code schreiben und Menschen die Kontrolle behalten.

Leitidee: Regeln, die ein Skript prüfen kann, gehören in CI, nicht in Prompts. Die Agenten lesen eine kurze
`AGENTS.md`, die Strenge liefert CI (`make check`, Ruleset auf `main`). Entscheidung: `docs/decisions/0017-hpo-flow.md`.

## Was der Owner tut

- **Den Release-PR prüfen.** Der Merge-Train (`tools/train.py`) sammelt die Changelog-Zeilen von `main` in einem PR
  `Release <version>`: ein Versionsschritt pro Release, Text in `OWNER_LANG` (Standard Deutsch), dazu eine Zeile mit dem,
  was noch nicht gelöst ist. Das ist die einzige Review-Anfrage an den Owner; `VERSION` ändert sich erst beim Merge.
- **PRs, die einen CODEOWNERS-Pfad ändern** (GitHub verlangt das Review des Code-Owners): CODEOWNERS,
  `.github/rulesets/`, `tools/trusted_issues.py`, `tools/agent_guard.py`, `tools/guard_mark.py`, `tools/exec_log.py`,
  `tools/ci/risk.py`, `risk.yml`, `.agents/checks.json`. In einem Projekt gilt das auch für einen Template-Sync-PR mit solchen Dateien.
- **Einmal einrichten:** Secrets, zwei Apps, Ruleset (siehe unten).

Sonst wird niemand gefragt, erwähnt oder zugewiesen, und kein Mensch setzt ein Label.

## Wie die Agenten arbeiten

- Rollen in `.agents/roles/`. Agenten laufen in GitHub Actions mit `claude-code-action@v1` über das Claude-Abo (OAuth-Token, kein API-Key).
- Zwei GitHub-Apps: Autor pusht und öffnet PRs, Approver reviewt. Auto-Merge (rebase) nach Approve und grüner CI.
- Namen: jede Arbeit hat einen NAMEN. Issues und PRs heißen `V<major>-<NAME>: <Kurztext>`, jeder Commit
  `V<version>-<NAME>: <was er tut>`. Viele kleine Commits, kein Squash.
- Der Reviewer läuft nur bei grüner CI und führt nie PR-Code aus. Fix-Runden starten automatisch bei `CHANGES_REQUESTED`
  oder roter CI und laufen weiter, solange jede Runde Befunde erledigt; bleibt derselbe Befund nach zwei Fix-Runden in
  Folge offen (oder nach 8 Runden), startet die Aufgabe einmal neu.
- Der Merge-Train (`tools/train.py`) bringt freigegebene PRs nach `main`. Weil `main` einen aktuellen Branch verlangt,
  landen zwei oder mehr fertige PRs mit verschiedenen Dateien zusammen als ein PR `Batch: #a, #b` auf `agent/batch`:
  ein Skript baut ihn, `tools/reapprove.py` gibt ihn nur frei, wenn jede Datei genau dem entspricht, was der Approver
  in einem der PRs freigegeben hat. Ein Modell ist nicht beteiligt. Scheitert der Batch, wird er geschlossen und die
  PRs landen einzeln (`docs/decisions/0018-batch-train.md`, `TRAIN_BATCH=off` schaltet das ab).
- Was festhängt, bekommt per Skript `parked`: keine Notiz, keine Erwähnung. Der Entsperrer (`unblocker.yml`,
  `UNBLOCKER=off` schaltet ihn ab) schaut zuerst darauf: eine falsche Annahme bekommt eine Korrektur und einen Neustart,
  ein Fehler in der Agenten-Infrastruktur ein `prio:1`-Issue. `tools/status.py` startet jedes geparkte Element nach einer
  Pause neu (24 h, bei jedem Parken verdoppelt, höchstens 7 Tage).
- Intake (`intake.yml`, `INTAKE=off` schaltet ab): Issues von anderen und Scout-Ideen liest ein Modell ohne Token und
  Shell als maskierte Daten. Ein Skript prüft das Ergebnis und antwortet, lehnt ab oder legt einen Auftrag an
  (`Intake: #N`). Nur diesem Auftrag wird vertraut, und sein PR muss Risiko `none` haben.
- Nur vertrauenswürdige Eingaben steuern Agenten (`tools/trusted_issues.py`): Issues des Owners, Intake-Aufträge,
  Design- und Sync-Issues der Autor-App, signierte Guard-Issues.
- Dependabot-PRs prüft keine KI: ein Workflow ohne Modell approved sie nach grüner CI.
- Design-Studie `docs/design/NNNN-<slug>.md` nur, wenn eine Änderung berührt, wer oder was vertraut wird, Token- oder
  App-Rechte, CODEOWNERS-Pfade oder was das Repo verlässt. Der Design-Reviewer gibt sie frei und entscheidet die
  *Owner decisions*; danach legt ein Skript die Umsetzungs-Issues an.
- Risikoklassen (`tools/ci/risk.py`, Workflow `risk`): `security` und `infra`. Jeder solche Agenten-PR braucht zusätzlich
  den Security-Reviewer (Status `security-review`), danach Auto-Merge. `risk` und `security-review` ins Ruleset als Pflicht-Checks eintragen.
- Token-Grenze (`docs/decisions/0016-safety-boundary.md`): Entwickler- und Fix-Läufe haben kein Schreibrecht auf `workflows`
  oder `actions`; eine Workflow-Änderung läuft als Patch, den `workflow-apply` nach dem Security-Review anwendet.
- Wöchentlich: der Aufräumer (`cleaner.yml`, `CLEANER=off` schaltet ab) entfernt, was niemand braucht, ein Commit pro
  Entfernung mit Beleg; der Rule Keeper öffnet einen PR mit Regelvorschlägen. Täglich löscht `branch-cleanup` veraltete `agent/*`-Branches.
- Autonomer `orchestrator` (nur mit `ORCHESTRATOR_ENABLED=true`): schreibt Aufträge, hält höchstens `MAX_DEV` (Standard 4)
  `agent:dev`-Issues, aktualisiert HANDOVER.md per PR. Monatlicher `scout` eröffnet höchstens `IDEAS_PER_WEEK` (Standard 3, 0 = aus) `idea`-Issues.

## Einrichtung

1. Template nutzen (privat), Auto-Merge aktivieren, nur Rebase-Merge erlauben.
2. Zwei GitHub-Apps anlegen und installieren (Autor: Contents, Pull requests, Issues, Actions und Workflows schreiben; Approver: Pull requests schreiben).
3. Vier Secrets, in jedem Repo neu zu setzen (werden nicht vom Template geerbt): `CLAUDE_CODE_OAUTH_TOKEN` (`claude setup-token`), `AUTHOR_APP_KEY`, `APPROVER_APP_KEY`, `GUARD_KEY` (lange Zufallszeichenkette). Dazu vier Variablen: `AUTHOR_CLIENT_ID` und `APPROVER_CLIENT_ID` (Client-IDs der Apps, nicht geheim), `AUTHOR_BOT` und `APPROVER_BOT` (Bot-Logins der Apps, z. B. `my-author[bot]`); `setup` prüft sie. Optional: `OWNER` (Standard: Besitzer des Repos), `OWNER_LANG` (Standard `German`).
4. Ruleset `.github/rulesets/main.json` importieren (nach jeder Änderung der Datei erneut importieren). Das optionale `agent-refs.json` (nur Agenten-Branches) wird genauso importiert.
5. Workflow `setup` manuell starten: legt die Labels an und listet fehlende Secrets und Variablen (nur Namen).
6. Ersten Auftrag als Issue anlegen und `/dev` kommentieren (oder `ORCHESTRATOR_ENABLED=true` setzen).

## Grün heißt: die Agenten funktionieren auch

Bei PRs, die `.github/workflows/`, `.github/actions/` oder `tools/ci/` ändern, erzeugt der Pflicht-Check `agent-smoke`
mit den Workflow-Versionen des PRs beide App-Tokens, ruft damit `gh api /installation/repositories` auf und prüft, ob das
Claude-OAuth-Secret existiert (kein Modellaufruf). Ohne solche Pfade wird er übersprungen (= Erfolg). Dependabot-PRs
bekommen keine Actions-Secrets: die drei Secrets `CLAUDE_CODE_OAUTH_TOKEN`, `AUTHOR_APP_KEY` und `APPROVER_APP_KEY` auch als
**Dependabot-Secrets** anlegen, sonst schlägt `agent-smoke` dort mit klarer Meldung fehl. `setup` meldet, ob sie existieren
(best effort). Ruleset danach neu importieren.

## Projektdateien (keine Overrides)

Ein Projekt legt eigene Inhalte in vier Dateien ab, die das Template nie verwaltet. Ein Projekt mit diesen Dateien und ohne
Overrides übernimmt jeden Template-Sync als saubere Kopie (`docs/decisions/0008-extension-points.md`,
`docs/design/0016-extension-points.md`).

- `project.mk`: Rezepte für `project-check::`, die `make check` zuletzt ausführt. Das Makefile lädt die Datei, wenn sie existiert.
- `AGENTS.project.md`: Projektregeln, von `CLAUDE.md` nach `AGENTS.md` importiert. Die Limits in `AGENTS.md` haben Vorrang.
- `.agents/checks.json`: `{"required": ["name", ...]}`, zusätzliche Pflicht-Checks. `tools/ruleset.py build` fügt sie dem
  Template-Ruleset hinzu; ein Name, der einen Template-Check wiederholt, oder ein fehlerhafter Name wird abgelehnt. Nach einer
  Änderung das gebaute Ruleset in *Settings > Rules* neu importieren; ein Name gilt erst als Pflicht, wenn GitHub ihn erzwingt.
  Die Datei ist per CODEOWNERS geschützt.
- `.agents/tool-pins.env`: Pins für `RUFF`, `ZIZMOR` oder `ACTIONLINT` als `NAME=version`-Zeilen. Jede andere Zeile oder
  jeder andere Name lässt `tools/ci/install_tools.sh` scheitern.

Template-Tests liegen in `tests/agent/`, daher bleibt `tests/` für die eigenen Tests des Projekts frei.

## Projekte synchron halten

Projekte aus diesem Template bekommen spätere Template-Änderungen als einen Sync-PR pro Template-Release, nicht über
blindes Kopieren (`docs/decisions/0007-template-sync.md`, `docs/design/0011-automatic-template-sync.md`).
`template-sync.yml` prüft täglich (ohne Modell) und startet `tools/template_sync.py`. Ist die `VERSION` des Templates höher als
`synced_version` in `.agents/template.json`, kopiert ein Skript die geänderten Dateien, die zu `managed` passen (`clean`-Dateien
unverändert, `overridden`-Dateien per `git merge-file` zusammengeführt), und öffnet einen PR `Template sync <version>`, der
auch `synced_sha` und `synced_version` setzt. Ein sauberer Sync braucht kein Modell. Eine Datei, deren Zusammenführung
Konflikte hat, bleibt aus diesem PR heraus: der PR heißt `Template sync <kurze sha> part 1`, und das Issue
`Template sync <kurze sha>` (Label `agent:dev`) listet nur die Konflikt-Dateien und endet mit `Template-Sync: <40 hex>`. Der
Orchestrator vertraut dem Issue nur, wenn die Autor-App (`AUTHOR_BOT`) es geschrieben hat. Der Entwickler führt jede
Konflikt-Datei von Hand zusammen und behält dabei die Absicht bei (agent-dev legt die drei Fassungen vorher in das nicht
versionierte `.template/`), setzt `synced_sha` und `synced_version` und öffnet einen PR mit `Closes #<Sync-Issue>`.
Ein Sync-PR mit CODEOWNERS-Pfaden braucht das Review des Owners als Code-Owner.

Einrichtung eines Projekts (sechs Schritte):

1. **Autor-App.** Die Autor-App (Einrichtung, Schritt 2) auf dem Projekt installieren und, falls das Template privat ist, auch auf dem Template-Repo.
   Der geskriptete Sync braucht Schreibrechte für `contents` und `pull-requests` auf dem Projekt, für Syncs, die
   `.github/workflows/` ändern, zusätzlich `workflows`. Ohne sie fällt der Sync auf das Issue zurück.
2. **Sync-Dateien.** Projekte, die mit *Use this template* entstehen, haben `.github/workflows/template-sync.yml`,
   `tools/template_sync.py` und `tools/template_apply.py` schon. Ältere Projekte kopieren alle drei einmal aus dem Template; spätere Änderungen kommen über den Sync.
3. **`.agents/template.json` anlegen** (Beispiel unten): `template`, `synced_sha` (die 40-stellige Template-SHA, mit der du zuletzt
   übereinstimmst; leer heißt, der Lauf tut nichts), `synced_version` (die Template-Version, mit der du zuletzt
   übereinstimmst; fehlt sie, gilt `0.0`), `managed` und `overrides`.
4. **Optionale Variablen.** `TEMPLATE_SYNC=off` schaltet die Prüfung ab. `TEMPLATE_SYNC_MODE` ist standardmäßig `version`
   (ein Sync-PR pro Template-Release); `all` synchronisiert jeden Template-Commit.
   `TEMPLATE_SYNC_APPLY=off` schaltet zurück auf das reine Issue (das Skript öffnet dann keinen PR).
5. **Prüfen.** *Actions > template-sync > Run workflow* mit gesetztem `force` starten: das Gate wird übersprungen. Ein sauberes
   Template ergibt einen PR `Template sync`; ein Konflikt ergibt den PR Teil 1 und das Issue. Ein zweiter Lauf aktualisiert den
   offenen PR oder das Issue, statt ein weiteres anzulegen.
6. **Wenn der letzte Sync-PR gemergt ist** (der Skript-PR oder bei Konflikt der PR des Entwicklers), rücken `synced_sha` und
   `synced_version` auf den Template-Commit und die Version vor, mit der er übereinstimmt; der nächste Sync wartet auf das nächste Template-Release.

Ein anderes Projekt nutzt dieses Template genauso: mit *Use this template* anlegen, dann Schritte 1 bis 6. Sein Feld
`template` nennt dieses Repo (`Bankaifan/agent-template`); das Template verweist nirgends zurück auf das Projekt.

Beispiel `.agents/template.json` für ein Projekt (einmal von Hand anlegen; die Datei gehört nicht zum Template, damit neue
Projekte nicht darauf zurückzeigen):

```json
{
  "template": "Bankaifan/agent-template",
  "synced_sha": "<40 hex: der Template-Commit, mit dem du zuletzt übereinstimmst>",
  "synced_version": "1.1",
  "managed": [".github/workflows/", ".github/claude-judge-settings.json", ".github/dependabot.yml", ".github/CODEOWNERS", ".github/rulesets/",
              ".agents/roles/", "tools/", "tests/agent/", "AGENTS.md", "CLAUDE.md", "Makefile", "docs/design/README.md"],
  "overrides": [
    {"path": ".github/workflows/agent-fix.yml", "why": "workflow_run.workflows braucht den CI-Namen 'Validate'"}
  ]
}
```

- `synced_version`: die Template-Version, mit der du zuletzt übereinstimmst (setzt der Sync-PR).
- `managed`: Pfadpräfixe, die dem Template gehören (`/` am Ende = Verzeichnis). Andere Pfade werden nie gemeldet.
- `overrides`: exakter `path` plus Freitext `why` für den Entwickler. Projektinhalte zuerst in die vier Projektdateien
  legen (siehe *Projektdateien*); ein Override ist eine Ganzdatei-Kopie, die ein Sync nicht aktualisieren kann.
- Eine zu alte `synced_sha` macht nur das erste Issue größer. Ohne Datei oder bei leerer `synced_sha` meldet der Lauf
  `template-sync: no .agents/template.json, skipped` und endet erfolgreich. Im Template-Repo selbst wird ebenfalls übersprungen.
- Listet der Vergleich 300 oder mehr Dateien, kann er abgeschnitten sein. Der Lauf schlägt dann mit Meldung fehl, legt
  kein Issue an und ändert keines.
- Ein privates Template lesen kann nur, wenn die Autor-App auf dem Template-Repo installiert ist.

**Projektwerte.** Lieber Repo-Variablen als geänderte Dateien: `PYTHON_VERSION` (Standard `3.x`), `EXTRA_INSTALL` (Shell-Befehl,
den `tools/ci/install_tools.sh` nach den üblichen Tools ausführt; nur aus der Repo-Variable, nie aus einer Datei im PR-Branch)
und `RUNNER`. `TEMPLATE_SYNC=off` schaltet den Sync ab. `NIGHTLY_HEAVY_TESTS` (Standard `false`): bei `true` verlassen Tests mit `@pytest.mark.slow` PRs und `main` und laufen im nächtlichen Lauf `nightly.yml`, der bei Fehlschlag ein `prio:1`-Issue öffnet. Ein Test wird `slow` markiert, wenn er etwa 5 s braucht oder ein Netzwerk bzw. einen Dienst benötigt (eine Zeile `@pytest.mark.slow` über dem Test; der Marker ist in `tests/conftest.py` registriert, Design in `docs/design/0009-test-scoping.md`). Nur der CI-Name in `workflow_run.workflows` kann keine Variable sein
(GitHub erlaubt dort keine Ausdrücke). Er steht als `[validate]` in `agent-fix.yml`, `agent-review.yml`,
`dependabot-automerge.yml` und `orchestrator.yml`. Heißt die CI eines Projekts anders (z. B. `Validate`), passt es diese
Zeilen an und trägt die Dateien unter `overrides` ein.

Begründung: [docs/decisions/0007-template-sync.md](docs/decisions/0007-template-sync.md).

Alle Repo-Variablen mit Standardwert, Lesern, Wirkung und erlaubten Werten: [docs/variables.md](docs/variables.md).

Details und Grenzen: [README.md](README.md).
