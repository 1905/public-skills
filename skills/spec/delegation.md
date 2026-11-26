# Delegating to subagents

The `spec`, `plan`, `hill-climb` and `fullsend` skills hand some work to subagents.
This file says how. Each skill directory has an identical copy, so a skill works when installed alone.

## Pick the tool

1. **T3 Code available** (`delegate_task` tool exists): use it. It can pick a provider, an exact model and an effort level per child.
2. **Otherwise:** use your host's native subagent tool (for example the Claude Code `Agent` tool, or Codex `spawn_agent`).
3. **No subagent tool at all:** do the work in the main thread and say so.

Never claim a review was independent when the main thread did it.

## With T3 Code

1. Discover `orchestrator_capabilities`, `delegate_task`, `task_status`, `task_cancel` and any wait tool. Read their live schemas.
2. Call `orchestrator_capabilities`. Pick an enabled provider instance that advertises the exact model you need.
3. Copy the exact model ID from the catalog. Display names are not model IDs.
4. Set effort through `target.options`, using the option ID and value the catalog advertises. A prompt cannot set effort.
5. Call `delegate_task` with a full `task` brief, a short `title`, a `role` (`review` for reviews, `general`/`implementation`/`test` for jobs) and a unique `clientRequestId`.
6. Prefer `mode: "async"`. Record `taskId`, `childThreadId`, `childRunId`.
7. Check the provider and model the result reports. A mismatch is a failed task.

Follow the result's `next` instruction. When completion wakes the parent, do not poll or sleep-loop.

## With a native subagent tool

Native tools usually have no model catalog, no per-child effort option and no report of the model that ran.

- Pass a model only through the tool's own model parameter, if it has one. Use the values that parameter accepts.
- If the tool can't select the model or effort you need, say so in your report. Do not pretend you selected it.
- If the tool reports no model, state that the executed model is unverified. Do not fail the task for that reason alone.
- Run independent subagents in parallel when the tool allows it.

## Write a complete brief

Children do not see the parent conversation. Every brief includes:

- Goal and acceptance criteria.
- Absolute paths, repo root, branch, and the exact diff baseline or snapshot.
- Decisions already made, and constraints.
- What the child may edit and run. For reviews: "Read-only. Findings only."
- Expected output format.
- "Do not start further subagents."

`role: "review"` is not a sandbox. The brief must forbid edits, file-writing builds, commits and deploys.
Do not let two parallel writers edit the same files.
Keep credentials out of briefs.
