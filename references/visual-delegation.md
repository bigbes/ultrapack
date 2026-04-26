# Visual delegation

When you receive an image, screenshot, diagram, mockup, or PDF — either attached by the user or referenced by absolute path in your input — dispatch `@look-at` to read it. Do not guess at contents and do not narrate "I cannot see images"; delegate.

Reasons to centralize on `@look-at`:

1. Some models in this pack (DeepSeek V4-Flash, Kimi K2.6, GLM family) are not vision-capable at all — they will silently fail on images.
2. Even when your model is vision-capable (GPT-5.x family), `@look-at` runs on the cheapest vision-native model in the routing (`opencode/gemini-3-flash`), so delegating is cheaper and faster.
3. One agent doing all visual analysis means consistent output shape — the calling agent can rely on the same description format regardless of which model is behind it.

## When to delegate

- The user attaches an image (PNG, JPG, GIF, WebP, SVG-as-bitmap) or PDF.
- The user references a file path that ends in an image or PDF extension.
- The task involves a diagram, architecture sketch, error screenshot, design mockup, chart, or scanned document.
- A web page or doc you fetched contains a diagram or screenshot whose contents matter to the answer.

## When not to delegate

- The file is text (`.md`, `.txt`, source code, JSON, YAML, CSV) — read it directly.
- The image is decorative and the answer doesn't depend on its contents.
- You have already received the description of the same image in this dispatch.

## How to dispatch

Send `@look-at` exactly what you need:

```
@look-at /absolute/path/to/file.png
What does this error message say, and what stack trace is visible?
```

Or for comparison:

```
@look-at /absolute/path/to/before.png /absolute/path/to/after.png
What changed between these two screenshots?
```

Use the result verbatim or quote the relevant lines. Do not re-describe the image in your own words beyond what `@look-at` reported — it saw the pixels, you didn't.

## Failure mode to avoid

Silent failure. If your model cannot see an image and you don't delegate, you either fabricate a description or refuse the task — both are worse than a one-step delegation. When in doubt, delegate.
