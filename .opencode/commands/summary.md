---
description: Produce a handoff summary from visible context and repo state so another OpenCode session can continue.
---
# /summary

Prepare a handoff summary so another OpenCode session can continue this work from repo state and the currently visible conversation. Drafting may be delegated to `@summarizer`, but do not rely on product-specific transcript paths.

## Process

### 1. Detect the active task file

Run the equivalent of:

```bash
ls -t docs/tasks/*.md 2>/dev/null | head
```

The active task file is the most-recently-modified entry whose `**Status:**` header is not `done`. If none qualify, use `null`.

### 2. Gather repo state

Read `git status`, staged and unstaged diffs, recent commits, and the active task file if present. Include only details needed for a fresh session to continue.

### 3. Draft the summary

You may delegate to `@summarizer`, passing the working directory and active task file path. The summarizer must use visible context plus repo state only; it must not search product-specific transcript stores.

### 4. Present the draft

The subagent returns prose beginning with `Draft summary below — main session decides destination.` followed by the eight-section summary (Goal / Problem / Infrastructure / Current state / Active blocker / Key files / What to do next / Gotchas).

Quote the draft verbatim back to the user. Do not rewrite — if something is missing, ask the subagent to revise rather than silently patching on the main model.

### 5. Ask the user where to put it

<required>
After showing the draft, ask:

1. Append to the current task file's `## Conclusion` as a `### Summary — YYYY-MM-DD` subsection (provide the detected `docs/tasks/<slug>.md` path).
2. Create a new file at `docs/tasks/summary-<new-slug>.md` (propose a slug based on the current work).

Pick the destination based on the user's answer. Do not write anywhere without confirmation.
</required>

If no active task file was detected in step 2, option 1 is unavailable — only offer option 2.

### 6. Write

Perform the write in the main session by appending to the chosen file or creating the chosen file. The subagent has no write tools.

## Rules

- Subagent drafts from visible context and repo state; main session asks and writes.
- Concrete: exact commands, exact paths, exact error messages.
- Terse: bullets over prose. No filler.
- Include only info that can't be derived from code or git history. Don't restate `AGENTS.md` or `CLAUDE.md`.
- Never write without confirmation.
