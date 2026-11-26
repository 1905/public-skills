# public-skills

Agent skills for planned, reviewed feature work. They are written for Claude Code and work in other hosts that read `SKILL.md` files.

| Skill | What it does |
|---|---|
| [`spec`](skills/spec/SKILL.md) | Turns an idea into `plans/YYYY-MM-DD-<feature>/spec.md`. The spec starts with a TL;DR that you approve. |
| [`plan`](skills/plan/SKILL.md) | Turns an approved spec into a versioned plan (`plan-v1.0.md`, `v1.1`, …) of small tasks, then runs it on a feature branch. |
| [`hill-climb`](skills/hill-climb/SKILL.md) | Three independent models review the same target and give it a score. Confirmed findings are fixed. The loop repeats until all three give 9/10 or the round limit is reached. |
| [`fullsend`](skills/fullsend/SKILL.md) | Runs spec → plan → implement → test → review → simplify with no check-ins. |

## Install

Copy or symlink the skill directories into your skills folder:

```sh
git clone https://github.com/1905/public-skills.git
mkdir -p ~/.claude/skills
for s in spec plan hill-climb fullsend; do ln -s "$PWD/public-skills/skills/$s" ~/.claude/skills/$s; done
```

You can also install them per project, in `.claude/skills/`.

## Requirements

- **Subagents.** The skills hand drafting, implementing and reviewing to subagents. See [`docs/delegation.md`](docs/delegation.md).
  - T3 Code `delegate_task` works best. It can pick an exact model and effort for each child.
  - Without T3 Code, the skills use the host's native subagent tool.
- **Several model providers (optional).** `hill-climb` works best with three reviewers from different providers. Change the council table in `hill-climb/SKILL.md` to use your own models.
- **Optional skills that the steps mention:** a plain-English/controlled-language pass for plans, `/simplify`, `/loop` and a notification skill. If you don't have one of these, the step that uses it is skipped.

## Workflow

```
/spec   → you approve the TL;DR
/plan   → you approve the plan
          → the plan runs on a feature branch
/hill-climb <target>   at any point, when you want a hard review
fullsend.              runs the whole pipeline with no stops
```

All artifacts go in `plans/` in the project root. When a feature is finished, its directory moves to `plans/done/`.

## License

MIT
