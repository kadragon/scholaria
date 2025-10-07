"""
FastAPI application entry point.

Pure FastAPI implementation (Django removed).
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.config import settings
from backend.routers import auth, contexts, history, rag, rag_streaming, setup, topics
from backend.routers.admin import analytics_router as admin_analytics
from backend.routers.admin import bulk_operations
from backend.routers.admin import contexts_router as admin_contexts
from backend.routers.admin import topics_router as admin_topics

app = FastAPI(
    title="Scholaria RAG API",
    description="FastAPI implementation of Scholaria RAG System",
    version="0.1.0",
    redirect_slashes=False,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(setup.router, prefix="/api", tags=["setup"])
app.include_router(auth.router, prefix="/api", tags=["auth"])
app.include_router(topics.router, prefix="/api", tags=["topics"])
app.include_router(contexts.router, prefix="/api", tags=["contexts"])
app.include_router(history.router, prefix="/api", tags=["history"])
app.include_router(rag.router, prefix="/api", tags=["rag"])
app.include_router(rag_streaming.router, prefix="/api", tags=["rag"])

# Admin API routers
app.include_router(admin_topics, prefix="/api/admin")
app.include_router(admin_contexts, prefix="/api/admin")
app.include_router(bulk_operations.router, prefix="/api/admin")
app.include_router(admin_analytics, prefix="/api/admin")


@app.get("/health")
async def health_check() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "healthy"}
