---
name: spec
description: "Use when starting non-trivial feature work or a proper multi-file bugfix (\"let's work on…\", \"build X\", \"fix Y properly\") — before any implementation plan or code exists."
---

# Spec — idea → design doc

## Overview
Stages 1-2 of the pipeline `idea → spec → plan (versioned) → exec → done`. All artifacts live in the **project root** under `plans/`, one dir per feature:

```
plans/
  YYYY-MM-DD-<feature>/   # feature = short kebab-case slug you pick
    idea.md
    spec.md
    plan-v1.0.md        # written by /plan, never by /spec
    plan-v1.1.md
  done/                 # finished features move here wholesale
```

If a dir for the same in-flight effort already exists, continue in it. Otherwise make a new dir (the date tells repeat attempts apart).

**Migrate-on-touch:** if the repo has legacy plan files (loose `PLAN.md`/`*_PLAN.md`/`TODO.md` at root, undated `plans/*.md`), offer the user a one-off sweep into the layout above. Show a dry-run report first: live → dated dir, finished → `plans/done/`, stale → `plans/done/superseded/`, permanent docs → `docs/`. Never migrate silently.

Every file carries a `**Status:**` line. Update it the moment a stage completes. Never leave it stale.

## Who writes the draft

A subagent writes the first draft, so the main thread stays free for questions and approval. See `docs/delegation.md` in this repo for how to dispatch.

- Default writer: the strongest model you have. The user can name another model or effort ("spec with model X, high effort").
- Resolve the exact model ID from the live catalog. Do not silently replace a requested model or effort. If it's unavailable, say so.
- Give the child a complete brief: feature dir, repo root, confirmed requirements, required sections (below), allowed edits. Ask it to write `idea.md` and `spec.md` and return the path plus the `## TL;DR` section. Tell it to start no subagents.
- The drafting child does the first self-check.
- Later edits and review fixes use the current session model, in the main thread.
- When presenting for approval, say which model wrote the draft.
- No subagent tool available → write the draft in the main thread.

## Steps

1. **idea.md.** Capture the raw idea before shaping it: 3-10 lines — what the user asked for, why now, first-guess scope. Header: `**Date:** YYYY-MM-DD`, `**Status:** draft`. When the brainstorm below confirms intent, set `**Status:** done`.
2. **Brainstorm.** One question at a time, multiple-choice when possible. Grep the codebase BEFORE asking — the answer may already be in the repo. Grep findings become the file:line citations in the spec's Problem(s). If the request already pins purpose, constraints and success criteria, confirm your reading in one message instead of a full brainstorm. Do not propose a design until all three are clear.
3. **spec.md** with exactly these sections:
   - `# Title` + `**Date:**` / `**Scope:** <project path>` / `**Status:** pending review`
   - `## TL;DR` — FIRST section, and the only one the user must read before approving. One block per feature/phase, each ≤5 lines: **what** changes (one sentence, plain words), **why** (the failure it fixes), **what the user must decide or do** (rotations, approvals, data — or "nothing"), **what it does NOT do**. Four phases → four blocks. A user who reads only this section must not be surprised later by what got built.
   - `## Problem(s)` — numbered; 2-4 sentences each + file:line citation
   - `## Goals` — numbered, terse; each traces to a problem
   - `## Non-goals` — things you'll be tempted to do but won't
   - `## <Domain section>` — one or more, named for the feature (e.g. "Theming pipeline"); data shapes as JSON examples, flows as ASCII diagrams
   - `## File-level changes` — table: file path → 1-3 sentence change (the plan explodes this into tasks)
   - `## Tests` — unit / integration / manual, grouped by file or behaviour
   - `## Failure modes & decisions` — table: failure → behaviour
   - `## Out of scope` — explicit list
   - `## Rollout` — phases P1, P2…, one line each; each phase = one commit gated on clean review
4. **Self-review, fix in place** (one pass, no loop): no TBD/TODO placeholders; sections don't contradict; scoped to ONE plan (split if not); no requirement readable two ways. A truly unresolvable ambiguity is a brainstorm question — ask it, don't guess.
5. **User approval.** Present the spec path and paste the `## TL;DR` section VERBATIM in chat. It is the approval surface. STOP until the user approves.
   - Approved → `**Status:** approved`, hand off to `/plan`.
   - Edits requested → fix spec.md in place (no versioning at spec stage; still `pending review`).
   - Scope change → back to brainstorming.
   - If the user later says "I thought we were only building X", the TL;DR was wrong. Fix the process, not the user.

## Smell-checks
- User replies with corrections ("no, also do X") → back to brainstorming; don't silently absorb scope creep.
- Spec needs >1 plan → split into multiple feature dirs.

## Style
Lead with the failure, then the fix. File:line citations everywhere. Tables for multi-row decisions. "Why" lines for non-obvious choices. Keep "Out of scope" honest. Plain, short sentences.
