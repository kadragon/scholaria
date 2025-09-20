# RAG Ingestion Pipeline - Agent Knowledge Base

## Intent

Document ingestion pipeline for PDF/Markdown/FAQ files using Celery.

## Constraints

- **TDD Required**: Red → Green → Refactor cycle
- **Celery Tasks**: Use `@shared_task` decorator
- **Smart Chunking**: Overlap at sentence/word boundaries
- **Type Safety**: mypy compliance

## Context

### Architecture
- **Parsers**: PDFParser (Unstructured API), MarkdownParser, FAQParser
- **Chunkers**: Document-specific chunking with optimized sizes
- **Tasks**: Background processing with error handling

### Flow
```
process_document → parser → chunker → ContextItem creation
```

## Changelog

### Core Implementation
- TDD test suite for parsers and Celery tasks
- PDF (Unstructured API), Markdown, FAQ parsers
- Smart chunking with boundary detection
- Background processing with error handling

### Optimized Chunking
- **MarkdownChunker**: Structure-aware (1200 chars, 200 overlap)
- **FAQChunker**: Q&A pair preservation (800 chars, 100 overlap)
- **PDFChunker**: Text normalization (1000 chars, 150 overlap)

### Features
- Chunk metadata, file path storage, automatic routing
- Content integrity and improved retrieval relevance
