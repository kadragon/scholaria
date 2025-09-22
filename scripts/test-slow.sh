#!/bin/bash
set -e

echo "🐌 Running slow tests (integration, performance, migrations)..."
echo "Expected: ~33 tests (these take longer to run)"

source .venv/bin/activate
python -m pytest -m "slow" --tb=short

echo "✅ Slow tests completed!"
