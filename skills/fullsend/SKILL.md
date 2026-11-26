---
name: fullsend
description: "Run a feature end to end with no check-ins: spec → plan → implement → test → review → simplify → close out → report. Use when the user says \"fullsend.\", \"fullsend\", \"full auto\", or \"do it all\"."
argument-hint: "<feature or task>"
---

# fullsend.

The user hands over the whole feature. Run every stage yourself and report at the end.
This skill uses the `spec` and `plan` skills; install them too.

No feature identifiable from the request → ask once.
A fix under ~10 lines → skip spec and plan: branch, fix, test, review, report.

## Pipeline

0. **Preflight** — before anything else: the `spec` and `plan` skills are installed, the project is a git repository, you are on the base branch, and the tree is clean (`plan` step 8.1). Any failure → STOP and say what is missing.
1. **Spec** — follow the `spec` skill. Replace its approval stop with its self-review, then set `**Status:** approved`. Ask a brainstorm question only if the request forks into truly different products.
2. **Plan** — follow the `plan` skill, steps 1-5. Replace its approval stop with its self-review, then set `**Status:** approved`.
3. **Implement** — follow the `plan` skill's step 8, sub-steps 1-6 (preconditions through per-task verification). Do not run its branch review (8.7) here; step 5 below does that.
4. **Test** — run the project's full build and test suite where the project's docs say to. Red → fix and re-run, at most 3 loops, then stop and report. No test suite → run build, lint or typecheck and say tests are missing.
5. **Review** — one independent read-only review of the whole branch diff (`git diff <base>...HEAD`) by a subagent, or `/hill-climb` if the user asked for it. Verify each finding. Fix confirmed issues. Skip false positives with a one-line note. Re-run build + tests. Commit.
6. **Simplify** — run `/simplify` on the diff if you have it, otherwise do one cleanup pass yourself. Skip if the project opts out. Re-run build + tests. Commit.
7. **Close out** — `plan` skill steps 9-10: reconcile the spec, set `done`, move the feature dir to `plans/done/`. Commit.
8. **Report** — what shipped, branch and commits, test results, review outcome, every assumption, anything skipped.

Commit after each task and after steps 5, 6 and 7.
Push follows the user's instructions. No instruction → push the feature branch once, at the end, if the repo has a remote, and say so in the report. Never push to the base branch. Never force-push. Do not merge unless the user asked.

## Stop only for

- A real safety issue.
- A decision only the user can make: a requirements fork, a destructive or irreversible action, missing credentials or access.
- A failed precondition: skill missing, no git repository, dirty tree, wrong branch, or a red baseline build.

Where `spec` or `plan` says STOP or "ask the user" for something not in this list: do not stop. Take the conservative option, write the assumption in one line, and list it in the final report. Skip `spec`'s migrate-on-touch sweep.

## Rules

- Never ask "want me to continue?". Report at the end, or when you truly need the user.
- While a review is running, do not start work that depends on its result. Read-only prep is fine. Skip a reviewer only when it FAILED, never because it's slow.
- A failed reviewer does not stop unrelated work. Retry once. Then report the failure and never claim that review passed.
- Never replace a job that is still running.
- Watchdog: for a multi-phase job, if the host has a loop or scheduled wake-up feature, arm one at the start (e.g. `/loop 10m continue the fullsend job`). On each wake-up: if a job or review is RUNNING, do nothing. Otherwise pick up finished results, fix verified findings, start the next phase, or get past a stall (retry once, or state an assumption). It never polls a running task and never starts a duplicate. Stop it after the final report.
- If you have a notification skill, notify the user when the job finishes or blocks on them.
