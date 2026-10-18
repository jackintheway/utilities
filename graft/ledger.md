# Graft ledger

Every verdict graft has given, oldest first. Check here before reviewing anything. Reopen an item only when something real changed (a major new version, a new need, or the setup changed), and name the change.

## My setup

(Filled in on the first run, from the Context Setup questions in SKILL.md.)

---

## Example entry (delete this once your first real entry is in)

A real entry from the setup this skill was built in, lightly trimmed, to show the shape.

## 2026-10-18: "The Claude Code workflow that helped me win 5 Hackathons in a Row" (Johnathan Mo, youtu.be/AoxK3JpxbRc; skills at github.com/23jmo/jmo-skills)

- **/codex handoff skill (Claude runs `codex exec` to hand Codex a review or a scoped feature)**: Borrow. Not a native subagent: Claude shells out to Codex's headless mode, sandbox read-only by default, then reads Codex's answer and verifies it. Codex CLI is installed and signed in here. Landing spot: a small skill of my own, read-only second opinion by default. His repo is MIT, one maintainer, created 2026-09-20. Acted on 2026-10-18: a `codex` skill, read-only by default, with a privacy check before sending private material out, and Claude verifies every point before reporting. A test run reviewed one of my scripts in 35 seconds and found four real issues, all confirmed against the code.
- **Superset (agent IDE, one git worktree per workspace, built-in browser, diffs)**: Already covered. The Claude desktop app does parallel sessions in worktrees with a browser pane and diff view.
- **/interview (question the user until aligned, save a spec)**: Already covered. Assumptions-first and "done when" lines in my global CLAUDE.md, question cards, plan mode.
- **/agentation (click-to-annotate page elements for the agent)**: Skip. Next.js only, needs its own MCP server; my sites are static.
- **Supabase, Neon, Stripe MCPs**: Skip. No project uses them.
- **Think backward from the winning demo, sleep and pitching tips**: Skip. Hackathon craft, not setup.
- **Past the list:** a Codex review is an outside judge from a different model family, which fits a habit of never letting a model grade its own work. Not acted on.
