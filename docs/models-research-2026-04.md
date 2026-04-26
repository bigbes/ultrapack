# Coding LLM Deep Research — April 2026

Verbatim copy of the deep-research report that informed `docs/models.md`. Kept as a snapshot so future revisits can compare against the data we actually had at the time.

---

## Coding LLM picks for April 2026, no Big-Three needed

**For Aider-style CLI work right now, pick Kimi K2.6 as your default agentic driver, Qwen 2.5-Coder for FIM autocomplete, and DeepSeek V4-Pro for hard algorithm problems.** Three Chinese open-weight models — Kimi K2.6 (Moonshot), DeepSeek V4 (released April 24), and GLM-5.1 (Z.ai) — now sit roughly 5–8 points behind Claude Opus 4.7 and GPT-5.4 on SWE-Bench Verified while costing 5–20× less, and all three are MIT-licensed. The real story of Q1 2026 is that **Cursor's Composer 2 was revealed to be Kimi K2.5 fine-tuned with RL**, meaning the dominant Western coding IDE is already running an open Chinese model under the hood. Below are concrete picks for an Aider/Cline user on Go and distributed systems work, with cost, license, and "what actually breaks" notes per tier.

## How the field looks heading into May 2026

The non-Big-3 frontier consolidated around five labs: **DeepSeek, Moonshot (Kimi), Z.ai (GLM), Alibaba (Qwen), and MiniMax** on the Chinese side; **Mistral, xAI, NVIDIA, and Cursor** on the Western side. Meta has effectively dropped out of the coding race — Llama 4 Maverick scores ~40% on LiveCodeBench and Llama 5 doesn't exist. Cohere never built a coding-specialist model. IBM Granite is fine for edge/regulated deployments but not a contender. Reka and Inflection are not relevant in 2026.

Two structural caveats shape every recommendation. First, **SWE-Bench Verified is officially contaminated**: OpenAI retired it in February 2026 after finding 59.4% of unsolved hard tasks had broken test cases, and the same models drop ~30 points on SWE-Bench Pro. Treat Verified scores as directional only, and lean on **SWE-Bench Pro, Terminal-Bench 2.0, and LiveCodeBench** when comparing models. Second, **scaffolding is worth 2–6 points on agentic benchmarks** independent of the model — Forge Code, Factory Droid, KRAFTON Terminus all materially shift rankings, so a "best agent" number is really a model-plus-harness measurement.

## Agentic and large-codebase work

**Top pick: Kimi K2.6 (Moonshot, MIT-modified, 1T total / 32B active MoE).** Released April 20, 2026. Scores 80.2% on SWE-Bench Verified, **58.6% on SWE-Bench Pro (highest open-weight)**, 89.6% on LiveCodeBench, and 66.7% on Terminal-Bench 2.0. Native 256K context, designed for 12-hour autonomous sessions and agent swarms up to 300 sub-agents / 4,000 coordinated steps. Bundled with Kimi Code CLI, but works fine as an Aider/Cline backend via the official Moonshot API ($0.95/$4.00 per M tokens) or cheaper providers (Parasail $0.60/$2.80, DeepInfra $0.75/$3.50, Together FP4). On AkitaOnRails' April 24 real-world Ruby/full-stack benchmark, **Kimi K2.6 was the only Chinese model to reach Tier A** (87/100 vs. Opus 4.7 at 97); every other Chinese non-Big-3 model clustered in Tier B because they skip tests, error handling, and concurrency-safe patterns. For Tarantool/Go work specifically, this matters — K2.6 is the one that actually writes production-grade code without nudging.

