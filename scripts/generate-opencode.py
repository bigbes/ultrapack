#!/usr/bin/env python3
"""Generate OpenCode files from the Claude Code ultrapack plugin."""

from __future__ import annotations

import re
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / "plugins" / "up"
OUT = ROOT / ".opencode"

GENERATED_DIRS = [
    OUT / "agents",
    OUT / "commands",
    OUT / "skills",
    OUT / "references",
]

COMMAND_NAMES = {
    "make": "make",
    "try": "try",
    "step-back": "step-back",
    "summary": "summary",
    "reflect": "reflect",
}

READONLY_AGENTS = {
    "explorer",
    "researcher",
    "reviewer",
    "summarizer",
    "finder",
    "librarian",
    "oracle",
    "diff-explainer",
}

WEB_AGENTS = {
    "researcher",
    "librarian",
    "oracle",
}


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + "\n", encoding="utf-8")


def split_frontmatter(text: str) -> tuple[dict[str, str], str]:
    if not text.startswith("---\n"):
        return {}, text
    end = text.find("\n---\n", 4)
    if end == -1:
        return {}, text
    raw = text[4:end]
    body = text[end + 5 :]
    data: dict[str, str] = {}
    for line in raw.splitlines():
        if not line.strip() or line.startswith(" "):
            continue
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        data[key.strip()] = value.strip()
    return data, body.lstrip()


def frontmatter(fields: list[tuple[str, str | list[str]]]) -> str:
    lines = ["---"]
    for key, value in fields:
        if isinstance(value, list):
            lines.append(f"{key}:")
            lines.extend(value)
        else:
            lines.append(f"{key}: {value}")
    lines.append("---")
    lines.append("")
    return "\n".join(lines)


