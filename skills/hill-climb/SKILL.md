---
name: hill-climb
description: "Improve a target through repeated rounds of three independent model reviews: score, verify findings, fix, repeat. Normal council: Opus 5.5 + Sol 6.2 + Gemini 4 Neon. Heavy: Fable 5.2 + Astra 6.2 + Neon, all xhigh. Normal mode uses each model if available, else the closest one you have; heavy mode falls back to normal. Use for hill climb, hill-climb, heavy hill climb, council review, or requested review-and-fix rounds. Do not start a council when the request is only to inspect or edit this skill."
argument-hint: "[heavy] <target: path | diff | feature> [goal] [rounds N] [score N] [effort LEVEL]"
metadata:
  version: "1.0.0"
---

# hill-climb

Three independent reviewers score the same target. Verify their findings, fix confirmed problems, and repeat within the requested limits.

Input: `$ARGUMENTS` and the user's request.

## 1. Resolve the request

- **Target:** files, a directory, a named feature, or an explicitly scoped diff. Use the target already set in the conversation when there is one.
- No identifiable target → return `usage: /hill-climb [heavy] <target> [goal] [rounds N] [score N] [effort LEVEL]`.
- **Goal:** the user's goal, or the target's stated requirements. State it briefly. Do not ask for an answer already given.
- **Rounds:** three by default. `rounds N` sets another limit, higher or lower. For a PR, count all rounds across new commits and base changes.
- **Early stop:** end when all three reviewers score the same snapshot ≥ 9/10 (or the requested `score N`).
- **Mode:** normal unless the user explicitly asks for `heavy`.

## 2. Pick the council

Use three reviewers from **different model families or providers**. Different models miss different things; three copies of one model mostly agree with each other.

| Mode | Claude reviewer | Codex reviewer | Gemini reviewer |
|---|---|---|---|
| Normal | Opus 5.5, `high` | Sol 6.2 (`gpt-6.2-sol`), `high` | Gemini 4 Neon, `xhigh` |
| Heavy | Fable 5.2, `xhigh` | Astra 6.2 (`gpt-6.2-astra`), `xhigh` | Gemini 4 Neon, `xhigh` |

**Normal mode:** use each model **if available** to you. If one is not:
- Use the strongest model you have from the same provider (e.g. another Claude model for Opus 5.5).
- No access to that provider at all → use the strongest model from another provider you have, so the council keeps three different models where possible.
- Name every substitution in the report. Never present a substitute as the model in the table.

**Heavy mode:** no substitutions. All three heavy models must run at `xhigh`, or the whole council falls back (see Heavy fallback).

The user can name models in the request; those win.

Rules:
- Do not pick heavy mode just because a task looks hard.
- An explicit `effort LEVEL` changes only the normal-mode Claude and Codex reviewers. Neon, when used, stays at `xhigh`. A substitute for Neon uses its own highest effort. Heavy mode ignores `effort LEVEL` (always `xhigh`); say so if the user gave one.
- Hosts with a model catalog (e.g. T3 Code):
  - Copy exact model IDs from the catalog. Display names are not model IDs. Neon can be on several providers (e.g. Antigravity, OpenCode, OpenRouter); pick one that can run child tasks.
  - Set effort through the advertised option (e.g. `effort`, `reasoningEffort`, `thought_level`), not through prompt text. Never silently lower a requested effort.
  - Check the provider and model each task reports. A mismatch is a failed review; never accept its score.
- Hosts without a catalog (native subagent tools): pass the model through the tool's own model parameter, if it has one. If you can't select a model or effort, or the tool doesn't report the model that ran, say so in the report. That alone does not fail the review.

### Dispatch

See `delegation.md` next to this file.
- T3 Code: one `delegate_task` per reviewer, `mode: "async"`, `role: "review"`, explicit `target.providerInstanceId`, `target.model`, `target.options`.
- No T3: use the host's native subagent tool with an explicit model per reviewer. If the host can't select three distinct models, say so in the report.
- Never run the reviews in the main thread and call them independent.

