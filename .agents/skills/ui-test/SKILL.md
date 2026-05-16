---
name: ui-test
description: Execute and report documented frontend UI test cases for this repository. Use when the user asks Codex to test a UI case, run a manual/browser test from docs/testcases, verify a frontend flow, or test by page/feature/description such as home symptom-description or disease-research.
---

# UI Test

Use this skill to find, execute, and report frontend UI test cases stored in this repo.

## Test Case Location

Test cases live under:

```text
docs/testcases/<page>/<feature>/<desc>.<happy|edge>.md
```

Treat `<page>` as a page key inside `docs/testcases`, not as an absolute URL or filesystem root. For example, `home` means:

```text
docs/testcases/home
```

Do not call it `/home`.

Current known page folders may be incomplete. If only `home` exists, do not imply admin test cases exist. Discover what is available with `rg --files docs/testcases`.

## Workflow

1. Read the relevant architecture docs before browser or app work:
   - Frontend-only UI tests: `.agents/architecture/FRONTEND.md`
   - Full-stack UI tests involving backend/API/SSE: read both `.agents/architecture/FRONTEND.md` and `.agents/architecture/BACKEND.md`
2. Discover candidate test cases:
   - Run `rg --files docs/testcases`
   - Match by page, feature, description, and happy/edge suffix.
3. If the user names an exact test case file, run that case.
4. If the user names a page/feature only, list matching files briefly and choose the most relevant case unless the request requires multiple cases.
5. Read the selected `.md` test case before executing it.
6. Start required local services only if they are not already running:
   - Frontend usually uses `src/webui`, `npm start`, URL `http://localhost:4200`
   - Backend usually uses `src/api`, `uvicorn app.main:app --port 8000`
7. Prefer the Browser Use plugin for local browser testing when available. If unavailable, state that and use an appropriate local browser fallback.
8. Execute the test case exactly enough to validate each expectation:
   - Record actual steps performed.
   - Record input values used.
   - Record observed UI behavior.
   - Check relevant network/API behavior when the expectation mentions endpoints or SSE events.
9. Report result as `PASS`, `FAIL`, or `BLOCKED`.
10. When done, ask before stopping user-owned services. If you started services for the test and the user did not ask to keep them running, stop only those services.

## Result Format

Use this concise report shape:

```text
Result: PASS|FAIL|BLOCKED
Test case: docs/testcases/<page>/<feature>/<desc>.<happy|edge>.md

Executed steps:
- ...

Observed:
- ...

Expectation check:
- PASS ...
- FAIL ...
- BLOCKED ...

Notes:
- ...
```

## Important Rules

- Do not invent missing test cases. If no matching file exists, say so and offer to create one.
- Do not treat `home` as an absolute path. It is a folder under `docs/testcases`.
- Do not silently switch from an edge case to a happy case or vice versa.
- Do not mark `PASS` if a required backend/API/SSE expectation was not checked.
- If environment configuration blocks the case, mark `BLOCKED` and include the concrete blocker.
- Keep screenshots/log artifacts only when useful; mention their paths in the report.
