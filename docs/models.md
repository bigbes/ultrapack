# Agent Model Routing — Reference

Snapshot of the model landscape and routing decisions as of **April 2026**, kept here so we can revisit when models, prices, or subscriptions shift. The active spec lives in `docs/tasks/agent-model-routing.md`; this file holds the rationale, alternatives considered, and revisit triggers.

## Current routing

- **GLM-5.1** → `@explorer`, `@finder`, `@summarizer`, `@diff-explainer`
- **DeepSeek V4-Flash** → `@implementer`, `@researcher`, `@rush`
- **Kimi K2.6** → `@librarian`, `@smart`
- **GPT-5.5** (via openai) → `@reviewer`, `@oracle`, `@deep`
- **Gemini 3 Flash** (via opencode) → `@look-at`

Tier philosophy: cheap by default; premium reserved for the two roles where autonomous deep reasoning has the highest payoff and the lowest call volume (review, advisory). The three personality agents (`@rush`/`@smart`/`@deep`) are general-purpose dispatch targets — they share each tier with a specialised agent rather than introducing a new tier. `@look-at` is the only agent on a vision-capable model; it carries Amp's "look at" role for images, diagrams, and PDFs.

## Why each role got each model

- **`@explorer` / `@finder` / `@summarizer` / `@diff-explainer` → GLM-5.1.** High call volume per task. Instruction-following + structured output is what these roles need; raw reasoning depth is wasted. GLM-5.1 also has the cheapest sustained pricing via the GLM Coding Plan ($30–240/quarter) when the budget tightens.
- **`@implementer` / `@researcher` → DeepSeek V4-Flash.** Top-of-cheap reasoning, $0.14/$0.28 with 1M context. Flash specifically (not Pro) — V4-Pro thinking-mode currently DNFs on tool calls in OpenCode (Simon Willison's testing, April 2026). Flash works reliably today.
- **`@librarian` → Kimi K2.6.** Long-context multi-repo / commit-history archaeology. K2.6 is the only Chinese non-Big-3 model that landed Tier A on real-world coding benchmarks ("writes production-grade code without nudging" — AkitaOnRails, April 24 2026). 256K context covers almost all archaeology cases.
- **`@reviewer` / `@oracle` → GPT-5.5.** Deep autonomous reasoning where mistakes are expensive. Both dispatched once per task, so spend is bounded by tasks-per-day. Aligns with OMO's recommendation that "principle-driven autonomous reasoning" roles map to GPT-class models.
- **`@rush` / `@smart` / `@deep` → tier mirrors Amp's `Rush`/`Smart`/`Deep` modes.** Personality agents lifted from Amp's system prompts (see [`amp_system_prompts.json`](../amp_system_prompts.json)). `@rush` on V4-Flash for cheapest-fastest execution (Amp's Haiku slot); `@smart` on Kimi K2.6 for pragmatic-engineer balance (Amp's Sonnet/Opus slot, kept on the cheap-default tier); `@deep` on GPT-5.5 for thorough reasoning that leans on `@oracle` (Amp's GPT slot).
- **`@look-at` → Gemini 3 Flash.** Visual analyzer lifted from Amp's `rAR` "look at" prompt. Picked Gemini Flash because it's cheap, vision-native, and Amp itself uses Gemini Flash for the analogous `Search` role on its Models page. None of the existing pinned models are vision-capable, so this is the only routing slot that genuinely needs a new provider rather than reusing an existing one.

## Background sources

- **Amp's Models page** (screenshot from `claude.ai/amp/models`) — the tier scheme that inspired this layout: `Smart` (Opus), `Rush` (Haiku), `Deep` (GPT), specialized subagents for `Search` (Gemini Flash), `Oracle` (GPT), `Librarian` (Sonnet).
- **oh-my-openagent agent-model matching** — <https://github.com/code-yeongyu/oh-my-openagent/blob/dev/docs/guide/agent-model-matching.md>. The "models as developers with different brains" framing: Claude/Kimi/GLM are mechanics-driven (instruction-following, multi-step procedures), GPT is principle-driven (autonomous reasoning). Drove the choice of GPT for `@reviewer` + `@oracle` and Claude-family/Kimi/GLM for the rest.
- **Deep-research report (April 2026)** — full text in [`docs/models-research-2026-04.md`](models-research-2026-04.md). Key quote: "Set up Kimi K2.6 via Moonshot's API for agentic edits and `/architect` reasoning, Qwen 2.5-Coder 32B in Ollama for editor autocomplete, and keep DeepSeek V4-Flash as a $0.14/$0.28 fallback for one-shot algorithm questions."

## Pricing & benchmark snapshot — April 2026

Treat SWE-Bench Verified as **directional only** — OpenAI retired it in February 2026 after finding 59.4% of unsolved hard tasks had broken test cases. SWE-Bench Pro and Terminal-Bench 2.0 are the better signals.

| Model | License | Input/Output ($/M) | Context | SWE-V | SWE-Pro | LCB | Term-2 |
|---|---|---|---|---|---|---|---|
| **Kimi K2.6** | MIT-mod | 0.95 / 4.00 | 256K | 80.2 | **58.6** | 89.6 | 66.7 |
| **DeepSeek V4-Pro** | MIT | 1.74 / 3.48 | 1M | 80.6 | 55.4 | **93.5** | 67.9 |
| **DeepSeek V4-Flash** | MIT | **0.14 / 0.28** | 1M | 79.0 | — | 91.6 | 56.9 |
| **GLM-5.1** | MIT | 1.00–1.40 / 3.20–4.40 | 200K | 77.8 | 58.4 | — | **69.0** |
| **MiniMax M2.5** | open | 0.30 / 1.20 | 197K | 80.2 | ~50 | 78.0 | — |
| **Qwen3.6-Plus** | closed | 0.33 / 1.95 | **1M** | 78.8 | — | — | 61.6 |
| **Devstral 2 (123B)** | mod-MIT | 0.40 / 2.00 | 256K | 72.2 | — | — | — |
| **grok-code-fast-1** | closed | 0.20 / 1.50 | 256K | 70.8* | — | — | — |
| **Nemotron 3 Super** | NVIDIA OML | 0.30 / 0.75 | 1M | 60.5 | — | 81.2 | — |

\* xAI self-reported; vals.ai independent runs are ~12 points lower.

## Alternatives considered, not chosen

- **DeepSeek V4-Pro for `@implementer`** — leader on LiveCodeBench (93.5%) and Codeforces (Elo 3206, beats GPT-5.4). Rejected because thinking-mode tool-calling DNFs in OpenCode today. Revisit after the V4 0.1 patch lands.
- **Kimi K2.6 across the cheap-quality + cheap-context tiers** (collapsing implementer/researcher onto K2.6 with librarian) — would simplify to one cheap model. Rejected because DeepSeek V4-Flash is dramatically cheaper per token and equivalently capable for tool-using agentic work; the per-task savings compound.
- **Qwen3.6-Plus for `@librarian`** — 1M context (4× Kimi K2.6), $0.33/$1.95. Rejected for v1 because closed-weight, not in current subscription set, and 256K covers almost all real archaeology cases. Hold as fallback if Kimi truncates on a real query.
- **Codestral 22B for any FIM/autocomplete role** — N/A in this pack; we don't ship an autocomplete agent. If we ever do, Codestral 22B (95.3% FIM pass@1) or Qwen 2.5-Coder are the picks. Qwen 3.5+ does not support FIM — common gotcha.
- **Gemini 3.1 Pro for `@reviewer`** (Amp's choice) — rejected in favor of GPT-5.5 because OMO's framing puts autonomous bug-hunting in GPT's wheelhouse. Could swap if GPT-5.5 reviews feel mechanical or miss subtle bugs.
- **Opus 4.7 for `@oracle`** — equivalent to GPT-5.5 in capability; OMO listed Opus as a viable fallback. Picked GPT-5.5 to keep the premium tier on a single provider (openai) and reduce config surface.

## Revisit triggers

Revisit this routing when **any** of these change:

- **DeepSeek V4 patch** lands fixing tool-calling DNFs → upgrade `@implementer` and/or `@researcher` from V4-Flash to V4-Pro. (Research expected this within weeks of April 24 2026.)
- **`@librarian` truncates on a real query** → swap K2.6 → Qwen3.6-Plus (1M context).
- **GPT-5.5 reviews feel sloppy** → try Gemini 3.1 Pro (Amp's reviewer pick) or Opus 4.7.
- **Kimi K3 / Grok 5 ship** (rumored Q2 2026) → benchmark against K2.6 / GPT-5.5 in their respective slots.
- **GLM Coding Plan price changes** or you drop a subscription → re-evaluate cheap-fast tier.
- **Cost telemetry** shows an unexpected agent dominating spend → tier-down that agent if quality permits.

## Subscription map

What pays for what (as of April 2026):

- **zai-coding-plan** — GLM family (`glm-4.5-air`, `glm-4.7`, `glm-5-turbo`, `glm-5.1`); GLM Coding Plan if heavy use.
- **kimi-for-coding** — Kimi K2.6 (`k2p6`); Moonshot's coding-tier subscription.
- **deepseek** (direct) — V4-Flash, V4-Pro (1M context tier; aggressive cache pricing $0.145/M cache hit).
- **openai** (direct) — GPT-5.4 / 5.5 family, including `-fast` and `-mini` / `-mini-fast` sizings (premium-tier exception path).
- **opencode** — Gemini 3 Flash (vision-capable; the only vision-native model in the routing). Also serves as a single-gateway alternative for GLM, Kimi, GPT, and most other listed models — useful if you'd rather have one provider entry in `opencode.json` than four.

## Provider notes

Loose facts kept around for the next routing decision; not load-bearing on any current pin.

### opencode/big-pickle

Stealth model on the opencode gateway, widely rumoured to be a tuned GLM-4.6 (per Reddit). Free-tier as a feedback-gathering trial. Known for strong coding output — Go, AWS debugging, single-shot tasks. Two variants: standard (typical edits) and `big-pickle-max` (longer context, larger output budget). Slower than other free models in the same gateway but often produces better results, which raises the open question of whether the gain is the model itself or heavy prompting on top. Hits "too many requests" under load, so not safe to wire into a high-volume agent — fine for one-shot exploratory dispatch.

### nvidia/

40 requests-per-minute free tier across the catalog. Useful as a fallback or for low-volume specialty models (vision-instruct, FIM-capable Codestral, embeddings) that the paid providers don't carry.

### ollama-cloud/

$20/month subscription with generous usage caps — closer to "unmetered for an individual" than per-token pricing. Worth considering for high-volume cheap-tier work if `kimi-for-coding` / `zai-coding-plan` subscriptions ever get squeezed; carries equivalents of Kimi, GLM, Qwen-coder, Devstral, and others.