def rewrite_common(text: str) -> str:
    replacements = {
        "/up:make": "/make",
        "/up:try": "/try",
        "/up:step-back": "/step-back",
        "/up:summary": "/summary",
        "/up:reflect": "/reflect",
        "up:udesign": "udesign",
        "up:uplan": "uplan",
        "up:uexecute": "uexecute",
        "up:uverify": "uverify",
        "up:ureview": "ureview",
        "up:udebug": "udebug",
        "up:udocument": "udocument",
        "up:test-driven-development": "test-driven-development",
        "up:git-worktrees": "git-worktrees",
        "up:handsoff": "handsoff",
        "up:explorer": "@explorer",
        "up:implementer": "@implementer",
        "up:researcher": "@researcher",
        "up:reviewer": "@reviewer",
        "up:summarizer": "@summarizer",
        "up:ureviewer": "@reviewer",
        "plugins/up/skills/_brevity.md": ".opencode/references/brevity.md",
        "plugins/up/skills/_principles.md": ".opencode/references/principles.md",
        "Task tool": "OpenCode subagent invocation",
        "subagent_type:": "agent:",
        "TodoWrite": "an explicit checklist",
        "WebSearch": "web search",
        "WebFetch": "web fetch",
        "Glob, Grep, Read": "file search, text search, file reads",
        "inline Grep/Read": "inline search/read",
        "quick Grep": "quick text search",
        "Sonnet 4.6": "the configured implementation model",
        "Haiku 4.5": "the configured lightweight model",
        "on Sonnet": "using the configured implementation model",
        "on Opus": "in the primary agent",
        "Claude Code reads": "OpenCode reads",
        "scaffolding Claude used": "scaffolding the assistant used",
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    text = re.sub(r"\bup:([a-z0-9-]+)\b", r"\1", text)
    return text


def rewrite_reflect(body: str) -> str:
    body = rewrite_common(body)
    body = body.replace(
        "CLAUDE.md, memory, or project docs",
        "AGENTS.md, approved memory, or project docs",
    )
    body = body.replace(
        "CLAUDE.md / memory / docs",
        "AGENTS.md / approved memory / docs",
    )
    body = body.replace(
        "**CLAUDE.md (project or global)** — project-wide or user-wide conventions, preferences, things to always or never do",
        "**AGENTS.md** — project-wide agent guidance, conventions, preferences, things to always or never do",
    )
    body = body.replace(
        "**Memory system** — references to external systems, user preferences, project context that applies across sessions",
        "**Approved memory system** — only if OpenCode/Amp/global memory is explicitly configured or the user approves writing outside the repo",
    )
    body = body.replace(
        "Anything already captured in CLAUDE.md, existing docs, or memory",
        "Anything already captured in AGENTS.md, CLAUDE.md, existing docs, or approved memory",
    )
    body = body.replace(
        "Don't commit to CLAUDE.md without showing the user the proposed diff",
        "Show proposed AGENTS.md or CLAUDE.md changes before applying them",
    )
    body = body.replace(
        "Memory edits can happen directly (per the auto-memory guidelines)",
        "Do not write user/global memory unless the location is configured and the user has approved that behavior",
    )
    insert = """\n## OpenCode routing\n\nPrefer `AGENTS.md` for portable project-wide agent guidance. Use `CLAUDE.md` only when preserving Claude compatibility or when the repo already treats it as canonical. If both are present, avoid duplicating full guidance; make one canonical and let the other point to it when possible.\n"""
    return body.replace("## Process\n", insert + "\n## Process\n")


def rewrite_doc_destinations(body: str) -> str:
    body = body.replace(
        "`CLAUDE.md` (project-wide agent guidance)",
        "`AGENTS.md` (project-wide agent guidance; keep `CLAUDE.md` as compatibility guidance only when the repo uses it)",
    )
    body = body.replace(
        "New conventions, invariants, or principles that should be global → update `CLAUDE.md`",
        "New conventions, invariants, or principles that should be global → update `AGENTS.md` first, then `CLAUDE.md` only for compatibility",
    )
    body = body.replace(
        'e.g. "README: fixed install instructions; CLAUDE.md: no change"',
        'e.g. "README: fixed install instructions; AGENTS.md: no change"',
    )
    body = body.replace(
        "check `CLAUDE.md` for a preference",
        "check `AGENTS.md` and then `CLAUDE.md` for a preference",
    )
    body = body.replace(
        "CLAUDE.md / AGENTS.md / GEMINI.md",
        "AGENTS.md / CLAUDE.md / GEMINI.md",
    )
    body = body.replace(
        "## CLAUDE.md / AGENTS.md",
        "## AGENTS.md / CLAUDE.md",
    )
    return body


def rewrite_summary(body: str) -> str:
    body = rewrite_common(body)
    body = body.replace(
        "Prepare a handoff summary so another agent session can continue this work without the current conversation. Drafting is delegated to the `@summarizer` subagent (pinned to Sonnet) so the expensive main-session model doesn't write the long structured prose. The subagent locates this session's JSONL transcript on disk using a distinctive phrase you pass to it, then reads it directly.",
        "Prepare a handoff summary so another OpenCode session can continue this work from repo state and the currently visible conversation. Drafting may be delegated to `@summarizer`, but do not rely on product-specific transcript paths.",
    )
    body = re.sub(
        r"### 1\. Pick a distinctive phrase.*?### 4\. Receive the draft",
        """### 1. Detect the active task file\n\nRun the equivalent of:\n\n```bash\nls -t docs/tasks/*.md 2>/dev/null | head\n```\n\nThe active task file is the most-recently-modified entry whose `**Status:**` header is not `done`. If none qualify, use `null`.\n\n### 2. Gather repo state\n\nRead `git status`, staged and unstaged diffs, recent commits, and the active task file if present. Include only details needed for a fresh session to continue.\n\n### 3. Draft the summary\n\nYou may delegate to `@summarizer`, passing the working directory and active task file path. The summarizer must use visible context plus repo state only; it must not search product-specific transcript stores.\n\n### 4. Present the draft""",
        body,
        flags=re.S,
    )
    body = body.replace(
        "The subagent greps JSONL files under the encoded-cwd projects dirs to locate this session's transcript, then reads it. Do not paste the transcript into the prompt.\n\n",
        "",
    )
    body = body.replace(
        "If the subagent reports it couldn't uniquely locate the JSONL (zero matches or multiple matches on both phrases), pick a different phrase and re-dispatch.\n\n",
        "",
    )
    body = body.replace(
        "Subagent locates the JSONL, drafts the summary; main session picks the phrase, asks, and writes.",
        "Subagent drafts from visible context and repo state; main session asks and writes.",
    )
    body = body.replace(
        "Don't restate `CLAUDE.md`.",
        "Don't restate `AGENTS.md` or `CLAUDE.md`.",
    )
    body = body.replace(
        "using Edit (append) or Write (new file)",
        "by appending to the chosen file or creating the chosen file",
    )
    body = body.replace("Claude", "OpenCode")
    return body


def command_body(name: str, body: str) -> str:
    body = rewrite_reflect(body) if name == "reflect" else rewrite_summary(body) if name == "summary" else rewrite_common(body)
    body = rewrite_doc_destinations(body)
    if name == "make":
        body = body.replace(
            "The user's description of the task follows the command.",
            "Use `$ARGUMENTS` as the task description.",
        )
    return body


def agent_permission(agent: str) -> list[str]:
    if agent in READONLY_AGENTS:
        webfetch = "ask" if agent in WEB_AGENTS else "deny"
        return [
            "  edit: deny",
            "  bash:",
            '    "*": ask',
            '    "git diff*": allow',
            '    "git log*": allow',
            '    "git show*": allow',
            '    "git status*": allow',
            '    "git grep*": allow',
            '    "rg *": allow',
            '    "ls *": allow',
            '    "cat *": allow',
            '    "sed *": allow',
            '    "nl *": allow',
            '    "wc *": allow',
            f"  webfetch: {webfetch}",
        ]
    return [
        "  edit: ask",
        "  bash: ask",
        "  webfetch: deny",
    ]


def generate_agents() -> None:
    for source in sorted((PLUGIN / "agents").glob("*.md")):
        meta, body = split_frontmatter(read(source))
        name = source.stem
        if name == "summarizer":
            write(OUT / "agents" / source.name, summarizer_agent())
            continue
        fields: list[tuple[str, str | list[str]]] = [
            ("description", rewrite_common(meta.get("description", ""))),
            ("mode", "subagent"),
            ("permission", agent_permission(name)),
        ]
        write(OUT / "agents" / source.name, frontmatter(fields) + rewrite_common(body))
    write(OUT / "agents" / "librarian.md", librarian_agent())
    write(OUT / "agents" / "finder.md", finder_agent())
    write(OUT / "agents" / "oracle.md", oracle_agent())
    write(OUT / "agents" / "diff-explainer.md", diff_explainer_agent())


def generate_commands() -> None:
    for source in sorted((PLUGIN / "commands").glob("*.md")):
        name = source.stem
        meta, body = split_frontmatter(read(source))
        description = rewrite_common(meta.get("description", ""))
        if name == "reflect":
            description = "Reflect on the current dialogue, extract what's worth keeping, and route each learning to AGENTS.md, approved memory, project docs, or the task file."
        elif name == "summary":
            description = "Produce a handoff summary from visible context and repo state so another OpenCode session can continue."
        fields: list[tuple[str, str | list[str]]] = [
            ("description", description),
        ]
        write(OUT / "commands" / f"{COMMAND_NAMES[name]}.md", frontmatter(fields) + command_body(name, body))
    write(OUT / "commands" / "explain-diff.md", explain_diff_command())


def generate_skills() -> None:
    for skill in sorted((PLUGIN / "skills").iterdir()):
        if not skill.is_dir():
            continue
        source = skill / "SKILL.md"
        if not source.exists():
            continue
        text = rewrite_doc_destinations(rewrite_common(read(source)))
        write(OUT / "skills" / skill.name / "SKILL.md", text)
    write(OUT / "references" / "brevity.md", rewrite_common(read(PLUGIN / "skills" / "_brevity.md")))
    write(OUT / "references" / "principles.md", rewrite_common(read(PLUGIN / "skills" / "_principles.md")))


def librarian_agent() -> str:
    return """---
description: Deep codebase understanding across large repos, multiple repos, upstream source, and commit history. Use when explorer/finder are too shallow.
mode: subagent
permission:
  edit: deny
  bash:
    "*": ask
    "git diff*": allow
    "git log*": allow
    "git show*": allow
    "git status*": allow
    "git grep*": allow
    "rg *": allow
    "ls *": allow
    "cat *": allow
    "sed *": allow
    "nl *": allow
    "wc *": allow
    "gh *": ask
  webfetch: ask
---

You are the Librarian, a specialized codebase understanding agent for large, complex, and multi-repository questions.

## Scope

Use this agent when the user or main agent needs:
- A feature explained end-to-end across modules or repositories
- Relationship mapping across services, packages, clients, or generated code
- Upstream framework or dependency source investigation
- Commit-history context for why behavior changed
- A shareable architecture explanation with file links and optional diagrams

Do not implement changes. Do not turn the answer into a code review unless the prompt asks for review.

## Diagram Guidance

Mermaid diagrams are optional. Use one only when it replaces a dense relationship explanation, such as:
- A request path crossing services, packages, or repositories
- A lifecycle or state transition with more than three meaningful states
- Ownership boundaries between generated code, SDKs, APIs, and storage
- A dependency graph where prose would become a long list of arrows

Avoid diagrams for simple call chains, small local flows, or anything that would be clearer as three bullets. If you include a diagram, keep it small enough to inspect quickly and introduce it with one sentence explaining what question it answers.

## Process

1. Identify the exact question and repositories/paths in scope.
2. Search broadly, then read the load-bearing files thoroughly.
3. Trace entry points, core flow, data/contracts, side effects, and external boundaries.
4. Check commit history when evolution matters.
5. Use web or repository tools only when local information is insufficient.
6. Create a Mermaid diagram only when the diagram is clearer than prose.

## Output

Answer directly. Be comprehensive but focused.

Include:
- Repositories and branches inspected
- Entry points and flow
- Key files with links
- Important contracts, schemas, or APIs
- Commit-history findings when relevant
- Mermaid diagram when useful, with a short explanation of what it shows
- Caveats for anything not inspected or unavailable

## Rules

- Read-only.
- Every concrete file/repo claim must be backed by a link or command evidence.
- Prefer source code over docs when behavior matters.
- Do not mention tool names.
- If private remote access is unavailable, say so and continue with local/public evidence.
"""


def finder_agent() -> str:
    return """---
description: Fast code search agent that returns relevant files and line ranges only. Use before deeper exploration or implementation scoping.
mode: subagent
permission:
  edit: deny
  bash:
    "*": ask
    "git grep*": allow
    "rg *": allow
    "find *": allow
    "ls *": allow
    "sed *": allow
    "nl *": allow
    "cat *": allow
    "wc *": allow
  webfetch: deny
---

You are a fast, parallel code search agent.

## Task

Find files and line ranges relevant to the user's query. Return locations, not an essay.

## Strategy

- Search breadth-first with diverse scoped queries.
- Prefer source files over docs unless docs are the target.
- For "all", "every", "each", "call sites", or "usages", find complete coverage.
- Use exact text search first for symbols, routes, flags, config keys, and error messages.
- Use conceptual search terms for behavior-level questions.
- Stop when you have enough locations for the main agent to act.

## Output

```markdown
<1-2 line finding>

Relevant files:
- [relative/path.ext#Lx-Ly](file:///absolute/path.ext#Lx-Ly)
```

## Rules

- Read-only.
- No implementation plan.
- No architecture walkthrough.
- No fixes.
- Include generous line ranges that capture complete functions, classes, or config blocks.
"""


def diff_explainer_agent() -> str:
    return """---
description: Explain diffs by behavior and review order. Use when the user wants to understand changes, not review for defects.
mode: subagent
permission:
  edit: deny
  bash:
    "*": ask
    "git diff*": allow
    "git status*": allow
    "git log*": allow
    "git show*": allow
    "git ls-files*": allow
    "rg *": allow
    "sed *": allow
    "nl *": allow
    "cat *": allow
  webfetch: deny
---

You explain code diffs clearly.

## Goal

Produce a walkthrough of what changed and why it matters. This is not a code review; do not hunt for defects unless a risk is necessary to understand the change.

## Process

1. Determine the requested diff scope. If none is provided, use current checkout changes and include untracked files.
2. Identify the behavior before and after.
3. Choose the best read order, starting with foundational files: schemas, core types, data flow, public APIs, then callers and tests.
4. Walk non-trivial hunks in that order.
5. Mention interactions between files when they explain the change.

## Output

Start with:

```markdown
**Overview:** <before/after behavior in 2-4 sentences>
```

Then include:
- Read first: files in the order a reviewer should inspect them, each with a five-word reason
- Walkthrough: grouped by behavior or component, not raw diff order
- Risks or follow-up checks only when materially relevant

## Rules

- Read-only.
- Prefer concise bullets.
- Avoid line-by-line mechanics when the code is obvious.
- Link files and line ranges.
- If the diff is huge, stop and ask for a narrower scope.
"""


def oracle_agent() -> str:
    return """---
description: Senior engineering advisor for architecture, planning, deep debugging strategy, and tradeoff decisions. Use when the main agent needs a concise second opinion before acting.
mode: subagent
permission:
  edit: deny
  bash:
    "*": ask
    "git diff*": allow
    "git log*": allow
    "git show*": allow
    "git status*": allow
    "rg *": allow
    "ls *": allow
    "cat *": allow
    "sed *": allow
    "nl *": allow
    "wc *": allow
  webfetch: ask
---

You are the Oracle, a senior engineering advisor with strong reasoning and a simplicity-first bias.

You are invoked when the main agent needs a focused recommendation for a hard decision. You may not ask follow-up questions, so work from the prompt and available evidence. If the input is insufficient, state the missing fact and give the safest bounded recommendation.

## Use When

- Architecture or API design has real tradeoffs
- A plan needs sanity checking before execution
- Debugging has reached a structural blocker
- Performance, security, reliability, or migration risk matters
- The agent may be over-engineering or splitting work incorrectly

## Do Not Use For

- Simple file search
- Routine implementation
- Long codebase walkthroughs
- Defect-oriented code review when `@reviewer` is the better fit

## Operating Principles

- Default to the simplest viable solution that satisfies stated constraints.
- Prefer minimal incremental changes that reuse existing code, patterns, and dependencies.
- Optimize for maintainability, developer time, and risk before theoretical scalability.
- Apply YAGNI and KISS.
- Give one primary recommendation.
- Offer at most one alternative when the tradeoff is materially different.
- Include a rough effort signal: S <1h, M 1-3h, L 1-2d, XL >2d.
- Name the signal that would justify revisiting with a more complex approach.

## Output

Use this shape:

```markdown
## TL;DR
<1-3 sentences>

## Recommended Path
<numbered steps or short checklist>

## Rationale
<brief tradeoffs>

## Risks
<key caveats and mitigations>

## Revisit When
<concrete triggers for a more advanced path>
```

Omit sections only when the answer is trivial.

## Rules

- Read-only.
- No implementation unless explicitly asked.
- No broad option matrix.
- Do not invent repository roots or facts not in evidence.
- If reviewing code, report only important actionable issues.
"""


def explain_diff_command() -> str:
    return """---
description: Explain a diff by behavior and review order. Pass a revision, path, or leave empty for current checkout changes.
agent: diff-explainer
---

Explain this diff scope: `$ARGUMENTS`

If `$ARGUMENTS` is empty, explain the current checkout changes:
- tracked changes from `git diff`
- staged changes from `git diff --cached`
- untracked files from `git ls-files --others --exclude-standard`

Focus on what changed, why it matters, and the best file order for understanding it. Do not perform a defect-oriented review unless the user explicitly asks.
"""


def summarizer_agent() -> str:
    return """---
description: Draft a session-handoff summary from visible context and repo state. Never writes to disk.
mode: subagent
permission:
  edit: deny
  bash:
    "*": ask
    "git status*": allow
    "git diff*": allow
    "git log*": allow
    "git ls-files*": allow
    "ls *": allow
    "rg *": allow
    "sed *": allow
    "cat *": allow
  webfetch: deny
---

You draft a handoff summary so a fresh OpenCode session can continue without the full current conversation.

## What you receive

- Working directory
- Active task file path, or `null`
- Any visible conversation context the dispatcher chooses to include

If required input is missing, say exactly what is missing. Do not invent.

## Process

1. Verify the working directory.
2. Read the active task file if one was provided.
3. Gather repo state with read-only git commands: status, staged/unstaged diffs, untracked files, and recent commits.
4. Use only visible context plus repo state. Do not search product-specific transcript stores.
5. Draft the summary. Do not write to disk.

## Output

Start with exactly:

```text
Draft summary below — main session decides destination.
```

Then include:

- Goal
- Problem
- Infrastructure / Environment
- Current state
- Active blocker
- Key files
- What to do next
- Gotchas

Omit sections only when genuinely irrelevant.

## Rules

- Read-only.
- Concrete paths and commands over prose.
- Include only information that cannot be recovered cheaply from code or git history.
- State uncertainty explicitly.
"""


def clean_generated_dirs() -> None:
    for path in GENERATED_DIRS:
        if path.exists():
            shutil.rmtree(path)
        path.mkdir(parents=True, exist_ok=True)


def main() -> None:
    clean_generated_dirs()
    generate_agents()
    generate_commands()
    generate_skills()
    files = []
    for path in GENERATED_DIRS:
        files.extend(sorted(p.relative_to(ROOT) for p in path.rglob("*") if p.is_file()))
    for path in files:
        print(path)


if __name__ == "__main__":
    main()
