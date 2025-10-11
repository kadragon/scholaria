#!/bin/bash
set -e

echo "⚡ Running unit tests only (models, views, admin)..."

source backend/.venv/bin/activate
python -m pytest rag/tests/test_models.py rag/tests/test_views.py rag/tests/test_admin.py core/tests/ --tb=short

echo "✅ Unit tests completed!"
