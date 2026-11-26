---
name: plan
description: "Create a versioned implementation plan from an approved feature spec, before dispatching implementers or writing code."
---

# Plan — versioned task breakdown

## Overview
Stage 3 of `idea → spec → plan (versioned) → exec → done`. Turns the spec's file-level table into small tasks (2-5 min each for a subagent). Expects an approved `plans/<feature-dir>/spec.md` from the `spec` skill.

**Versioning (hard rule):** every plan revision is a NEW file, never an overwrite.
- `plan-v1.0.md` — first draft
- `plan-v1.1.md` — after review fixes / small scope tweaks (minor bump)
- `plan-v2.0.md` — redesign or major scope change (major bump)
- The superseded file gets `**Status:** superseded by v<X.Y>`. Only one file is current.

**Statuses:** `draft` → `reviewed` → `approved` → `in-progress` → `done`. Update the status line the moment a stage completes.

## Who writes the draft

A subagent writes the first draft. See `docs/delegation.md` in this repo for how to dispatch.

- Default writer: the strongest model you have, at high effort. The user can name another model or effort.
- Resolve the exact model ID from the live catalog. Do not silently replace a requested model or effort. If it's unavailable, say so.
- Brief: feature dir, approved spec path, required structure (below), allowed edits. Ask it to write the file and return its path and task headers. Tell it to start no subagents.
- Later versions and review fixes use the current session model.
- When presenting for approval, say which model wrote the draft.
- No subagent tool available → write the draft in the main thread.

## Steps

1. **Write `plans/<feature-dir>/plan-v1.0.md`**, header:
   - `# <Title> Implementation Plan v1.0`
   - `**Date:**` / `**Status:** draft` / `**Spec:** ./spec.md`
   - `**Goal:**` one sentence · `**Architecture:**` 2-3 sentences · `**Tech Stack:**` key libs
   - Banner: `> For agentic workers: implement task-by-task. Checkbox syntax for tracking.`
2. **File map** before tasks: exact paths grouped Modify / Create / Out-of-scope.
3. **Tasks.** Per task: Files (Create/Modify/Test exact paths), then checkbox steps — failing test first, exact runnable commands with expected output, implement, verify pass, commit.
   - **Lock interfaces, names, signatures and test expectations. Do NOT embed full code bodies.** Implementers write the code; TDD keeps them honest.
   - Tag each task `heavy` (real code), `light` (read-only, docs, screenshots) or `gate` (a check that must pass before the next phase).
   - Add a "baseline sanity check" before Task 1: the build and tests are green before any change.
   - Type-consistency check at the end: a name in Task 3 must match Task 7.
4. **Self-review, fix in place:** every spec requirement maps to a task; no placeholders ("TODO", "similar to Task N"); names consistent across tasks; no arbitrary phase boundaries.
5. **Optional language pass.** If you have a plain-English or controlled-language skill, run it once on the plan before approval. Plans are instructions for agents, so one meaning per word matters. Skip it if you don't.
6. **No automatic model review.** Self-review is the default check. Run an independent read-only review (or `/hill-climb`) only when the user asks. If one runs: show its full output, set `**Status:** reviewed`, and put the fixes in a new minor version that supersedes the reviewed one.
7. **User approval.** Present the current version path, the task headers, and the review verdict if one ran. STOP until approved.
   - Approved → `**Status:** approved`.
   - Changes requested → cut a new minor version, supersede, re-present.
8. **Exec.** Preconditions first (hard gate): the working tree must be clean and on the project's base branch. If it's dirty or on another branch, STOP and ask the user.
   - Create the feature branch: `git checkout -b <branch> <base>`. One feature = one branch. Never implement directly on the base branch.
   - Set `**Status:** in-progress`.
   - Dispatch implementers task-by-task (see `docs/delegation.md`). Each brief names the task id, exact files it may touch, and the commands it may run.
   - Build and test where the project's own docs say to. Never point tests at a production database.
   - No per-task model review. The orchestrator verifies each stage itself (build + tests).
   - One independent read-only review of the whole branch at the end, with an explicit baseline (`git diff <base>...HEAD`) and file scope.
9. **Reconcile spec.** Before closing, update spec.md to match what shipped — deviations, dropped goals, files that turned out different. Put drift under `## As-built notes` rather than silently rewriting history.
10. **Done.** Set `**Status:** done` in the current plan file, `mkdir -p plans/done`, then move the whole feature dir: `git mv plans/<feature-dir> plans/done/` (plain `mv` if untracked).

## Smell-checks
- Plan introduces a file the spec didn't mention → the spec is wrong; update spec.md first.
- A task needs an unexpected step mid-exec → STOP, cut a new plan version, re-dispatch. Don't let implementers freelance.
- More than 3 fix loops on one task → task too big or spec wrong; split it.
