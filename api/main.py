"""
FastAPI application entry point.

POC implementation for Django to FastAPI migration.
"""

import os

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

from fastapi import FastAPI  # noqa: E402
from fastapi.middleware.cors import CORSMiddleware  # noqa: E402

from api.routers import auth, contexts, history, rag, topics  # noqa: E402
from api.routers.admin import contexts_router as admin_contexts  # noqa: E402
from api.routers.admin import topics_router as admin_topics  # noqa: E402

app = FastAPI(
    title="Scholaria RAG API",
    description="FastAPI implementation of Scholaria RAG System",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8000", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api", tags=["auth"])
app.include_router(topics.router, prefix="/api", tags=["topics"])
app.include_router(contexts.router, prefix="/api", tags=["contexts"])
app.include_router(history.router, prefix="/api", tags=["history"])
app.include_router(rag.router, prefix="/api", tags=["rag"])

# Admin API routers
app.include_router(admin_topics, prefix="/api/admin")
app.include_router(admin_contexts, prefix="/api/admin")


@app.get("/health")
async def health_check() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "healthy"}
