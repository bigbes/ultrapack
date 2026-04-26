# Agent Model Routing

**Status:** executing
**Branch:** main
**Worktree:** none
**Mode:** interactive

## Design

Pin a `model:` to every agent's frontmatter so dispatch costs are predictable and aligned to each role's working style. Today no agent declares a model — all 9 inherit OpenCode's session default, so cost depends on whatever the user happened to set.

**Policy: three cheap tiers + one premium-exception tier.** Cheap tiers use models the user already pays for through opencode-go, Zhipu (GLM), Moonshot (Kimi), and DeepSeek. Premium uses opencode-zen for the two roles where deep autonomous reasoning has the highest payoff (review, advisory) and the lowest call volume.

Mapping follows the OMO/Amp principle that GPT-class models suit autonomous reasoning while Claude/Kimi/GLM suit instruction-following and structured output. DeepSeek V4 sits between as best-of-cheap for code-heavy work.

- **Cheap-fast** — `@explorer`, `@finder`, `@summarizer`, `@diff-explainer` → **GLM-5.1**. Fast, structured, instruction-following; high call volume per task.
- **Cheap-quality** — `@implementer`, `@researcher` → **DeepSeek V4-Flash**. Top-of-cheap reasoning for bulk coding and multi-step research decomposition; V4-Flash specifically because it works reliably with opencode tool-calling today (V4-Pro thinking-mode DNFs await a 0.1 patch).
- **Cheap-context** — `@librarian` → **Kimi K2.6**. Long context (256K) for multi-repo / commit-history archaeology; only Chinese model in Tier A on real-world coding benchmarks.
- **Premium** — `@reviewer`, `@oracle` → **GPT-5.5** (via opencode-zen). Autonomous deep reasoning; one dispatch per task each, so spend is bounded by tasks-per-day.

Implementation: add `model: <provider>/<id>` to each agent's frontmatter. Spend overlay stays inside the repo; users provide provider auth in their own `opencode.json`. README install section documents the required providers and which agents need them.

TDD: no (frontmatter-only doc change; verification is "OpenCode loads each agent without error").

### Invariants

- IV1 — Every agent file under `agents/` has exactly one `model:` line in frontmatter.
- IV2 — `@reviewer` and `@oracle` are the only agents on the premium tier.

### Principles

- PC1 — Fail loud over silent fallback: if a provider isn't configured, the agent must error rather than silently using a default model.
- PC2 — Model assignments are visible in the agent file, not hidden in external config — a contributor reading `agents/<x>.md` should see exactly what model dispatches.

### Assumptions

- AS1 — OpenCode's `model:` frontmatter accepts a `provider/model-id` string and routes accordingly using the user's `opencode.json` provider config.
- AS2 — The user's subscriptions cover all three cheap-tier model IDs (GLM-5.1, DeepSeek V4-Flash, Kimi K2.6) and opencode-zen covers GPT-5.5.
- AS3 — GLM-5.1 is good enough for `@summarizer` and `@diff-explainer` output quality (structured, instruction-followed). If output is sloppy, escalate to DeepSeek V4-Flash.
- AS4 — DeepSeek V4-Flash's tool-calling works reliably enough in OpenCode for `@implementer` and `@researcher` (V4-Pro thinking-mode is the known-broken variant per April 2026 testing).

### Unknowns

- UK1 — Exact provider/model-id strings for the `model:` field (e.g. `opencode/glm-5.1` vs `zhipuai/glm-5.1`, `deepseek/deepseek-v4-flash` vs `opencode-go/deepseek-v4-flash`). Resolve by inspecting the user's `opencode.json` or OpenCode's provider catalog at plan time.
- UK2 — Whether `@librarian` ever needs more than Kimi K2.6's 256K context window. If yes, swap to Qwen3.6-Plus (1M context, $0.33/$1.95) via opencode-go in a follow-up task.
- UK3 — When DeepSeek V4-Pro's opencode tool-calling is patched, evaluate whether to upgrade `@implementer` and/or `@researcher` from V4-Flash to V4-Pro. V4-Pro is the LiveCodeBench / Codeforces leader; V4-Flash trades a few benchmark points for reliability today.

## Plan

Approach: Pin `model:` in each agent's frontmatter (PH1), then refresh README to match (PH2). Two commits, sequential. Direct provider prefixes for the three cheap tiers (`zhipuai/`, `deepseek/`, `moonshot/`); `opencode-zen/` for the premium tier.

### PH1 — Pin model per agent

- **1.1** `agents/explorer.md`, `agents/finder.md`, `agents/summarizer.md`, `agents/diff-explainer.md` (modify) — insert `model: zhipuai/glm-5.1` on its own line in frontmatter, after `description:`, before `mode:`.
- **1.2** `agents/implementer.md`, `agents/researcher.md` (modify) — insert `model: deepseek/deepseek-v4-flash` in the same position.
- **1.3** `agents/librarian.md` (modify) — insert `model: moonshot/kimi-k2.6`.
- **1.4** `agents/reviewer.md`, `agents/oracle.md` (modify) — insert `model: opencode-zen/gpt-5.5`.
- Respects: IV1 (every agent has exactly one `model:`), IV2 (only reviewer/oracle on premium), PC2 (model visible in agent file).
- Commit: `feat(agents): pin per-agent model — cheap default + premium exception`

### PH2 — README provider setup and stale parentheticals

- **2.1** `README.md` — under `## Install`, add subsection `### Provider setup` listing the four required providers (`zhipuai` for GLM-5.1, `deepseek` for V4-Flash, `moonshot` for Kimi K2.6, `opencode-zen` for GPT-5.5) and one-line note that agents fail loud if a provider isn't configured (PC1).
- **2.2** `README.md` — in `### Agents`, strip the stale `(Haiku 4.5)` / `(Sonnet 4.6)` parentheticals and replace with the model assigned in PH1 per agent. Cross-link to `docs/models.md` once.
- Respects: AS2 (subscriptions cover all four), PC1 (fail loud over silent fallback).
- Commit: `docs(readme): align agent model parentheticals with routing; document provider setup`

### Test strategy

Doc/config change — verification is install-and-invoke per uverify:

- Each agent dispatches successfully (`opencode` reads the frontmatter without error) — covers IV1, AS1, AS2.
- `@implementer` completes one tool-using turn — covers AS4 (V4-Flash tool-calling reliable).
- `@summarizer` produces structured handoff output on a real session — covers AS3 (GLM-5.1 quality acceptable for instruction-following roles).

### Risks / rollback

- **RK1** — Provider id mismatch (e.g. user's `opencode.json` uses `z-ai` instead of `zhipuai` for GLM, or routes Kimi via opencode-go instead of direct Moonshot). Mitigation: one-line frontmatter edit per affected file; canonical strings + alternatives documented in `docs/models.md`.
- **RK2** — DeepSeek V4-Flash tool-calling breaks for `@implementer` / `@researcher` despite AS4. Mitigation: swap those two files to `model: moonshot/kimi-k2.6` (the deferred alternative noted in design and `docs/models.md`).

## Verify

<empty — filled by uverify>

## Conclusion

<empty — filled by ureview>