**Strong alternate 1: DeepSeek V4-Pro (MIT, 1.6T total / 49B active, 1M context).** Released April 24, 2026 as a preview. Tops LiveCodeBench at 93.5%, Codeforces Elo 3206 (#1 across all tested models including GPT-5.4), 80.6% SWE-Verified, 67.9% Terminal-Bench. Pricing is $1.74/$3.48 with a 75% promotional discount through May 5, plus aggressive cache pricing ($0.145/M cache hit). The 1M context is a real differentiator for monorepo work — load a Tarantool checkout and ask for cross-module refactors. **Caveat**: V4 just shipped, all numbers are self-reported, and Simon Willison's testing flagged tool-calling integration issues in opencode where V4 Pro DNFs in thinking mode. Watch for a 0.1 patch before deploying it as your default; V4-Flash (also MIT, 13B active, $0.14/$0.28, 1M context) is the cheaper sibling that already works reliably.

**Strong alternate 2: GLM-5.1 (Z.ai, MIT, 754B total / 40B active).** Best non-Big-3 score on Terminal-Bench 2.0 at **69.0%**, SWE-Pro 58.4%, and the only model with independently verified Code Arena Elo (1530, third globally on agentic webdev per Arena.ai). The killer feature for hobbyist budgets is the **GLM Coding Plan**: $30/quarter Lite, $90/quarter Pro, $240/quarter Max, drop-in compatible with Claude Code, Cline, Cursor, and OpenClaw. Demonstrated 8-hour autonomous research-and-optimize loops (655-iteration vector-DB tuning, CUDA kernel autotuning at 35.7× speedup). Trained entirely on Huawei Ascend chips, zero NVIDIA hardware. Weakness: text-only, slower output, and 200K context vs. K2.6/V4's 256K–1M.

**Honorable mentions worth knowing.** **MiniMax M2.5** ($0.30/$1.20, 230B/10B-active, 80.2% SWE-Verified) is the *de facto* OpenHands default — it accounts for 41.4% of OpenHands' OpenRouter token volume at 2.2% of cost, the best price/performance ratio in production right now. **Mistral Devstral 2** (123B, modified MIT, $0.40/$2.00, 256K context, 72.2% SWE-Verified) is the best Western open-weight pick if you want to avoid Chinese providers entirely; **Devstral Small 2** (24B, Apache 2.0, $0.10/$0.30) at 68% SWE-Verified is the realistic local-on-a-4090 choice. **Cursor Composer 2** is excellent if you live in Cursor but isn't available as a standalone API.

## Fast autocomplete and FIM

**Top pick: Qwen 2.5-Coder (7B / 14B / 32B by VRAM tier).** Counterintuitively, the 18-month-old Qwen 2.5-Coder family **still wins inline FIM at every size class** in early-to-mid 2026. The newer Qwen 3.5 and Qwen 3.6 models do not support fill-in-the-middle — they're chat/agent-only — and this is the most common gotcha in r/LocalLLaMA threads. Run via Ollama or vLLM behind Continue.dev or Zed. Apache 2.0 license, runs everywhere, latency in single-digit milliseconds on consumer hardware.

**Strong alternate 1: Codestral 22B (Mistral, August 2025).** Hits **95.3% FIM pass@1, the highest of any model including closed ones**. The standard `tabAutocompleteModel` recommendation in Continue.dev. The catch is the Mistral Non-Production License — fine for personal use, you need a commercial license for company work. 256K context and 80+ languages.

**Strong alternate 2: Qwen3-Coder-Next (80B-A3B MoE, Apache 2.0).** Native FIM, 3B active parameters, runs on a single RTX 5090 at Q4_K_M quantization at 38–48 tok/s, or on a Mac M4 Max at usable speeds. 256K context, $0.14/$0.80 if you'd rather hit OpenRouter than self-host. The right choice if you have 48GB+ of unified memory or VRAM and want one model that handles both autocomplete and light agent work.

For pure cloud-based autocomplete latency, **xAI grok-code-fast-1** runs at ~92 tok/s with $0.20/$1.50 pricing and >90% cache hit rates in Cursor/Copilot integrations, but it's closed-weight and lock-in to xAI's API.

## Algorithms and one-shot problems

**Top pick: DeepSeek V4-Pro (or V4-Flash).** Currently #1 on LiveCodeBench at **93.5%** (V4-Flash at 91.6%) and **Codeforces Elo 3206** — beating GPT-5.4 (3168) and Gemini 3.1 Pro on both. For LeetCode Hard, AtCoder, and competitive-programming work this is the new state of the art among non-Big-3, and the **V4-Flash variant at $0.14 input / $0.28 output is by an enormous margin the best $/correct-solution model on the market**. Use the "Think Max" mode for hard problems (384K output budget). Strong on math-heavy code: HMMT 2026 95.2%, GPQA Diamond 90.1%.

**Strong alternate 1: Kimi K2.6.** LiveCodeBench v6 at 89.6%, beats Claude Opus 4.6 (88.8). Better than DeepSeek V4 at "explain the algorithm before coding" workflows because of stronger HLE-with-tools performance (54.0%, actually #1 across all models tested). Pick K2.6 over V4 if you want both the algorithm reasoning and to use the same model for agentic work — it's the all-rounder.

**Strong alternate 2: Step-3.5-Flash (StepFun, 196B/11B-active, Apache 2.0)** for math-heavy code on a budget. Hits 99.8% on AIME 2025 with Python and 97.3% standalone, $0.10/$0.30 pricing, available on OpenRouter free tier. Niche but excellent for numerical algorithms and contest math. **Grok 4 Fast** ($0.20/$0.50, 2M context, 83.2% LiveCodeBench) is the cheap Western alternative if you want to avoid Chinese APIs entirely. **NVIDIA Nemotron 3 Super** (open weights, $0.30/$0.75 on DeepInfra, 81.2% LiveCodeBench, 1M context) is the best fully-open-recipe choice for STEM-coding self-hosters.

## Pricing and benchmark snapshot

| Model | License | Input/Output ($/M) | Context | SWE-V | SWE-Pro | LCB | Term-2 |
|---|---|---|---|---|---|---|---|
| **Kimi K2.6** | MIT-mod | 0.95 / 4.00 | 256K | 80.2 | **58.6** | 89.6 | 66.7 |
| **DeepSeek V4-Pro** | MIT | 1.74 / 3.48 | 1M | 80.6 | 55.4 | **93.5** | 67.9 |
| **DeepSeek V4-Flash** | MIT | **0.14 / 0.28** | 1M | 79.0 | — | 91.6 | 56.9 |
| **GLM-5.1** | MIT | 1.00–1.40 / 3.20–4.40 | 200K | 77.8 | 58.4 | — | **69.0** |
| **MiniMax M2.5** | open | 0.30 / 1.20 | 197K | 80.2 | ~50 | 78.0 | — |
| **Qwen3.6-Plus** | closed | 0.33 / 1.95 | **1M** | 78.8 | — | — | 61.6 |
| **Devstral 2 (123B)** | mod-MIT | 0.40 / 2.00 | 256K | 72.2 | — | — | — |
| **Devstral Small 2 (24B)** | Apache 2.0 | 0.10 / 0.30 | 256K | 68.0 | — | — | — |
| **grok-code-fast-1** | closed | 0.20 / 1.50 | 256K | 70.8\* | — | — | — |
| **Nemotron 3 Super** | NVIDIA OML | 0.30 / 0.75 | 1M | 60.5 | — | 81.2 | — |
| **Step-3.5-Flash** | Apache 2.0 | 0.10 / 0.30 | 256K | — | — | — | — |

\* xAI self-reported; vals.ai independent runs are ~12 points lower.

## What to actually do

If you're an Aider user on Go/Tarantool work and want one default, **set up Kimi K2.6 via Moonshot's API** (or Parasail for the cheapest reliable host) for agentic edits and `/architect` reasoning, **Qwen 2.5-Coder 32B in Ollama** for editor autocomplete, and keep **DeepSeek V4-Flash** as a $0.14/$0.28 fallback for one-shot algorithm questions and 1M-context whole-repo reads. That triple covers every category at total cost roughly 1/10th of an equivalent Claude Opus + Codex setup. If your work is sensitive about Chinese providers, the equivalent Western stack is **Devstral 2 → Codestral 22B → Grok 4 Fast**, accepting a ~5-point capability hit on hard agent tasks and the Codestral commercial license question.

Three forward-looking notes. **DeepSeek V4 is still preview** as of April 24 — expect a 0.1 patch within weeks that fixes the opencode tool-calling DNFs, after which it likely becomes the default agentic pick over Kimi K2.6 on price alone. **Grok 5 and Kimi K3 are both rumored for Q2 2026** but neither has shipped. And **Cursor's "secret sauce" Composer 2 is Kimi K2.5 with RL fine-tuning** — meaning if you can run K2.6 with a decent agent harness (Cline, OpenHands, Aider with custom prompts), you have access to roughly the same capability Cursor users are paying $20/month for, just without the IDE polish.
