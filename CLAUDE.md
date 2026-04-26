# ultrapack

Claude Code plugin with a generated OpenCode compatibility layer for spec-driven, git-centered development. The Claude plugin remains the source of truth under `plugins/up/`; OpenCode files are generated into `.opencode/`.

## Repo layout

- `.claude-plugin/marketplace.json` — marketplace manifest (lists `up`)
- `plugins/up/.claude-plugin/plugin.json` — plugin manifest
- `plugins/up/{skills,commands,agents,hooks}/` — plugin contents
- `scripts/generate-opencode.py` — generates `.opencode/{agents,commands,skills,references}/`
- `.opencode/plans/*.md` — OpenCode porting plans
- `docs/tasks/*.md` — task files (design + plan + conclusion per task)
- `README.md`, `CLAUDE.md` — repo docs

Everything under `plugins/up/` loads into Claude Code. The generated `.opencode/` layer is for OpenCode. Everything outside those plugin/config directories (`docs/`, README, CLAUDE.md) is repo-only.

## Naming

Internal plugin name: `up`. Slash/skill invocations use the `up:` prefix: `/up:make`, `up:udesign`, `up:reviewer`. Process skills are `u`-prefixed (`udesign`, `uplan`, `uexecute`, `uverify`, `ureview`, `udebug`, `udocument`) to dodge collisions with Claude Code built-ins.

OpenCode output uses unprefixed command and agent names: `/make`, `/reflect`, `/explain-diff`, `@implementer`, `@reviewer`, `@librarian`, `@finder`, `@oracle`.

## Design principles

- **Minimal** — only skills we actually use; no speculative additions
- **Doc-only** — no runtime code, no unit tests; verification is install-and-invoke
- **Generated OpenCode** — edit Claude source files and `scripts/generate-opencode.py`, then regenerate; do not hand-edit generated OpenCode files unless debugging the generator

## Versioning

Plugin version lives in `plugins/up/.claude-plugin/plugin.json`. Always bump the patch digit (`x.y.Z`) when merging, finalizing, or otherwise landing changes on `main`. Default to patch; ask before bumping minor (`x.Y.z`) or major (`X.y.z`).

## OpenCode generation

Run:

```bash
python3 scripts/generate-opencode.py
```

The generator owns:

- `.opencode/agents/`
- `.opencode/commands/`
- `.opencode/skills/`
- `.opencode/references/`

It must not delete `.opencode/plans/`, `.opencode/node_modules/`, or package metadata.
