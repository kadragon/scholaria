"""Admin API routers for Refine Admin Panel."""

from api.routers.admin.contexts import router as contexts_router
from api.routers.admin.topics import router as topics_router

__all__ = ["topics_router", "contexts_router"]
