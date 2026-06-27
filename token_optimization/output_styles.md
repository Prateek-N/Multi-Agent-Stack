# Output Styles

## Token Cost Tier Definitions

Used in skill cards and [Companion] block next-step options to set user expectations:

| Tier | Approx. output tokens | Typical context needed |
|------|----------------------|------------------------|
| **Low** | < 500 | Conversation only — no file reads required |
| **Medium** | 500–1,500 | 3–5 source files needed; normal session size |
| **High** | > 1,500 | Full repo scan or large diff; use `project_summary.py` first |

These tiers are intentionally coarse — they indicate session preparation cost, not response quality.

---

## Purpose

Named verbosity presets that control the format and length of agent responses. Each style is referenced by name in `config/token_policies.yaml` and in agent spec default settings.

Full style definitions (rules, token limits, format templates) live in `config/token_policies.yaml` under `output_styles:`. This file is the usage guide — not the source of truth.

---

## Style Quick Reference

| Style key | Best for |
|---|---|
| `concise_bullets` | UX critique, status updates, compression reports |
| `standard` | General Q&A, workflow explanations, mixed responses |
| `detailed_with_code` | Implementation, refactoring, test generation |
| `design_brief` | Architecture outputs, API contracts, ADRs |
| `review_checklist` | Code reviews, layout reviews, security audits |
| `qa_brief` | Phase 0 task framing — numbered question list |
| `requirements_spec` | Phase 1 requirements gathering |
| `solution_design` | Phase 2 solution design output |
| `implementation_slice` | Phase 3 incremental delivery |
| `critique_summary` | Phase 4 severity-rated review |
| `handoff_package` | Phase 5 packaging and handoff |

---

## How to Apply a Style

**In conversational use** — append to the agent's system prompt or first message:

```
Output style: <style_name>
Max response length: <max_response_tokens> tokens
```

**In programmatic use** — via `compressor.py`:

```python
policy = token_policies.get_workflow_policy("ux_critique")
style = policy.output_style  # → "concise_bullets"
style_config = token_policies.get_output_style(style)
```

The user can override for any turn: "Use `<style_name>` for this response."

---

## Style Selection by Workflow

| Workflow | Phase | Default style |
|---|---|---|
| `code_review` | — | `review_checklist` |
| `feature_implementation` | — | `detailed_with_code` |
| `feature_design` | — | `design_brief` |
| `ui_improvement` | — | `design_brief` |
| `ux_critique` | — | `concise_bullets` |
| `refactoring` | — | `detailed_with_code` |
| `test_generation` | — | `detailed_with_code` |
| `generic_project_lifecycle` | task_framing | `qa_brief` |
| `generic_project_lifecycle` | requirements | `requirements_spec` |
| `generic_project_lifecycle` | solution_design | `solution_design` |
| `generic_project_lifecycle` | implementation | `implementation_slice` |
| `generic_project_lifecycle` | review_refinement | `critique_summary` |
| `generic_project_lifecycle` | handoff | `handoff_package` |
