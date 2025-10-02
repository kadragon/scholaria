"""Admin API routers for Refine Admin Panel."""

from backend.routers.admin.analytics import router as analytics_router
from backend.routers.admin.contexts import router as contexts_router
from backend.routers.admin.topics import router as topics_router

__all__ = ["topics_router", "contexts_router", "analytics_router"]
