---
description: Explain a diff by behavior and review order. Pass a revision, path, or leave empty for current checkout changes.
agent: diff-explainer
---

Explain this diff scope: `$ARGUMENTS`

If `$ARGUMENTS` is empty, explain the current checkout changes:
- tracked changes from `git diff`
- staged changes from `git diff --cached`
- untracked files from `git ls-files --others --exclude-standard`

Focus on what changed, why it matters, and the best file order for understanding it. Do not perform a defect-oriented review unless the user explicitly asks.
