Goal: Ensure FastAPI contexts endpoints read Django test data by syncing SQLAlchemy DB configuration.
Key Changes:
- Added regression coverage (`api/tests/test_config.py`) verifying sqlite URL generation.
- Enhanced `api/config.Settings` to derive DB config from Django settings/environment and return connect args.
- Reworked `api/models/base.py` for lazy engine binding with sqlite awareness; pointed Django tests to shared `tmp/test.sqlite3`.
Tests: `uv run pytest api/tests/test_config.py api/tests/test_contexts.py api/tests/test_topics_poc.py -q` (pass).
Notes: sqlite test DB now file-backed; FastAPI and Django share via lazy engine creation.
