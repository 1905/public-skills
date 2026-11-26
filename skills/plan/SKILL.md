---
name: plan
description: "Create a versioned implementation plan from an approved feature spec, then execute it on a feature branch and close the feature out. Use before dispatching implementers or writing code."
---

# Plan — versioned task breakdown and execution

## Overview
Stages 3-5 of `idea → spec → plan (versioned) → exec → done`. Turns the spec's file-level table into small tasks (2-5 min each for a subagent), runs them, and closes the feature.

Expects an approved `plans/<feature-dir>/spec.md` from the `spec` skill. No approved spec → run the `spec` skill first. Not installed → ask the user for the requirements, write a `spec.md` with at least `## TL;DR`, `## Goals`, `## File-level changes`, `## Tests`, and get it approved.

**Format:** follows the spec. HTML spec → `plan-vX.Y.html`, same structure.

**Versioning (hard rule):** every plan revision is a NEW file, never an overwrite.
- `plan-v1.0.md` — first draft
- `plan-v1.1.md` — after review fixes / small scope tweaks (minor bump)
- `plan-v2.0.md` — redesign or major scope change (major bump)
- The superseded file gets `**Status:** superseded by v<X.Y>`. Only one file is current.
- A new version starts as `draft`.

**Statuses:** `draft` → (`reviewed`, only when an independent review ran) → `approved` → `in-progress` → `done`. Update the status line the moment a stage completes.

If the host is in a plan or read-only mode that blocks file writes, ask the user to switch modes before you start.

## Who writes the draft

A subagent writes the first draft. See `delegation.md` next to this file for how to dispatch.

- **Default writer:** Opus (the newest you have, e.g. Opus 5.5). No Opus → the current session model; say so.
- **On request only:** Gemini 4 Neon (`xhigh`), Fable 5.2, Astra 6.2. Never pick Fable 5.2 or Astra 6.2 on your own.
- **Effort:** `xhigh`, or the highest the host can set. An explicit request wins.
- A model the user named is unavailable → report it and ask. Do not fall back on your own.
- Brief: feature dir, approved spec path, required structure (below), allowed edits. Ask it to write the file and return its path and task headers. Tell it to start no subagents.
- Later versions and review fixes use the current session model.
- When presenting for approval, say which model wrote the draft, or that it is unverified.
- No subagent tool available → write the draft in the main thread.

## Steps

1. **Write `plans/<feature-dir>/plan-v1.0.md`**, header:
   - `# <Title> Implementation Plan v1.0`
   - `**Date:**` / `**Status:** draft` / `**Spec:** ./spec.md`
   - `**Goal:**` one sentence · `**Architecture:**` 2-3 sentences · `**Tech Stack:**` key libs
   - Banner: `> For agentic workers: implement task-by-task. Checkbox syntax for tracking.`
2. **File map** before tasks: exact paths grouped Modify / Create / Out-of-scope.
3. **Tasks.** Each task has an id (`T1.1`, `T1.2`, …). Per task: Files (Create/Modify/Test exact paths), then checkbox steps — failing test first, exact runnable commands with expected output, implement, verify pass. (The orchestrator commits; see Exec loop.)
   - **Lock interfaces, names, signatures and test expectations. Do NOT embed full code bodies.** Implementers write the code; TDD keeps them honest.
   - Tag each task:
     - `heavy` — creates or edits code or config. Implementer: Opus 5.5 (no Opus → the strongest coding model you have; never a small or fast model). Not Fable 5.2 unless the user asks.
     - `light` — read-only work that changes no file: screenshots, summaries of logs, docs or changelogs, counts, dry runs. A Sonnet-class model is fine. It runs and reports; it never edits code, commits, calls paid APIs, or touches data, devices or infrastructure.
     - `gate` — a check the orchestrator runs itself (build, test suite, smoke check). Nothing after it starts until it passes.
     - Unsure whether a task writes or matters → `heavy`.
   - Add a "baseline sanity check" `gate` before Task 1: build and tests are green before any change. Red baseline → STOP and report. Do not fix unrelated failures on your own.
   - Type-consistency check at the end: a name in Task 3 must match Task 7.
