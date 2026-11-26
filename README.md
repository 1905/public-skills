# public-skills

> **Agents:** read [TL;DR for agents](#tldr-for-agents) and follow it.

Agent skills for planned, reviewed feature work: write a spec, plan it, build it on a branch, and have independent models review it. Plus Anthropic's `frontend-design` skill for HTML reports and pages.
They are written for Claude Code and work in other hosts that read `SKILL.md` files.

| Skill | What it does | You get |
|---|---|---|
| [`spec`](skills/spec/SKILL.md) | Turns an idea into `plans/YYYY-MM-DD-<feature>/spec.md` after a short Q&A. | A spec that starts with a TL;DR. You approve the TL;DR. |
| [`plan`](skills/plan/SKILL.md) | Turns an approved spec into a versioned plan of small tasks, runs them on a feature branch, has the branch reviewed, and closes the feature. | A feature branch with one commit per task. No push, no merge unless you say so. |
| [`hill-climb`](skills/hill-climb/SKILL.md) | Three independent models review the same target and give it a score. Confirmed findings get fixed. Repeats until all three give 9/10 or the round limit. | A better target and a score table per round. |
| [`fullsend`](skills/fullsend/SKILL.md) | Runs spec → plan → implement → test → review → simplify → close-out with no check-ins. | A finished feature branch and a report. |
| [`frontend-design`](skills/frontend-design/SKILL.md) | Anthropic's design skill: deliberate typography, palette and layout instead of templated defaults. Unchanged copy of the official Claude Code plugin v1.1.1. | HTML reports, pages and UI that don't look generic. |

## TL;DR for agents

You are probably an AI agent installing this for your user. Do this:

1. Clone to a stable path (the symlinks point here; don't use a temp dir):
   `git clone https://github.com/1905/public-skills.git ~/public-skills` (or a path the user names).
2. Dry run: `python3 ~/public-skills/install.py`. It finds every skills folder on this machine:
   - Claude Code: `~/.claude/skills`, and `$CLAUDE_CONFIG_DIR/skills` if set.
   - **T3 Code:** every enabled Claude provider instance with its own config dir (`homePath` or `CLAUDE_CONFIG_DIR` in `~/.t3/userdata/settings.json`) → `<config dir>/skills`. Each instance loads skills only from its own config dir, so `~/.claude/skills` alone is not enough.
   - Codex, OpenCode and other Agent Skills hosts: `~/.agents/skills`.
   - Antigravity: `~/.gemini/config/skills`.
3. Show the user the dry-run output. If it lists conflicts (`✗`), ask: move the existing item, or skip it. Never delete the user's files.
4. Install: `python3 ~/public-skills/install.py --apply`. It only creates symlinks. It never replaces anything.
5. Rules: show the user [`CLAUDE.snippet.md`](CLAUDE.snippet.md). Ask for their base branch, build command and test command, and which `[optional]` lines they want. With their OK, append the block to each instruction file the installer listed (`CLAUDE.md` per Claude config dir; `~/.codex/AGENTS.md` for Codex). Remove the `[essential]`/`[optional]` tags.
6. Tell the user to restart their agent sessions (in T3 Code: start a new thread) so the skills load.

Options: `--skills spec plan` installs a subset. `--target <dir>` adds another skills folder. Update later with `git -C ~/public-skills pull`.

## Install

**Recommended:** run the installer (see the TL;DR above). It finds Claude Code, T3 Code, Codex, OpenCode and Antigravity skills folders, shows a dry run, and creates symlinks with `--apply`.

```sh
git clone https://github.com/1905/public-skills.git ~/public-skills
python3 ~/public-skills/install.py          # dry run
python3 ~/public-skills/install.py --apply  # install
```

**Manual, Claude Code only:**

```sh
mkdir -p ~/.claude/skills
for s in spec plan hill-climb fullsend frontend-design; do
  if [ -e "$HOME/.claude/skills/$s" ] && [ ! -L "$HOME/.claude/skills/$s" ]; then
    echo "exists: $s — move it first"; continue
  fi
  ln -sfn "$HOME/public-skills/skills/$s" "$HOME/.claude/skills/$s"
done
```

### T3 Code

T3 Code runs Claude Code, Codex and other agents as providers. Each provider loads skills from its own folder:

| Provider in T3 Code | Skills folder |
|---|---|
| Claude, default instance | `~/.claude/skills` |
| Claude, instance with its own config dir (the instance's home path setting, or a `CLAUDE_CONFIG_DIR` env var) | `<that dir>/skills` — and its `CLAUDE.md` lives there too |
| Codex | `~/.agents/skills` |
| OpenCode | reads `~/.claude/skills` and `~/.agents/skills` |
| Antigravity | `~/.gemini/config/skills` |

- Install globally. T3 Code may not show repo-local skills (`<repo>/.claude/skills`, `<repo>/.agents/skills`) in its skill picker, because its server can run from your home directory instead of the project (see [t3code#3040](https://github.com/pingdotgg/t3code/issues/3040)).
- T3 Code gives `hill-climb` the full council: it can start reviewers on other providers (Codex, Antigravity, OpenCode) with exact models and effort.
- New skills load in new threads.

### Other notes

- **Check:** start a new session and ask the agent to list its skills.
- **Update:** `git -C ~/public-skills pull`. The symlinks pick up the change.
- **Uninstall:** delete the symlinks the installer created.
- Each skill directory is self-contained. It carries its own copy of `delegation.md`, so you can copy one skill alone. `fullsend` needs `spec` and `plan`.
- Already have the official `frontend-design` plugin? The installer skips it for that Claude config dir; it's the same skill.

## Make them behave as designed: add rules to CLAUDE.md

Much of how these skills behave for the author comes from global rules, not from the skill files. Examples: approve the TL;DR, never commit to the base branch, Opus for code.

Copy the block in [`CLAUDE.snippet.md`](CLAUDE.snippet.md) into `~/.claude/CLAUDE.md` or your project's `CLAUDE.md`. Fill in your base branch, build command and test command. Keep the `[essential]` lines. Choose from the `[optional]` ones.

Add it by hand, or tell your agent: *"Add the rules from public-skills/CLAUDE.snippet.md to my ~/.claude/CLAUDE.md. Ask me for the base branch, build and test commands."*

### HTML reports: always use `frontend-design`

Skills do not trigger on their own reliably. Without a rule, the agent writes generic HTML. Add this line to your CLAUDE.md (by hand, or ask your agent to add it):

```markdown
- HTML for me (reports, pages, mockups, dashboards, any `.html` file): ALWAYS invoke the `frontend-design` skill first and follow it. Subagents that build HTML get the same instruction in their brief.
```

It is already in `CLAUDE.snippet.md`.

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

MIT, except `skills/frontend-design/`: © Anthropic, Apache License 2.0 (see `skills/frontend-design/LICENSE.txt`). Copied unchanged from the official Claude Code `frontend-design` plugin v1.1.1.
