#!/bin/bash
set -e

echo "🚀 Running fast tests (excluding slow integration tests)..."
echo "Expected: ~248 tests"

source .venv/bin/activate
python -m pytest -m "not slow" --tb=short

echo "✅ Fast tests completed!"
