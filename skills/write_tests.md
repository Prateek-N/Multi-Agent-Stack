# Skill: write_tests

## Description

Generate unit and integration test stubs for a given function, class, or endpoint. Tests follow the project's existing fixture patterns, assertion style, and test framework. Output is ready-to-run test code with one-line explanations per test case.

---

## When to invoke

- The Code Agent is asked to add or improve test coverage.
- A new function or endpoint has been implemented and needs tests.
- A bug fix needs a regression test to prevent recurrence.

---

## Input expectations

| Input | Required | Description |
|---|---|---|
| `target_code` | Yes | The function, class, or endpoint to test |
| `test_type` | Yes | `unit` \| `integration` \| `both` |
| `existing_tests` | No | A representative existing test file to extract fixture and assertion patterns |
| `test_framework` | No | `pytest` \| `unittest` \| `jest` \| `vitest` \| `go test` \| other (inferred from existing_tests) |
| `fixtures_available` | No | List of fixture names available in the project |
| `coverage_targets` | No | Specific paths/branches to target (default: happy path + top 3 error cases) |

**If required input is missing:**
- `target_code` absent → ask: "Please paste the function, class, or endpoint you want tests for."
- `test_type` absent → default to `unit`; state this assumption in the output header.
- `existing_tests` absent and `test_framework` absent → infer framework from the project stack in `project.yaml` (e.g., Python → pytest, JS → jest). State the inferred framework explicitly. If stack is unknown, default to pytest and note it.

---

## Output format

```python
# tests/test_<module>.py

import pytest
# (other imports matching project conventions)

# --- Fixtures (only if new fixtures are needed) ---

@pytest.fixture
def <fixture_name>():
    # <one-line: what this fixture provides>
    ...


# --- Test cases ---

def test_<function>_<scenario>():
    # Happy path: <what is being verified>
    ...

def test_<function>_<error_scenario>():
    # Error case: <what condition triggers this>
    ...

def test_<function>_<edge_case>():
    # Edge case: <what boundary is being tested>
    ...
```

After the code block, append a coverage summary:

```
## Coverage Summary

| Test case | Type | What it verifies |
|---|---|---|
| `test_create_user_success` | unit | Returns 201 and user ID on valid input |
| `test_create_user_duplicate_email` | unit | Returns 409 when email already exists |
| `test_create_user_invalid_payload` | unit | Returns 400 with field-level errors |

## Not covered (out of scope or requires additional fixtures)
- Database rollback behavior on concurrent inserts
- Token expiry edge case (requires time-mocking fixture)
```

---

## Token cost tier

**Medium.** Scales with number of test cases. Typical output: 300–600 tokens per function under test.

Compression hint: request `test_type: unit` and `coverage_targets: happy_path_only` for a minimal first pass. Integration tests can be added in a follow-up turn.

---

## Notes

- **Never use `time.sleep()` in tests.** If time-dependent behavior must be tested, note it in "Not covered" and suggest the appropriate mocking approach.
- **Do not generate tests for third-party libraries** — test only the project's own logic.
- **Match existing patterns exactly**: if the project uses `assert response.status_code == 200` (not `assertEqual`), follow that style throughout.
- **Regression tests**: if invoked after a bug fix, prefix the test name with `test_regression_` and include a comment: `# Regression: <short description of the bug>`.
