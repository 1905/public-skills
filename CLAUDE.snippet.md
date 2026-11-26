# Suggested CLAUDE.md rules for public-skills

Paste the block below into `~/.claude/CLAUDE.md` (all projects) or a project's `CLAUDE.md` (one project).
Fill in the three `<…>` values on the "Base branch" line.

- **[essential]** lines make the skills behave as designed. Keep them.
- **[optional]** lines are the author's taste. Keep the ones you like.

Delete the `[essential]` / `[optional]` tags after you choose.

```markdown
## Feature workflow (public-skills)

- [essential] Plan before code. Non-trivial feature or multi-file bugfix: `/spec` → I approve the TL;DR → `/plan` → I approve → exec. Exceptions: fixes under ~10 lines, typo and wording fixes.
- [essential] "Just do X" = exactly X. It skips the plan only when X is a small fix.
- [essential] An approval request pastes the spec's `## TL;DR` verbatim. It is all I read.
- [essential] Every plan revision is a new file (`plan-v1.0`, `v1.1`, …). Every file has a `**Status:**` line. Finished features move to `plans/done/`.
- [essential] Never commit to the base branch. One feature = one branch. Exec starts only from a clean base branch; dirty tree or another branch → stop and ask.
- [essential] Base branch: <main|master|dev>. Build: <command>. Test: <command>.
- [essential] No automatic model review of specs or plans. One independent read-only review of the whole branch at the end. Verify each finding before a fix. A self-check is not an independent review. Report a failed review as failed.
- [essential] Tests never use a database you did not create for that run.
- [essential] Models: Opus writes spec and plan drafts and implements code. Sonnet only for read-only tasks that change no file. Fable 5.2 and Astra 6.2 only when I name them. Review fixes use the session model. Never replace a model I named without telling me.
- [essential] "fullsend.", "fullsend", "full auto", "do it all" → run the `fullsend` skill: no check-ins. Stop only for safety, a decision only I can make, or a failed precondition. Never ask "want me to continue?".
- [essential] HTML for me (reports, pages, mockups, dashboards, any `.html` file): ALWAYS invoke the `frontend-design` skill first and follow it. Subagents that build HTML get the same instruction in their brief.
- [optional] Push the feature branch after each finished task. After each push, watch CI (e.g. `gh run watch`); red → fix → push, until green.
- [optional] Merge into the base branch only through a pull request, and only when I ask. Merge a green branch the day it passes.
- [optional] Hill-climb: at most three rounds per PR in total. Stop early when all three reviewers give 9/10 or more on the same snapshot. Scores never block a merge.
- [optional] Hill-climb `strict council`: never substitute a reviewer; a missing model stops the run.
- [optional] Choices: score every option 1-10 for fit to my goal, one line on what costs the missing points, recommend the highest.
- [optional] Three or more steps → keep a todo list and check items off.
- [optional] Notify me (notification skill) when you need a decision or a long job ends.
- [optional] No AI attribution lines or co-author trailers in commits and PR bodies.
- [optional] Never create a git worktree unless I ask. Never `git stash` on your own.
```
