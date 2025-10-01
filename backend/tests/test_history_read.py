"""
Tests for FastAPI history read endpoints.

SKIPPED: Django ORM dependency - will be rewritten with SQLAlchemy fixtures.
"""

import pytest

pytestmark = pytest.mark.skip(reason="Django ORM dependency - needs SQLAlchemy rewrite")
