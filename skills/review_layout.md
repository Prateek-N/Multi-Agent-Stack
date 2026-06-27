# Skill: review_layout

## Description

Critique the visual hierarchy, spacing, responsive behavior, and accessibility of a UI layout. Input can be a component tree, file snippet, or plain-text screen description. Output is a structured table of findings with severity and specific recommendations.

---

## When to invoke

- The UI Agent needs a baseline assessment before making layout recommendations.
- The UX Agent identifies a layout-level problem (not a flow problem) and defers it.
- A design review specifically calls out visual or accessibility issues.

---

## Input expectations

| Input | Required | Description |
|---|---|---|
| `screen_description` | Yes | Component tree, file snippet, or plain-text description of the layout |
| `framework` | No | `React` \| `Vue` \| `HTML/CSS` \| `Svelte` \| `other` |
| `target_devices` | No | `desktop` \| `mobile` \| `both` (default: `both`) |
| `accessibility_level` | No | `A` \| `AA` \| `AAA` \| `none` (default: `AA`) |
| `existing_tokens` | No | Design token values in scope (colors, spacing scale) |

**If required input is missing:**
- `screen_description` — ask: "Please paste a component tree, file snippet, or describe the layout you want reviewed." Do not produce findings without it.
- `framework` — infer from component syntax (JSX → React, SFC → Vue, `.svelte` → Svelte); if indeterminate, note "Framework assumed: [X] — correct if wrong."
- `target_devices` — default to `both`.
- `accessibility_level` — default to `AA`.
- `existing_tokens` — proceed without; note that token-specific recommendations (e.g., "use spacing-4") cannot be made and generic values will be suggested instead.

---

## Output format

```
## Layout Review: <screen/component name>

**Summary**: N critical, N high, N medium, N low

### Visual Hierarchy

| Severity | Element | Issue | Recommendation |
|---|---|---|---|
| high | Page title | Same font size as body text | Increase to heading level; use h1 |
| medium | CTA button | Low contrast against background | Use primary brand color |

### Spacing

| Severity | Element | Issue | Recommendation |
|---|---|---|---|
| medium | Card grid | Inconsistent gap (12px and 16px mixed) | Standardize to spacing-4 (16px) |

### Responsive Behavior

| Severity | Breakpoint | Issue | Recommendation |
|---|---|---|---|
| high | Mobile (<768px) | Table overflows viewport | Use horizontal scroll or card layout |

### Accessibility

| Severity | Element | WCAG criterion | Issue | Fix |
|---|---|---|---|---|
| critical | Icon button | 1.1.1 Non-text content | No aria-label | Add `aria-label="<action>"` |
| high | Link color | 1.4.3 Contrast | 2.8:1 ratio (AA requires 4.5:1) | Darken link color |

### Positive Findings
- <bullet>
```

Omit sections with no findings.

---

## Token cost tier

**Low.** Typical output: 200–400 tokens. Does not require reading large file trees.

Compression hint: if scoped to a single component, this skill is already token-light. No further compression needed.

---

## Notes

- WCAG criterion references should use the format `N.N.N Title`.
- Do not flag every spacing inconsistency as `high`. Reserve `high` for issues that visually break the layout or prevent task completion.
- If the input is text-only (no actual CSS/tokens), note: "Review based on description only — actual values may differ."
