# public-skills

Four agent skills for planned, reviewed feature work: write a spec, plan it, build it on a branch, and have independent models review it.
They are written for Claude Code and work in other hosts that read `SKILL.md` files.

| Skill | What it does | You get |
|---|---|---|
| [`spec`](skills/spec/SKILL.md) | Turns an idea into `plans/YYYY-MM-DD-<feature>/spec.md` after a short Q&A. | A spec that starts with a TL;DR. You approve the TL;DR. |
| [`plan`](skills/plan/SKILL.md) | Turns an approved spec into a versioned plan of small tasks, runs them on a feature branch, has the branch reviewed, and closes the feature. | A feature branch with one commit per task. No push, no merge unless you say so. |
| [`hill-climb`](skills/hill-climb/SKILL.md) | Three independent models review the same target and give it a score. Confirmed findings get fixed. Repeats until all three give 9/10 or the round limit. | A better target and a score table per round. |
| [`fullsend`](skills/fullsend/SKILL.md) | Runs spec → plan → implement → test → review → simplify → close-out with no check-ins. | A finished feature branch and a report. |

## Install

```sh
git clone https://github.com/1905/public-skills.git
mkdir -p ~/.claude/skills
for s in spec plan hill-climb fullsend; do
  if [ -e "$HOME/.claude/skills/$s" ] && [ ! -L "$HOME/.claude/skills/$s" ]; then
    echo "exists: $s — move it first"; continue
  fi
  ln -sfn "$PWD/public-skills/skills/$s" "$HOME/.claude/skills/$s"
done
```

- **Check:** start a new session and ask the agent to list its skills.
- **Update:** `git -C public-skills pull`. The symlinks pick up the change.
- **Uninstall:** delete the four symlinks in `~/.claude/skills/`.
- **Per project:** link or copy into the project's `.claude/skills/` instead.
- **Other hosts:** use that host's skills folder (e.g. `~/.agents/skills/` or `~/.codex/skills/`).
- Each skill directory is self-contained. It carries its own copy of `delegation.md`, so you can copy one skill alone. `fullsend` needs `spec` and `plan`.

## Make them behave as designed: add rules to CLAUDE.md

Much of how these skills behave for the author comes from global rules, not from the skill files. Examples: approve the TL;DR, never commit to the base branch, Opus for code.

Copy the block in [`CLAUDE.snippet.md`](CLAUDE.snippet.md) into `~/.claude/CLAUDE.md` or your project's `CLAUDE.md`. Fill in your base branch, build command and test command. Keep the `[essential]` lines. Choose from the `[optional]` ones.

## Usage

```text
/spec add CSV export to the reports page
spec with Fable 5.2: rework the auth retry logic
/plan                                   # after you approve the spec
/hill-climb src/auth "no data loss on retry"
/hill-climb heavy plans/2026-11-26-csv-export/plan-v1.0.md rounds 2 score 8
fullsend. add CSV export to the reports page
```

## Workflow and files

```
/spec  → you approve the TL;DR
/plan  → you approve the plan → it runs on a feature branch → branch review → close-out
/hill-climb <target>   any time you want a hard review
/fullsend              the whole pipeline, no check-ins
```

```
plans/
  2026-11-26-csv-export/
    idea.md            Status: draft → done
    spec.md            Status: pending review → approved
    plan-v1.0.md       Status: superseded by v1.1
    plan-v1.1.md       Status: draft → (reviewed) → approved → in-progress → done
  done/                finished feature dirs move here
```

- The `plans/` files stay uncommitted until exec starts. Then they are the first commit on the feature branch.
- If `plans/` is gitignored, the skills skip those commits and say so.
- If your CLAUDE.md asks for HTML specs and plans, the files are `spec.html` and `plan-vX.Y.html` with the same structure.

## Models

Model names are current as of November 2026.

| Role | Default | Notes |
|---|---|---|
| Spec and plan drafts | Opus 5.5 | Gemini 4 Neon, Fable 5.2 or Astra 6.2 only when you name them. Plans at `xhigh` effort. |
| Implementers (`heavy` tasks) | Opus 5.5 | Never a small or fast model. |
| Read-only tasks (`light`) | Sonnet-class | Changes no file. |
| hill-climb, normal | Opus 5.5 + Sol 6.2 + Gemini 4 Neon | Missing model → closest one you have, named in the report. |
| hill-climb, heavy | Fable 5.2 + Astra 6.2 + Gemini 4 Neon, all `xhigh` | Any heavy model missing → the whole council falls back to normal. |

## Host support

| | Claude Code alone | Claude Code + T3 Code | Other hosts |
|---|---|---|---|
| Subagents | native `Agent` tool | `delegate_task` with exact model and effort per child | native subagent tool, if any |
| `spec`, `plan` | ✓ | ✓ | ✓ (main thread if no subagents) |
| `hill-climb` | runs as `degraded council (one provider)`: three different Claude models | full council across providers | stops with `council unavailable` without subagents |
| `fullsend` | ✓ | ✓ | ✓ |

T3 Code is an agent orchestrator that can start child agents on other providers and models. Nothing breaks without it. It only makes model and effort selection exact.

## Optional companions

| Companion | Used by | Without it |
|---|---|---|
| Brainstorming skill (e.g. `superpowers:brainstorming`) | `spec` step 2 | `spec` asks its own questions. |
| Controlled-language / plain-English skill | `plan` step 5 | Skipped; the approval message says so. |
| `/simplify` | `fullsend` step 6 | `fullsend` does one cleanup pass itself. |
| `/loop` or scheduled wake-ups | `fullsend` watchdog | No watchdog. |
| Notification skill | approvals, finished jobs | No notifications. |

## Cost and autonomy

- ⚠ `hill-climb` runs up to 9 model reviews (3 rounds × 3 reviewers) plus retries. Heavy mode uses the top models at `xhigh`. That can cost a lot.
- ⚠ `fullsend` commits on a feature branch without asking. If the repo has a remote, it pushes the feature branch once at the end. It never pushes to the base branch, never force-pushes and never merges unless you ask.
- `fullsend` stops only for: a safety issue, a decision only you can make, missing credentials, or a failed precondition (no git repo, dirty tree, wrong branch, red baseline build).

## Troubleshooting

| Message | Cause | Fix |
|---|---|---|
| `council unavailable` | Fewer than three different models can run, or no subagent tool. | Add a provider, or allow a one-provider council (don't use `strict council`). |
| `target changed` | A file changed while reviewers were reading it. | Don't edit the target during a round. Run again. |
| Precondition stop in `plan` | Not a git repo, dirty tree, or not on the base branch. | Commit or switch branch, then run again. |
| Model unavailable | A model you named isn't in your catalog. | Name another model, or drop the request to use the default. |

## Known issue: `/plan` name

Some Claude Code versions may have a built-in `/plan` command that takes precedence over the `plan` skill. This hasn't been verified. If `/plan` doesn't start this skill:

1. Rename `skills/plan/` (e.g. to `feature-plan`).
2. Change the `name:` field in its `SKILL.md`.
3. Update the references in `skills/spec/SKILL.md`, `skills/fullsend/SKILL.md`, every `delegation.md`, and this README.

## License

MIT
