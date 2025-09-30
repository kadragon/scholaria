"""
FastAPI application entry point.

POC implementation for Django to FastAPI migration.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routers import contexts, history, rag, topics

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

app.include_router(topics.router, prefix="/api", tags=["topics"])
app.include_router(contexts.router, prefix="/api", tags=["contexts"])
app.include_router(history.router, prefix="/api", tags=["history"])
app.include_router(rag.router, prefix="/api", tags=["rag"])


@app.get("/health")
async def health_check() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "healthy"}
