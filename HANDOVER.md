# Handover
<!-- Overwrite, do not append. History lives in git and CHANGELOG. Max 60 lines. -->

## Goal
Pipeline hardening on prio:1: actions watcher (#413, design 0012), scripted template sync (#475-#481),
denied-command guard (#487-#489), version/changelog fragments (#468), review-round rule (#469), footer strip (#471).

## Current state (measured 2026-11-12, issue_comment run, DISPATCH off)
- Open PRs: none. No agent/rule-keeper PRs open.
- Main CI at 2bd036b: last 10 runs all skipped, no red run.
- Free agent:dev slots 4, free PR slots 5 at start of this run.
- Started this run (slip, overlap exit 0, model:sonnet, then agent:dev): #429, #468, #469, #471.
- Trusted list also holds prio:1 #413-#416, #430, #475-#482, #487-#489 and guard issues #484, #485; prio:2 and prio:3 items behind them.
- #415 carries needs-human.

## Open
- #429 depends on #428: whether #428 is merged is open (the script listed #429 as startable).
- Design 0005 section 9 (Limit 5 exception): yes/no for Daniel, blocks #201 only.
- #117 follow-up: second app token scoped to the template repo (Daniel to provision).
- Guard issues #484 (status.yml) and #485 (watch.yml cancelled): cause not analysed.

## Next 3 steps
1. Review the PRs of #429, #468, #469, #471 as they arrive; remove agent:dev after each merge.
2. Start the next trusted issues (#430, #475, #487 ...) as slots free up.
3. Daniel decides on #415 (needs-human).
