# ultrapack

Opinionated [OpenCode](https://opencode.ai) skill pack for developers: plan-driven, git-centered, minimalistic. Built around frequently clearing context and using one conversation per feature.

## TL;DR

```
/make fix the flaky login test
```

Walks you through Design → Plan → Execute → Verify → Review → docs refresh.

Each stage populates `docs/tasks/<slug>.md`. The task file is the source of truth — any fresh agent can read it and resume from wherever the last one stopped. `docs/TODO.md` is a rolling index across tasks.

```
/make handsoff fix the flaky login test
```

Same, but ask as few questions as possible. The agent picks the safest, most reversible choices: don't delete things (copy and rename instead), work in a git branch, no silent defaults, fix only critical issues.

Core ideas:
- One file per task. `docs/tasks/<slug>.md` evolves through Design → Plan → Verify → Conclusion.
- Invariants-, principles-, and assumptions-first. Discovered in design, obeyed in plan, checked at review. Short IDs (IV, PC, AS, UK) let later sections reference them without re-quoting.
- Per-phase subagent implementation. Each plan phase dispatched to a fresh `@implementer`. Plan declares interfaces (`### Interfaces`) and an execution graph (`### Interface graph`); the executor topo-sorts it into waves and dispatches independent phases in parallel.
- Mandatory manual testing. Agent runs what it built before claiming done.
- As short as I could make it. Doesn't waste tokens.

## Install

OpenCode reads from `.opencode/` (per-project) or `~/.config/opencode/` (global). This repo's directory layout (`agents/`, `commands/`, `skills/`, `references/`) maps directly into either location.

### Per-project

```bash
git clone https://github.com/bigbes/ultrapack.git /tmp/ultrapack
cd your-project
mkdir -p .opencode
cp -r /tmp/ultrapack/{agents,commands,skills,references} .opencode/
rm -rf /tmp/ultrapack
```

### Global (recommended — installs once, works everywhere)

```bash
git clone https://github.com/bigbes/ultrapack.git ~/.local/share/ultrapack
mkdir -p ~/.config/opencode/{agents,commands,skills,references}
ln -sfn ~/.local/share/ultrapack/agents/*     ~/.config/opencode/agents/
ln -sfn ~/.local/share/ultrapack/commands/*   ~/.config/opencode/commands/
ln -sfn ~/.local/share/ultrapack/skills/*     ~/.config/opencode/skills/
ln -sfn ~/.local/share/ultrapack/references/* ~/.config/opencode/references/
```

To upgrade: `git -C ~/.local/share/ultrapack pull`. Symlinks pick up changes automatically.

### Provider setup

Each agent declares its own `model:` in frontmatter, so the matching providers must be configured in your `opencode.json`:

- `zhipuai` — for GLM-5.1 (`@explorer`, `@finder`, `@summarizer`, `@diff-explainer`)
- `deepseek` — for DeepSeek V4-Flash (`@implementer`, `@researcher`, `@rush`)
- `moonshot` — for Kimi K2.6 (`@librarian`, `@smart`)
- `opencode-zen` — for GPT-5.5 (`@reviewer`, `@oracle`, `@deep`)

If a provider isn't configured, the affected agent fails loud rather than silently falling back to a different model. Rationale and alternatives in [`docs/models.md`](docs/models.md).

### Verify

Open OpenCode in any project and run `/make a quick smoke test` — it should kick off the design stage.

## Design

Inspired by [feature-dev](https://github.com/anthropics/claude-code/tree/main/plugins/feature-dev) and [obra/superpowers](https://github.com/obra/superpowers). Feature-dev is too barebones; superpowers is great but builds huge plans with duplication and is geared to a specific style of dev work. Ultrapack takes the best of both, shortened and simplified.

The whole workflow updates one markdown file per task — `docs/tasks/<slug>.md` with sections Design, Plan, Verify, Conclusion — and tracks all of them in `docs/TODO.md`. It's git-centered: worktrees by default for parallel work, incremental commits for easier rollback and review.

Each stage is a skill. `/make` orchestrates the flow:

- `udesign` — discuss tradeoffs, discover **invariants** (hard constraints, e.g. "class Player must not access internals of class Enemy"), **principles** (softer guidance like "prefer composition over inheritance"), **assumptions** (unverified premises the design rests on; the Conclusion reports whether each held), and **unknowns** (open questions to resolve during plan/execute). Writes the initial spec to the task file.
- `uplan` — populate the task file with a concrete plan: files to change, classes/methods to update or create, interfaces, test strategy, phase breakdown, execution order. No code blocks unless especially tricky.
- `uexecute` — create branch + worktree, dispatch independent `@implementer` agents per plan phase, incremental commits, plan/design checks between phases. The plan's `### Interface graph` is topo-sorted into waves; phases in the same wave run in parallel (implementers stage; dispatcher commits serially in phase order). Boundary check after each commit (diff ⊆ declared `Owns` paths). Wiring check after the final wave (per-IF caller/anchor match). Uses TDD when helpful.
- `uverify` — manual smoke test from a positive/negative/invariant checklist. Writes summary to task file. Loops back to execute on failure.
- `ureview` — dispatch `@reviewer` (independent, knows design/plan/diff but not implementer's rationale). Confidence-filtered (≥80), severity-tiered. Fills the Conclusion. Then refreshes project docs.

## Components

### Skills

Process skills (u-prefixed to dodge built-ins):
- `udesign` — Brainstorm requirements, populate Design + Invariants + Principles + Assumptions + Unknowns, decide TDD.
- `uplan` — Plan: files, classes/methods, interfaces, test strategy, order. Non-trivial code blocks only.
- `uexecute` — Dispatch `@implementer` per phase (parallel waves from `### Interface graph`), incremental commits, boundary + plan-diff + consistency sweep per phase, wiring check after the final wave.
- `uverify` — Positive + negative + invariant checklist, manual smoke test, writes summary, loops back on failure.
- `ureview` — Dispatch `@reviewer`: independent review, check that all invariants/assumptions still hold.
- `udebug` — Four-phase root-cause investigation.
- `udocument` — Guidance for updating docs, AGENTS.md, READMEs, in-code comments.

Discipline skills:
- `test-driven-development` — Failing test → make change → test passes.
- `git-worktrees` — Worktree conventions.
- `handsoff` — Shared contract for hands-off mode (`/make handsoff <description>`): safety principles, decision log, no-default rule, end-of-task summary.

### Commands

- `/make [handsoff] <description>` — Orchestrate the full flow: task file → design → branch → plan → execute → verify → review → docs refresh.
- `/try` — Design one positive and one negative test case, run both, report.
- `/step-back` — Circuit breaker: stop, diagnose why approaches failed, propose new direction.
- `/summary` — Produce a handoff summary so another session can continue with zero context.
- `/reflect` — Reflect on the dialogue, extract learnings into AGENTS.md / docs.
- `/explain-diff` — Explain a diff by behavior and review order.

### Agents

Model assignments are pinned in each agent's frontmatter; see [`docs/models.md`](docs/models.md) for the routing rationale.

- `@explorer` (GLM-5.1) — Codebase tracing, file:line refs, 3–5 essential files.
- `@implementer` (DeepSeek V4-Flash) — One phase: code + tests + commit + self-review. Receives `Owns`/`Implements`/`Consumes` from the plan's interface graph. `commit: self|defer` mode (defer for parallel waves; dispatcher commits serially). Fresh context per dispatch.
- `@reviewer` (GPT-5.5) — Independent review against Plan + Invariants + Assumptions. Confidence-filtered (≥80), severity-tiered.
- `@researcher` (DeepSeek V4-Flash) — Decompose a query, investigate systematically.
- `@summarizer` (GLM-5.1) — Drafts the handoff prose for `/summary`; gathers repo state, never writes.
- `@librarian` (Kimi K2.6) — Deep multi-repo/source archaeology, commit-history context, architecture explanations.
- `@finder` (GLM-5.1) — Fast file and line-range discovery, no architecture essay.
- `@oracle` (GPT-5.5) — Senior engineering advisor for architecture, planning, debugging strategy, tradeoffs.
- `@diff-explainer` (GLM-5.1) — Behavior-first diff walkthrough.

General-purpose personality agents (depth/speed tradeoff, lifted from Amp's tier scheme):
- `@rush` (DeepSeek V4-Flash) — Fast executor, terse output, parallel tool use. For well-defined tasks where speed matters more than discussion.
- `@smart` (Kimi K2.6) — Pragmatic balanced default; builds context first, smallest correct change, persists end-to-end.
- `@deep` (GPT-5.5) — Thorough reasoner; leans on `@oracle` for hard structural calls; for complex, multi-file, or risky work.

## License

WTFPL — see [license.txt](license.txt).
