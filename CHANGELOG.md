# Changelog

All notable changes to agents-maker are documented here.

Format: [Semantic Versioning](https://semver.org). Types: `Added`, `Changed`, `Fixed`, `Removed`.

---

## [1.0.2] - 2026-07-10

### Added
- **Clone-and-invoke named agents.** `npx … init` now installs Claude Code subagents (`.claude/agents/*`) and slash commands (`.claude/commands/*`) into the project root, so you can invoke agents by name: `/brain`, `/planpro`, `/orchestrate`, `/architect`, `/code`, `/execute`, `/ui`, `/ux`, `/review`, `/compress`. Non-destructive (never overwrites your own `.claude/` files).
- `agents/brain.md` — new brainstorming agent: explores the problem space, generates 3+ approaches with trade-offs, recommends one. Reuses `compare_approaches` + `suggest_next`.
- `agents/planpro.md` — new planning agent: turns a goal into a short, specific, dependency-ordered, verifiable plan file. Reuses `analyze_repo` + `compare_approaches`.
- `tools/generate_claude_agents.py` — generates the `.claude/` subagents + slash commands from the roster (frontmatter `name`/`description`/`tools`/`model`); ships a committed `claude/` template so `npx` (pure Node) installs without Python.
- `tools/compare_prompts.py` — proof-of-value harness: runs a naive vs structured prompt through the same model (CLI runner or `--api` with role separation); writes side-by-side outputs to `examples/proof/`.
- `tools/grade_proof.py` — blind adversarial grader: anonymized A/B, impartial judge model, scores completeness/correctness/actionability/structure.
- `generate_prompt.py --system-only` — emit just the task-scoped system prompt for an API `system` field.

### Changed
- **Token cost.** `--full` / `--system-only` now inline only the detected domain's agents + skills (`routing.domain_agents`) instead of the whole kit — ~30k → ~18–26k tokens; `compare_prompts --api` marks the system prompt `cache_control: ephemeral`.
- `generate_platform_configs.py` — new `claude_agents` step writes `.claude/`; `brain`/`planpro` added to the agkit metadata. `package.json` ships `claude/`.
- `system_prompt.md` regenerated to include `brain` + `planpro`; `README` gains a "Clone & Invoke" section and the site lists 10 agents.
- Test suite expanded to 65 checks (added generator tests); `validate_kit` remains 12/12.

---

## [1.0.1] - 2026-07-09

### Added
- `tools/_core.py` — shared primitives (YAML load, atomic write, source hash, shell-invocation) replacing helpers previously copy-pasted across five tools
- `tools/routing.py` — single source of truth for phase→domain agent routing, phase labels, and agent roles
- `site/public/og.png` — social-share/OpenGraph card (previously referenced in metadata but missing)
- `tools/generate_platform_configs.py` — new CLI tool: generates native config files for all major AI platforms from a single command; writes `CLAUDE.md` (Claude Code), `.github/copilot-instructions.md` (GitHub Copilot), `.cursor/rules` (Cursor), and `.agkit/agents.yaml` (Antigravity); supports `--platforms` (subset), `--dry-run`, and `--path` flags; all output files are atomic-written and safe to commit
- `tools/generate_claude_md.py` — new CLI tool: writes `CLAUDE.md` to project root for Claude Code integration; reads `config/project.yaml` + `project_state.md`; outputs domain, stack, phase, and agent routing; supports `--dry-run` and `--path` flags
- `skills/write_process_map.md` — new ops_process skill: numbered step table, RACI matrix, exception-handling table
- `skills/define_data_schema.md` — new data_analytics skill: ER sketch (ASCII), metric definition table, data dictionary
- `tools/domain_utils.py` — shared domain scoring module; eliminates duplicated scoring logic across 3 tools
- `.github/workflows/release.yml` — tag-triggered release workflow: validates, tests, and publishes GitHub Release with CHANGELOG body

### Fixed
- `tools/validate_kit.py` — now uses the shared `domain_utils.score_domain` instead of a private duplicate scorer (they could drift); `check_output_styles` corrected to read `workflows.generic_project_lifecycle` (was reading a nonexistent top-level key, so lifecycle phase/domain output styles were never validated)
- `context_loaders/project_summary.py` — `find_test_dirs` now skips `node_modules`/`.venv`/`.git` so large repos aren't fully traversed
- `token_optimization/compressor.py` — removed the dead `recency` relevance weight (was hardwired to `0.0`); folded into `lexical_overlap` so weights still sum to 1.0
- `pyproject.toml` — `build-backend` corrected to `setuptools.build_meta` (was a nonexistent module, breaking `pip install`)
- `bin/cli.js` + `package.json` `files` — `npx … init` now ships and copies `platforms/`, `docs/`, `examples/`, and `PROMPT_TEMPLATE.md`, so the zero-Python paste workflow the README advertises actually works after install
- `site` — added missing `<h1>` (hero headline was a `<p>`, hurting SEO/a11y); footer anchors (`#agents`/`#skills`/`#platforms`) now resolve to real section ids with `scroll-mt` offset for the fixed nav
- `tools/domain_utils.py` — wrong YAML key `detection_settings` corrected to `settings`; domain scoring now reads `confidence_threshold` and `ambiguity_threshold` from `config/domain_profiles.yaml` instead of silently using hardcoded defaults
- `tools/generate_prompt.py` — `[domain: X]` prefix now parsed explicitly before scoring, so all 8 domains can be force-routed (previously only `data_analytics` and `product_design` worked by coincidence); invalid domain names in prefix now print a warning instead of silently falling back
- `tools/generate_prompt.py` — session_count write to `project.yaml` is now atomic (`tempfile + os.replace`), matching `init_project.py`; previously a crash mid-write could corrupt the config file
- `tools/validate_kit.py` — `FAILURES` list now cleared at the start of `main()`, preventing stale failures accumulating across multiple calls in the same process
- `token_optimization/compressor.py` — `estimated_token_reduction_pct` now measures truncation savings only (retained files before vs after truncation), not file drops; previously dropping files inflated the reported reduction percentage
- `context_loaders/repo_tree.py` — `format_tree()` `root` parameter made optional (`None` default); it was declared but never used in the function body
- `tools/init_project.py` — removed dead `format_tree` import (imported but never called)
- `quickstart.sh`, `quickstart.ps1` — context loader example commands now include the required `--path .` argument; previously the shown commands would exit with a usage error

### Changed
- routing unified: `generate_prompt.py` and `generate_claude_md.py` now consume `tools/routing.py` (platform configs via aliases), removing three drifting hardcoded copies so the pasted prompt, `CLAUDE.md`, and platform configs agree
- shared helpers: `init_project.py`, `generate_prompt.py`, `generate_claude_md.py`, `generate_platform_configs.py`, `validate_kit.py` now use `tools/_core.py` instead of duplicated YAML-load / atomic-write / source-hash / shell-invocation helpers
- `README.md` — reframed the opening to describe agents-maker accurately as a structured prompting kit (not an agent runtime); `compressor.py` labeled a reference implementation with stub adapters
- `.github/workflows/validate.yml` — CI matrix expanded to `ubuntu`, `windows`, and `macos` (was Linux-only) across Python 3.9–3.12
- `site` — dependency-free scroll-reveal + count-up animations; extracted the duplicated section eyebrow into a component; removed a duplicate font `@import`; CTA copy "Clone once. Use forever." → "One command. Any project."
- `agents/orchestrator.md` — added domain-phase mapping precedence rule, Phase Exit Criteria table, Phase 5 Handoff procedure spec, and Companion Block Schema
- `agents/code_agent.md` — standardized phase nomenclature to "Phase N — Name (`phase_key`)" format
- `agents/ux_agent.md` — standardized phase nomenclature to "Phase N — Name (`phase_key`)" format
- `agents/architect_agent.md` — standardized phase nomenclature to "Phase N — Name (`phase_key`)" format
- `tools/init_project.py` — added `--platforms` flag: runs `generate_platform_configs` for all 4 platforms after bootstrap; added `--claude-md` flag (Claude Code only, kept for backward compatibility); tip in non-flag summary now points to `generate_platform_configs.py`
- `config/agents.yaml` — registered `write_process_map` on `execution_agent`, `define_data_schema` on `code_agent`; added routing_priority comment clarifying when it applies vs. domain-phase mapping
- `token_optimization/output_styles.md` — added Token Cost Tier Definitions table (Low/Medium/High)
- `tools/init_project.py` — atomic file writes via `tempfile + os.replace`; delegates domain scoring to `domain_utils`; YAML injection hardening for project_name and stack fields; source hash embedded in system_prompt.md header
- `tools/generate_prompt.py` — delegates domain scoring to `domain_utils`
- `tools/validate_kit.py` — check 12: system_prompt.md freshness (source hash comparison)
- `platforms/claude.md` — added Option C for Claude.ai free tier (no Projects access)
- `platforms/openai.md` — added Companion Mode subsection with Chat Completions example
- `requirements.txt` — version cap: `pyyaml>=6.0,<8`

---

## [1.0.0] — 2026-06-27

Initial public release.

### Added

**Core kit**
- 8 specialist agents: Orchestrator, Architect/Planner, Code Agent, Execution Agent, UI Agent, UX Agent, Reviewer Agent, Compression Agent
- 10 skill cards (initial): `analyze_repo`, `design_api`, `review_code`, `review_layout`, `improve_copy`, `write_tests`, `summarize_history`, `suggest_next`, `compare_approaches`, `animated_website`
- 8 built-in domains: `software`, `content`, `research`, `data_analytics`, `product_design`, `marketing`, `ops_process`, `general`
- 6-phase lifecycle: Task Framing → Requirements → Solution Design → Implementation → Review → Handoff

**Configuration**
- `config/agents.yaml` — agent registry with routing tags, cost tiers, skill assignments
- `config/domain_profiles.yaml` — domain detection signals and agent mappings
- `config/token_policies.yaml` — compression and verbosity presets per phase and domain

**Python tooling**
- `tools/init_project.py` — one-time project bootstrap with `--update` flag
- `tools/generate_prompt.py` — daily prompt generator with `--phase`, `--full`, `--compress` flags
- `tools/validate_kit.py` — 8-check integrity validator
- `context_loaders/project_summary.py` — stack and structure detection
- `context_loaders/repo_tree.py` — annotated directory tree generator
- `context_loaders/file_chunker.py` — large-file token splitter
- `token_optimization/compressor.py` — token budget enforcement engine

**Zero-Python workflow**
- `system_prompt.md` — pre-assembled system prompt (all 8 agents + 10 skills at launch, ~24K tokens)
- `PROMPT_TEMPLATE.md` — fillable session message template

**Documentation**
- `README.md` — full overview with context guide, domain reference, lifecycle docs
- `docs/architecture.md` — agent graph, context flow, design decisions
- `docs/workflows.md` — lifecycle phases and interface contracts
- `docs/domains.md` — domain plugin schema and built-in domain cards
- `platforms/claude.md` — Claude Projects and API integration guide
- `platforms/openai.md` — OpenAI Chat Completions, Assistants, and Agents SDK guide
- `platforms/antigravity.md` — Antigravity pipeline mapping guide
- `examples/generic_project_lifecycle.md` — two full annotated lifecycle walkthroughs (software + research)

**Project packaging**
- `LICENSE` — MIT
- `CONTRIBUTING.md` — contribution guide
- `requirements.txt` — `pyyaml>=6.0`
- `.gitignore` — excludes project-specific state files

---

## How to update

```bash
git pull origin main
python tools/validate_kit.py        # verify integrity after any update
python tools/init_project.py --update   # regenerate system_prompt.md if agents or skills changed
```
