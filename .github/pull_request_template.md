## Summary

<!-- 1–3 bullet points describing what this PR does -->

- 
- 

## Type of Change

- [ ] New skill card
- [ ] New agent
- [ ] New domain
- [ ] Bug fix (Python tooling)
- [ ] Documentation update
- [ ] CI/tooling improvement
- [ ] Other

## Pre-Submit Checklist

- [ ] `python agents-maker/tools/validate_kit.py` passes ALL checks
- [ ] `python agents-maker/tools/test_kit.py` passes 60/60 (or more if new tests added)
- [ ] If adding a skill: has `## Input Expectations`, `## Output Format`, and `## Token Cost Tier` sections
- [ ] If adding an agent: has `## Role`, `## Goals`, and `## Context` sections
- [ ] If adding a domain: entry added to `config/domain_profiles.yaml` with detection signals and primary_agents
- [ ] `CHANGELOG.md` updated under `[Unreleased]`
- [ ] README repo map updated if new files added

## Validator Output

```
paste output of: python agents-maker/tools/validate_kit.py
```

## Test Output

```
paste last 5 lines of: python agents-maker/tools/test_kit.py
```