4. **Self-review, fix in place:** every spec requirement maps to a task; no placeholders ("TODO", "similar to Task N"); names consistent across tasks; no arbitrary phase boundaries.
5. **Language pass.** If you have a controlled-language or plain-English skill, run it on the plan: one run per plan file, right before approval, in strict mode (plans are instructions for agents). Apply its findings in that run. No second run after later edits. In the approval message say whether it ran and what it left unfixed. No such skill → skip and say so.
6. **No automatic model review.** Self-review and the language pass are the default checks. Run an independent read-only review only when the user asks:
   - Ask the reviewer for a 1-10 score and findings. Show its full output verbatim in a fenced block. One round only. Verify each finding before a fix. A failed review is reported as failed.
   - Set `**Status:** reviewed`. Fixes needed → put them in a new minor version (`draft`) that supersedes the reviewed one. A clean review needs no new version.
   - `/hill-climb` on a plan: first copy the current version to the next minor version (`draft`), mark the old one superseded, and give hill-climb the new file. All rounds edit that one file.
7. **User approval.** Present the current version path, the task headers, the language-pass result, and the review verdict if one ran. If you have a notification skill, notify the user that an approval is waiting. STOP until approved.
   - Approved → `**Status:** approved`.
   - Changes requested → cut a new minor version, supersede, re-present.
8. **Exec.**
   1. **Preconditions (hard gate):**
      - The project is a git repository. If not → STOP and ask.
      - Base branch = the branch the project docs name; else the remote default (`git symbolic-ref --short refs/remotes/origin/HEAD`); else `main` or `master`, whichever exists.
      - You are on the base branch. The tree is clean, except files under `plans/`.
      - Any other dirty file, or another branch → STOP and ask the user (offer: commit, or switch branch). Never stash on your own.
   2. Create the feature branch: `git checkout -b <branch> <base>`. One feature = one branch. Never implement directly on the base branch.
   3. Set `**Status:** in-progress`. Commit `plans/<feature-dir>/` as the first commit on the branch. If `plans/` is ignored by git, skip this commit and say so.
   4. Run the **Exec loop** (below) for every task, in plan order.
   5. Build and test where the project's own docs say to. Never point tests at a production database.
   6. No per-task model review. The orchestrator verifies each task (diff + task tests) and each rollout phase (full build + tests), and runs every `gate` task.
   7. **Branch review.** One independent read-only review of the whole branch at the end, with an explicit baseline (`git diff <base>...HEAD`) and file scope. Verify each finding against the code. Fix confirmed issues. Re-run build + tests. Commit.
9. **Reconcile spec.** Update spec.md to match what shipped — deviations, dropped goals, files that turned out different. Put drift under `## As-built notes` rather than silently rewriting history.
10. **Done.** Set `**Status:** done` in the current plan file, `mkdir -p plans/done`, then move the whole feature dir: `git mv plans/<feature-dir> plans/done/` (plain `mv` if the dir is not tracked). Commit if tracked.
11. **Hand over.** Report: branch, commits, test results, review result, open items. Push, PR and merge follow the user's instructions. No instruction → do not push or merge; ask.

## Exec loop

Per task, in plan order, one implementer at a time:

1. Mark the task in progress in the host's todo list, if it has one.
2. Dispatch the implementer (model per the task's tag). Paste the FULL task text into the brief; do not make it read the plan file. Add repo root, branch, the files it may edit and the commands it may run. Tell it: do not commit; end with `DONE`, `DONE_WITH_CONCERNS`, `BLOCKED` or `NEEDS_CONTEXT`.
3. Validate it yourself: read the diff against the task and run the task's tests. Problems → send the fixes back to the same implementer. Its own check does not replace yours.
4. Commit (orchestrator only), conventional style: `feat(scope): …`, `fix(scope): …`, `test(scope): …`.
5. Mark the task done. Run any `gate` that follows.

- `DONE_WITH_CONCERNS`: a reasoned deviation → accept it and note it for step 9. A feature switched off or a test weakened to pass → dispatch again.
- `BLOCKED` / `NEEDS_CONTEXT`: missing context → give it, same model. Plan problem → see Smell-checks.
- The orchestrator writes no feature code while a subagent tool exists. Never move on with a known defect.

## Smell-checks
- Plan introduces a file the spec didn't mention → the spec is wrong; update spec.md first.
- A task needs an unexpected step mid-exec → STOP the task. Cut a new minor version, set it `in-progress`, supersede the old one. Inside the approved scope → continue and name it in the final report. Scope change → user approval first.
- More than 3 fix loops on one task → task too big or spec wrong; split it.
