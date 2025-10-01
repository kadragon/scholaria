# Task Summary
- Goal: eliminate hard-coded DB password default flagged by GitGuardian.
- Key Change: Settings now omits a default password and drops the credential segment when none is provided.
- Key Change: Added config tests covering missing password and percent-encoded secrets.
- Key Change: Updated environment documentation to state no default password ships with the app.
- Tests: `uv run pytest backend/tests/test_config.py -q`
- Follow-up: ensure GitGuardian pipeline passes; adjust docker-compose defaults if further tightening is required.
