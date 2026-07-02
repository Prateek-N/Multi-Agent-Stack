# Security Policy

## Supported Versions

| Version | Supported |
|---------|-----------|
| 1.0.x   | ✅ Yes     |
| < 1.0   | ❌ No      |

## Scope

The following are in scope for security reports:

- **Python tools** — `tools/generate_prompt.py`, `tools/init_project.py`, `tools/validate_kit.py`
- **Context loaders** — `context_loaders/file_chunker.py`, `context_loaders/repo_tree.py`, `context_loaders/project_summary.py`
- **YAML parsing** — handling of `config/*.yaml` and user-supplied YAML content
- **File path handling** — any tool that accepts user-supplied paths or file names

The following are **out of scope**:

- The AI model's own responses (these depend on the LLM provider, not this kit)
- Markdown content inside agent/skill spec files (these are prompts, not executable code)
- Issues in third-party dependencies (report those to the upstream project)

## Reporting a Vulnerability

**Do NOT open a public GitHub issue for security vulnerabilities.**

Report vulnerabilities via [GitHub Security Advisories](https://github.com/Prateek-N/Multi-Agent-Stack/security/advisories/new) — click **"Report a vulnerability"** on the Security tab.

Please include in your report:

- A description of the vulnerability and the affected component
- Steps to reproduce (command, input, environment)
- Potential impact (what an attacker could do)
- Your suggested fix (optional but appreciated)

## Response Timeline

| Step | Timeline |
|------|----------|
| Acknowledgement | Within 48 hours |
| Initial assessment | Within 5 business days |
| Patch release | Within 14 days for CRITICAL/HIGH; 30 days for MEDIUM |
| Public disclosure | After patch is released and users have had time to update |

## Disclosure Policy

We follow **coordinated disclosure**: we ask that you give us time to release a patch before publicly disclosing the vulnerability. We will credit reporters in the release notes unless you prefer to remain anonymous.
