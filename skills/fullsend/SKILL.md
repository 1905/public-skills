---
name: fullsend
description: "Run a feature end to end with no check-ins: spec → plan → self-review → implement → test → independent review → simplify → report. Use when the user says \"fullsend.\", \"fullsend\", \"full auto\", or \"do it all\"."
---

# fullsend.

The user hands over the whole feature. Run every stage yourself and report at the end.

## Pipeline

1. **Spec** — follow the `spec` skill. Skip the approval stop: a self-review replaces it. Ask a brainstorm question only if the request forks into truly different products.
2. **Plan** — follow the `plan` skill. A self-review of the plan replaces user approval.
3. **Implement** — follow the plan's Exec step: clean base branch, feature branch, task-by-task, verify each stage with build + tests yourself.
4. **Test** — run the project's full test suite and build where the project's docs say to.
5. **Review** — one independent read-only review of the whole branch diff (`git diff <base>...HEAD`) by a subagent or `/hill-climb`. Verify each finding. Fix confirmed issues. Skip false positives with a one-line note.
6. **Simplify** — run `/simplify` (or an equivalent cleanup pass) on the diff, unless the project opts out. Re-run tests after.
7. **Report** — what shipped, branch and commits, test results, review outcome, anything skipped.

Commit and push the feature branch after each finished task. Do not merge to the base branch unless the user asked for it.

## Stop only for

- A real safety issue.
- A decision only the user can make: a requirements fork, a destructive or irreversible action, missing credentials or access.
- A review that is still RUNNING. A running review blocks implementing; do only read-only prep while you wait. Skip a reviewer only when it FAILED, never because it's slow.

Everything else: state your assumption in one line and keep going.

## Rules

- Never ask "want me to continue?". Report at the end, or when you truly need the user.
- A failed reviewer does not stop unrelated work. Retry once. Then report the failure and never claim that review passed.
- Never replace a job that is still running.
- Long multi-phase jobs: if your host has a loop or scheduled-wakeup feature, arm a watchdog (e.g. `/loop 10m continue the fullsend job`). Each tick: pick up finished subagents, dispatch the next phase, fix verified review findings, unstick the main thread. Stop it after the final report.
- If you have a notification skill, notify the user when the job finishes or blocks on them.
