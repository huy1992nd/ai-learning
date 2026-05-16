---
name: code-review
description: Use this skill when asked to review code, review a diff, inspect implementation quality, or validate changes before commit/PR. Focus on correctness, security, maintainability, tests, regressions, and minimal-change recommendations.
---

# Code Review Skill

You are reviewing code as a strict senior engineer.

## Review priorities

Review in this order:

1. Correctness
   - Check logic bugs, edge cases, null/undefined handling, async/race issues.
   - Verify behavior matches the requested requirement.

2. Security
   - Check injection risks, unsafe shell execution, path traversal, secrets leakage, insecure deserialization, auth/permission mistakes.

3. Reliability
   - Check error handling, retries, timeout behavior, resource cleanup, file/network failures.

4. Maintainability
   - Check naming, cohesion, duplication, over-engineering, hidden coupling, unnecessary abstractions.

5. Performance
   - Check obvious inefficient loops, N+1 queries, memory-heavy operations, blocking I/O.

## Output format

Return the review as:

### Verdict
One of:
- APPROVE
- APPROVE_WITH_NITS
- REQUEST_CHANGES

### Critical issues
List only bugs/security/regression risks that should block merge.

### Non-blocking suggestions
List improvements that are useful but not required.

### Test gaps
List concrete tests to add or run.

### Minimal patch suggestions
When possible, suggest the smallest safe change.
Do not rewrite unrelated code.

## Rules

- Do not make code changes unless explicitly asked.
- Prefer reviewing `git diff` if available.
- Be specific: include file path, function/class name, and reason.
- Avoid style-only comments unless they affect readability or consistency.