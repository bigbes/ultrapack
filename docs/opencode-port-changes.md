# OpenCode Port Change Ledger

This file records how the Claude plugin was rewritten for OpenCode so future upstream changes can be reapplied deliberately.

## Rule

Treat `plugins/up/` as the source of truth. Reapply upstream changes there first, then update `scripts/generate-opencode.py` only when the OpenCode transform or OpenCode-only agents/commands need to change. Regenerate with:

```bash
python3 scripts/generate-opencode.py
```

Do not hand-edit generated files under `.opencode/agents/`, `.opencode/commands/`, `.opencode/skills/`, or `.opencode/references/` except while debugging the generator.

## Files Changed By This Port

- `scripts/generate-opencode.py`
  - New generator from Claude source to OpenCode layout.
  - Owns generated paths: `.opencode/agents/`, `.opencode/commands/`, `.opencode/skills/`, `.opencode/references/`.
  - Preserves `.opencode/plans/`, package metadata, and `node_modules`.
  - Converts Claude command/agent/skill references (`/up:*`, `up:*`) to OpenCode command and `@agent` names.
  - Converts Claude-only transcript assumptions in `summary` / `summarizer` to visible-context plus repo-state summaries.
  - Converts `reflect` routing from `CLAUDE.md` first to `AGENTS.md` first, with `CLAUDE.md` as compatibility guidance.
  - Adds OpenCode-only agents: `librarian`, `finder`, `oracle`, `diff-explainer`.
  - Adds OpenCode-only command: `explain-diff`.

- `.opencode/plans/1776438413966-cosmic-panda.md`
  - Replaced the old "agent-only / no skills directory" plan.
  - New plan keeps OpenCode skills first-class.
  - Documents generated OpenCode commands, agents, skills, references, and Amp-derived roles.
  - Documents the `AGENTS.md`-first reflect behavior.

- `README.md`
  - Added OpenCode install/generation instructions.
  - Added generated command list: `/make`, `/try`, `/step-back`, `/summary`, `/reflect`, `/explain-diff`.
  - Added generated agent list, including `@librarian`, `@finder`, `@oracle`, and `@diff-explainer`.
  - Notes that Claude remains the source format.

- `CLAUDE.md`
  - Documents dual Claude/OpenCode layout.
  - Documents `scripts/generate-opencode.py` ownership.
  - Adds OpenCode naming convention.
  - Adds the "generated OpenCode" maintenance rule.

- `docs/opencode-port-changes.md`
  - This ledger.
  - Use it when applying future upstream diffs.

## Generated Files

These files are generated and should be updated by running the generator.

### Agents

- `.opencode/agents/explorer.md`
  - Generated from `plugins/up/agents/explorer.md`.
  - Claude frontmatter is converted to OpenCode `mode: subagent` and `permission`.
  - `up:*` references are rewritten.

- `.opencode/agents/implementer.md`
  - Generated from `plugins/up/agents/implementer.md`.
  - Keeps writer behavior but converts metadata to OpenCode.
  - Permission defaults to `edit: ask`, `bash: ask`, `webfetch: deny`.

- `.opencode/agents/researcher.md`
  - Generated from `plugins/up/agents/researcher.md`.
  - Claude tool references are normalized where product-specific.
  - Allows web fetch by permission because external research is in scope.

- `.opencode/agents/reviewer.md`
  - Generated from `plugins/up/agents/reviewer.md`.
  - Read-only OpenCode permissions.
  - Keeps confidence-filtered review behavior.

- `.opencode/agents/summarizer.md`
  - OpenCode-specific generated template, not a direct copy.
  - Removes Claude JSONL transcript lookup.
  - Summarizes from visible context, active task file, git status/diff/log, and repo state.

- `.opencode/agents/librarian.md`
  - OpenCode-only Amp-derived agent.
  - Deep read-only source archaeology across large repos, multiple repos, upstream source, and commit history.
  - Use when `finder` / `explorer` are too shallow.
  - Mermaid diagrams are optional and constrained to complex cross-boundary flows, lifecycle/state transitions, ownership boundaries, or dependency graphs where prose would be less clear.

- `.opencode/agents/finder.md`
  - OpenCode-only Amp-derived agent.
  - Fast file and line-range discovery.
  - No implementation plan or architecture essay.

- `.opencode/agents/oracle.md`
  - OpenCode-only Amp-derived agent.
  - Senior engineering advisor for architecture, planning, debugging strategy, and tradeoffs.
  - Read-only; one primary recommendation; rough effort signal; revisit triggers.

- `.opencode/agents/diff-explainer.md`
  - OpenCode-only Amp-derived agent.
  - Explains diffs by behavior and review order.
  - Not a defect review.

