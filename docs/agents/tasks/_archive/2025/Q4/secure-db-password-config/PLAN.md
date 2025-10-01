# Objective
Remove the hard-coded database password default from `Settings` while keeping URL construction robust and covered by tests.

# Constraints
- Follow TDD (introduce failing tests before implementation).
- Maintain compatibility with existing deployment env vars.
- No regression in other settings behavior.

# Target Files & Changes
- `backend/tests/test_config.py`: add coverage for missing/explicit DB password behavior.
- `backend/config.py`: allow empty password and adapt URL builder to omit credentials when absent.
- `docs/ENVIRONMENT.md` (if wording requires clarification).

# Test/Validation Cases
1. Settings without `DB_PASSWORD` should build a PostgreSQL URL that omits the password segment.
2. Settings with `DB_PASSWORD` containing special chars should percent-encode them in the URL.
3. Regression guard: existing sqlite path test continues to pass.

# Steps
- [x] Step 1: Write failing tests capturing missing-password omission and explicit password encoding.
- [x] Step 2: Implement config updates to satisfy tests (default empty/optional, URL builder logic).
- [x] Step 3: Update documentation if necessary and run full relevant test suite (`uv run pytest backend/tests/test_config.py`).

# Rollback
Revert modifications to `backend/config.py` and associated tests; restore prior documentation.

# Review Hotspots
- URL string formatting and quoting logic.
- Interactions with BaseSettings defaults and environment overrides.

# Status
- Complete
