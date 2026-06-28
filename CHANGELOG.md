# Changelog

All notable changes to agents-maker are documented here.

Format: [Semantic Versioning](https://semver.org). Types: `Added`, `Changed`, `Fixed`, `Removed`.

---

## [Unreleased]

### Added
- `tools/generate_claude_md.py` — new CLI tool: writes `CLAUDE.md` to project root for Claude Code integration; reads `config/project.yaml` + `project_state.md`; outputs domain, stack, phase, and agent routing; supports `--dry-run` and `--path` flags
- `skills/write_process_map.md` — new ops_process skill: numbered step table, RACI matrix, exception-handling table
- `skills/define_data_schema.md` — new data_analytics skill: ER sketch (ASCII), metric definition table, data dictionary
- `tools/domain_utils.py` — shared domain scoring module; eliminates duplicated scoring logic across 3 tools
- `.github/workflows/release.yml` — tag-triggered release workflow: validates, tests, and publishes GitHub Release with CHANGELOG body

### Fixed
- `tools/domain_utils.py` — wrong YAML key `detection_settings` corrected to `settings`; domain scoring now reads `confidence_threshold` and `ambiguity_threshold` from `config/domain_profiles.yaml` instead of silently using hardcoded defaults
- `tools/generate_prompt.py` — `[domain: X]` prefix now parsed explicitly before scoring, so all 8 domains can be force-routed (previously only `data_analytics` and `product_design` worked by coincidence); invalid domain names in prefix now print a warning instead of silently falling back
- `tools/generate_prompt.py` — session_count write to `project.yaml` is now atomic (`tempfile + os.replace`), matching `init_project.py`; previously a crash mid-write could corrupt the config file
- `tools/validate_kit.py` — `FAILURES` list now cleared at the start of `main()`, preventing stale failures accumulating across multiple calls in the same process
- `token_optimization/compressor.py` — `estimated_token_reduction_pct` now measures truncation savings only (retained files before vs after truncation), not file drops; previously dropping files inflated the reported reduction percentage
- `context_loaders/repo_tree.py` — `format_tree()` `root` parameter made optional (`None` default); it was declared but never used in the function body
- `tools/init_project.py` — removed dead `format_tree` import (imported but never called)
- `quickstart.sh`, `quickstart.ps1` — context loader example commands now include the required `--path .` argument; previously the shown commands would exit with a usage error

### Changed
- `agents/orchestrator.md` — added domain-phase mapping precedence rule, Phase Exit Criteria table, Phase 5 Handoff procedure spec, and Companion Block Schema
- `agents/code_agent.md` — standardized phase nomenclature to "Phase N — Name (`phase_key`)" format
- `agents/ux_agent.md` — standardized phase nomenclature to "Phase N — Name (`phase_key`)" format
- `agents/architect_agent.md` — standardized phase nomenclature to "Phase N — Name (`phase_key`)" format
- `tools/init_project.py` — added `--claude-md` flag: runs `generate_claude_md` after bootstrap and prints CLAUDE.md path; added tip to non-flag summary pointing to `generate_claude_md.py`
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