### Heavy fallback

If Fable 5.2, Astra 6.2 or Gemini 4 Neon is unavailable or can't run at `xhigh`, switch the **whole council** to normal mode (Opus 5.5 + Sol 6.2 + Neon, with normal-mode substitutions) and say which requirement was missing. Do not mix heavy and normal reviewers. Do not compare scores across councils.

A timeout alone does not mean a model is unavailable — keep waiting on that task.
If fewer than three distinct reviewers can run at all, stop with `council unavailable`. Never pass with fewer than three valid reviews.

## 3. Run the rounds

Make a private run directory, e.g. `/tmp/hill-climb-<slug>-<timestamp>/`. Keep snapshots and review outputs out of tracked files.

For each round:

1. **Snapshot the target.** Record file paths and contents, including untracked target files. For a repo, also record HEAD and the scoped diff.
2. **Launch three fresh reviews** in parallel. Each gets a unique request ID and a title with run, mode, round and model. Never reuse a child thread for a new round.
3. **Keep the target unchanged** until all three finish.
4. **Wait for results.** Follow the tool's completion notice. Do not build sleep loops, poll loops or watcher agents. Never start a duplicate because a task is slow.
5. **Parse all three.** Each needs an integer `SCORE` 1-10 and findings for this snapshot.
   - If the target changed during review, stop with `target changed`. Mixed-snapshot scores are invalid.
   - Retry a failed or malformed review once with a fresh task. If the retry fails, record `n/a` and leave the council score blank. Still verify and fix the findings from the valid reviews, then continue to the next round. A round with `n/a` can't trigger the early stop.
6. **Score the round:** the minimum of the three scores. Save all outputs and the exact model selections.
7. **Verify and fix.** Check each finding against the code before acting. Apply confirmed fixes, including from the last round. Reject false positives with a one-line reason. Run focused tests.
8. **Stop** at the early-stop score or the round limit. Final fixes need tests even when the review budget is spent.

If the user stops the run or a prerequisite fails, stop with that reason. Before cleanup, cancel only tasks still active; keep finished results.

## 4. Reviewer brief

Send this as the task, with every placeholder filled:

```text
You are one of three independent council reviewers. Do not consult the other reviewers.

Goal: <goal and acceptance criteria>
Target: <absolute paths, or scoped diff command and repo root>
Snapshot: <snapshot identifier and files to review>
Mode: <normal or heavy>. Your model: <exact model ID>. Effort: <effort>.
Round <r> of <rounds>. Pass mark: <pass>/10.
Validation already run: <commands, results, and limits>
Previous findings and responses: <confirmed fixes, rejected findings with reasons, unresolved objections; none in round 1>

Rules:
- Read-only. Do not edit, create, move, or delete files. Do not commit or start subagents.
- Do not run builds or commands that mutate files. Read the supplied validation evidence and flag gaps.
- Score the target against the goal, 1-10. 10 means nothing worth changing. 9 means only minor nits remain.
- Give 8 or lower when an issue materially affects the goal.
- Each finding needs a severity, file:line or exact section, evidence, and a concrete fix.
- Stay within the goal. Do not repeat rejected findings without new evidence.

Reply in this format:
SCORE: <integer 1-10>
VERDICT: <one sentence>
FINDINGS:
1. [critical|high|medium|low] <file:line> — <problem and evidence> → <fix>
Use "FINDINGS: none" when there are no findings.
```

## 5. Report

- Stop reason, requested mode, effective mode, and any fallback reason.
- All three actual models and effort levels.
- One row per round:

| Round / mode | Claude model / score | Codex model / score | Gemini model / score | Council score | Changes |
|---|---|---|---|---|---|

After a substitution from another provider, rename that column to the provider that actually ran.

- Confirmed findings still open, notable false positives, validation limits.
- Reviewed commit and final commit.
- Never invent scores. An incomplete council is not a pass, even when every available score reaches the target.
