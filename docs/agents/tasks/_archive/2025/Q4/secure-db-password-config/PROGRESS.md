# Summary
Config updated to drop hard-coded DB password; tests currently green.

# Goal & Approach
Follow TDD to remove hard-coded DB password default, ensuring URL formatting handles missing passwords gracefully.

# Completed Steps
- Step 1: Added failing tests for missing and explicit DB password handling.
- Step 2: Updated config to omit password when unset and encode when provided.
- Step 3: Updated environment docs and re-ran config tests.

# Current Failures
- None (latest test run succeeded).

# Decision Log
- Maintained percent-encoding via `quote_plus`; skipping password colon when empty to satisfy scanner.

# Next Step
Task complete; monitor GitGuardian pipeline for green signal.
