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
    plan-v1.0.md        # written by the plan skill, never by spec
    plan-v1.1.md
  done/                 # finished features move here wholesale
```

If a dir for the same in-flight effort already exists, continue in it. Otherwise make a new dir (the date tells repeat attempts apart).

**Migrate-on-touch:** if the repo has legacy plan files (loose `PLAN.md`/`*_PLAN.md`/`TODO.md` at root, undated `plans/*.md`), offer the user a one-off sweep into the layout above. Show a dry-run report first: live → dated dir, finished → `plans/done/`, stale → `plans/done/superseded/`, permanent docs → `docs/`. Never migrate silently. Commit an accepted sweep on its own, before any spec work, on the branch the user names.

Every file carries a `**Status:**` line. Update it the moment a stage completes. Never leave it stale.

These files stay uncommitted until the plan skill's Exec step commits them on the feature branch.

If the host is in a plan or read-only mode that blocks file writes, ask the user to switch modes before you start.

## Who writes the draft

The main thread writes `idea.md` and runs the brainstorm. A subagent writes the first `spec.md` draft, so the main thread stays free for questions and approval. See `delegation.md` next to this file for how to dispatch.

- **Default writer:** Opus (the newest you have, e.g. Opus 5.5). No Opus → the current session model; say so.
- **On request only:** Gemini 4 Neon (`xhigh`), Fable 5.2, Astra 6.2. Never pick Fable 5.2 or Astra 6.2 on your own.
- **Effort:** the session's effort. An explicit request wins.
- A model the user named is unavailable → report it and ask. Do not fall back on your own.
- Brief: feature dir, repo root, path to `idea.md`, the requirements confirmed in the brainstorm, the required sections (below), allowed edits. Ask it to write only `spec.md` and return the path, the `## TL;DR` section, and a list of open questions it could not resolve. Tell it to start no subagents.
- The drafting child does the first self-check (step 4). The main thread asks the child's open questions, then fixes `spec.md`.
- Later edits and review fixes use the current session model, in the main thread.
- When presenting for approval, say which model wrote the draft, or that it is unverified.
- No subagent tool available → write the draft in the main thread.

## Steps

1. **idea.md** (main thread). Capture the raw idea before shaping it: 3-10 lines — what the user asked for, why now, first-guess scope. Header: `**Date:** YYYY-MM-DD`, `**Status:** draft`.
2. **Brainstorm** (main thread). If you have a brainstorming skill (e.g. `superpowers:brainstorming`), use it for this step.
   - One question at a time, multiple-choice when possible.
   - Grep the codebase BEFORE asking — the answer may already be in the repo. Grep findings become the file:line citations in the spec's Problem(s).
   - When the design forks, show 2-3 approaches with trade-offs and name the one you recommend.
   - If the request already pins purpose, constraints and success criteria, confirm your reading in one message instead of a full brainstorm.
   - Do not propose a design until purpose, constraints and success criteria are clear. Then set `idea.md` to `**Status:** done`.
3. **spec.md** (drafting subagent) with exactly these sections:
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
   - `## Rollout` — phases P1, P2…, one line each. Each phase is a group of plan tasks that ends with a green build and tests. One independent review of the whole branch runs at the end, not per phase.
4. **Self-review, fix in place** (one pass, no loop): no TBD/TODO placeholders; sections don't contradict; scoped to ONE plan (split if not); no requirement readable two ways. A truly unresolvable ambiguity is a brainstorm question — ask it, don't guess.
   - No model review of the spec unless the user asks.
   - No language/plain-English pass on a spec unless the user asks. Write plain, short sentences from the first draft.
5. **User approval.** Present the spec path and paste the `## TL;DR` section VERBATIM in chat. It is the approval surface. If you have a notification skill, notify the user that an approval is waiting. STOP until the user approves.
   - Approved → `**Status:** approved`, hand off to the `plan` skill. No `plan` skill installed → stop here; tell the user the spec is approved and ask whether to commit `plans/<feature-dir>/`.
   - Edits requested → fix spec.md in place (no versioning at spec stage; still `pending review`).
   - Scope change → back to brainstorming.
   - If the user later says "I thought we were only building X", the TL;DR was wrong. Fix the process, not the user.

## Smell-checks
- User replies with corrections ("no, also do X") → back to brainstorming; don't silently absorb scope creep.
- Spec needs >1 plan → split into multiple feature dirs.

## Style
Lead with the failure, then the fix. File:line citations everywhere. Tables for multi-row decisions. "Why" lines for non-obvious choices. Keep "Out of scope" honest. Plain, short sentences.
