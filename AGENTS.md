# ultrapack

OpenCode skill pack for spec-driven, git-centered development. The whole workflow is built around evolving one markdown file per task (`docs/tasks/<slug>.md`) through Design → Plan → Verify → Conclusion, with `docs/TODO.md` as a rolling index across tasks.

## Repo layout

- `agents/` — subagents (`@implementer`, `@reviewer`, `@explorer`, `@summarizer`, `@researcher`, `@finder`, `@librarian`, `@oracle`, `@diff-explainer`, `@rush`, `@smart`, `@deep`)
- `commands/` — slash commands (`/make`, `/try`, `/step-back`, `/summary`, `/reflect`, `/explain-diff`)
- `skills/<name>/SKILL.md` — process and discipline skills (`udesign`, `uplan`, `uexecute`, `uverify`, `ureview`, `udebug`, `udocument`, `git-worktrees`, `handsoff`, `test-driven-development`)
- `references/` — shared snippets (`brevity.md`, `principles.md`) included by skills
- `docs/tasks/<slug>.md` — one file per task (source of truth per task)
- `docs/TODO.md` — rolling index across tasks
- `README.md`, `AGENTS.md`, `license.txt` — repo docs

This repo is structured to drop directly into OpenCode — copy `agents/`, `commands/`, `skills/`, `references/` into `.opencode/` (per-project) or `~/.config/opencode/` (global). See `README.md` for install commands.

## Naming

Commands and agents have no prefix: `/make`, `/reflect`, `@implementer`, `@reviewer`. Process skills are `u`-prefixed (`udesign`, `uplan`, `uexecute`, `uverify`, `ureview`, `udebug`, `udocument`) to dodge collisions with built-in commands a host might ship.

## Task tracking

`docs/TODO.md` is the rolling index of every task in `docs/tasks/`. `/make` updates it at task creation, every status transition, and on finish — entries move from `## In flight` to `## Done`. The per-task file remains the source of truth; `TODO.md` is a navigation aid so a fresh session can answer "what's open right now?" without globbing.

## Design principles

- Minimal — only skills used in the workflow; no speculative additions
- Doc-only — no runtime code, no test harness; verification is install-and-invoke
- Source of truth lives in the task file, not in agent memory or chat scrollback

## Versioning

Releases are git tags only (`vX.Y.Z`). No version file. Default to patch on landing changes; ask before bumping minor or major.
