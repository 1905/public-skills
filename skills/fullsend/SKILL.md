---
name: fullsend
description: "Run a feature end to end with no check-ins: spec → plan → implement → test → review → simplify → close out → report. Use when the user says \"fullsend.\", \"fullsend\", \"full auto\", or \"do it all\"."
---

# fullsend.

The user hands over the whole feature. Run every stage yourself and report at the end.
This skill uses the `spec` and `plan` skills; install them too.

## Pipeline

1. **Spec** — follow the `spec` skill. Replace its approval stop with its self-review, then set `**Status:** approved`. Ask a brainstorm question only if the request forks into truly different products.
2. **Plan** — follow the `plan` skill, steps 1-5. Replace its approval stop with its self-review, then set `**Status:** approved`.
3. **Implement** — follow the `plan` skill's step 8, sub-steps 1-6 (preconditions through per-stage verification). Do not run its branch review (8.7) here; step 5 below does that.
4. **Test** — run the project's full build and test suite where the project's docs say to.
5. **Review** — one independent read-only review of the whole branch diff (`git diff <base>...HEAD`) by a subagent, or `/hill-climb` if the user asked for it. Verify each finding. Fix confirmed issues. Skip false positives with a one-line note. Re-run build + tests. Commit.
6. **Simplify** — run `/simplify` on the diff if you have it, otherwise do one cleanup pass yourself. Skip if the project opts out. Re-run build + tests. Commit.
7. **Close out** — `plan` skill steps 9-10: reconcile the spec, set `done`, move the feature dir to `plans/done/`. Commit.
8. **Report** — what shipped, branch and commits, test results, review outcome, anything skipped or assumed.

Commit after each task and after steps 5, 6 and 7. Push the feature branch after each commit only if the repo has a remote and the project pushes work-in-progress branches; otherwise push once at the end, or not at all for a local-only repo. Do not merge to the base branch unless the user asked for it.

## Stop only for

- A real safety issue.
- A decision only the user can make: a requirements fork, a destructive or irreversible action, missing credentials or access.

Everything else: state your assumption in one line and keep going.

## Rules

- Never ask "want me to continue?". Report at the end, or when you truly need the user.
- While a review is running, do not start work that depends on its result. Read-only prep is fine. Skip a reviewer only when it FAILED, never because it's slow.
- A failed reviewer does not stop unrelated work. Retry once. Then report the failure and never claim that review passed.
- Never replace a job that is still running.
- Watchdog: only on hosts where finished subagents do NOT wake the main thread on their own. There, if you have a loop or scheduled-wakeup feature, arm one (e.g. `/loop 10m continue the fullsend job`) to pick up finished subagents and dispatch the next stage. Stop it after the final report. On hosts with completion wakeups (e.g. T3 Code), do not poll.
- If you have a notification skill, notify the user when the job finishes or blocks on them.