### Commands

- `.opencode/commands/make.md`
  - Generated from `plugins/up/commands/make.md`.
  - `/up:make` becomes `/make`.
  - Uses `$ARGUMENTS` as OpenCode command input.

- `.opencode/commands/try.md`
  - Generated from `plugins/up/commands/try.md`.
  - `/up:try` becomes `/try`.

- `.opencode/commands/step-back.md`
  - Generated from `plugins/up/commands/step-back.md`.
  - `/up:step-back` becomes `/step-back`.

- `.opencode/commands/summary.md`
  - OpenCode-specific rewrite from `plugins/up/commands/summary.md`.
  - Removes Claude transcript discovery.
  - Delegates only to the OpenCode summarizer behavior.

- `.opencode/commands/reflect.md`
  - Generated from `plugins/up/commands/reflect.md` with OpenCode routing.
  - Routes project-wide guidance to `AGENTS.md` first.
  - Does not write global memory unless configured/approved.

- `.opencode/commands/explain-diff.md`
  - OpenCode-only Amp-derived command.
  - Delegates to `diff-explainer`.
  - Empty arguments mean current checkout changes.

### Skills

- `.opencode/skills/udesign/SKILL.md`
  - Generated from `plugins/up/skills/udesign/SKILL.md`.
  - `up:*` references rewritten to OpenCode names.
  - Reference-doc paths point to `.opencode/references/`.

- `.opencode/skills/uplan/SKILL.md`
  - Generated from `plugins/up/skills/uplan/SKILL.md`.
  - Keeps phase/interface graph planning behavior.
  - Reference-doc paths point to `.opencode/references/`.

- `.opencode/skills/uexecute/SKILL.md`
  - Generated from `plugins/up/skills/uexecute/SKILL.md`.
  - Agent references become `@implementer`, `@explorer`, `@researcher`.
  - Claude checklist/tool wording is normalized where needed.

- `.opencode/skills/uverify/SKILL.md`
  - Generated from `plugins/up/skills/uverify/SKILL.md`.
  - Keeps positive/negative/invariant verification flow.

- `.opencode/skills/ureview/SKILL.md`
  - Generated from `plugins/up/skills/ureview/SKILL.md`.
  - Agent reference becomes `@reviewer`.

- `.opencode/skills/udebug/SKILL.md`
  - Generated from `plugins/up/skills/udebug/SKILL.md`.
  - Keeps root-cause-first debugging flow.

- `.opencode/skills/udocument/SKILL.md`
  - Generated from `plugins/up/skills/udocument/SKILL.md`.
  - Guidance destination order is `AGENTS.md / CLAUDE.md / GEMINI.md`.

- `.opencode/skills/git-worktrees/SKILL.md`
  - Generated from `plugins/up/skills/git-worktrees/SKILL.md`.
  - Worktree preference lookup checks `AGENTS.md` before `CLAUDE.md`.

- `.opencode/skills/handsoff/SKILL.md`
  - Generated from `plugins/up/skills/handsoff/SKILL.md`.
  - `/up:make` references become `/make`.

- `.opencode/skills/test-driven-development/SKILL.md`
  - Generated from `plugins/up/skills/test-driven-development/SKILL.md`.
  - Keeps RED-GREEN-REFACTOR guidance.

### References

- `.opencode/references/brevity.md`
  - Generated from `plugins/up/skills/_brevity.md`.
  - Moved out of `.opencode/skills/` because `_brevity` is not a normal skill directory.

- `.opencode/references/principles.md`
  - Generated from `plugins/up/skills/_principles.md`.
  - Moved out of `.opencode/skills/` because `_principles` is not a normal skill directory.

## Upstream Sync Checklist

1. Apply upstream Claude plugin changes to `plugins/up/`.
2. If upstream changes command/agent/skill names, update rewrite rules in `scripts/generate-opencode.py`.
3. If upstream changes `summary`, re-check that no Claude transcript-path dependency leaks into OpenCode output.
4. If upstream changes `reflect`, re-check `AGENTS.md`-first routing.
5. Run `python3 scripts/generate-opencode.py`.
6. Run static checks:

```bash
python3 -m py_compile scripts/generate-opencode.py
rg -n "No skills directory|agent-only|~/.claude/projects|/up:|\\bup:|Task tool|subagent_type|WebSearch|WebFetch|TodoWrite|Sonnet|Opus|Haiku" .opencode/agents .opencode/commands .opencode/skills .opencode/references
```

7. Smoke test in OpenCode when local OpenCode storage is healthy:

```bash
opencode agent list
```
