# RAG Ingestion Pipeline - Agent Knowledge Base

## Intent

Document ingestion pipeline for processing PDF, Markdown, and FAQ files into chunked ContextItems using Celery background tasks.

## Constraints

- **TDD Required**: All ingestion development follows Red → Green → Refactor cycle
- **Celery Tasks**: Use `@shared_task` decorator for task definition
- **Chunking Strategy**: Smart chunking with overlap at sentence/word boundaries
- **Error Handling**: Graceful handling of missing files and parsing errors
- **Type Safety**: Full mypy compliance with proper task typing

## Context

### Ingestion Architecture

- **PDFParser**: Uses Unstructured API for PDF text extraction
- **MarkdownParser**: Direct file reading with UTF-8 encoding
- **FAQParser**: Direct file reading for Q&A format documents
- **TextChunker**: Intelligent text splitting with configurable chunk size and overlap
- **Celery Tasks**: Background processing with proper error handling

### Task Flow

```
process_document → ingest_pdf_document | ingest_markdown_document | ingest_faq_document
                → PDFParser | MarkdownParser | FAQParser
                → TextChunker
                → ContextItem creation (one per chunk)
```

### Key Classes

- `PDFParser`: Extract text from PDF files using Unstructured
- `MarkdownParser`: Read and return Markdown file content
- `FAQParser`: Read and return FAQ file content (Q&A format)
- `TextChunker`: Split text into overlapping chunks with smart boundaries
- `process_document`: Main task dispatcher based on context type
- `ingest_pdf_document`: PDF-specific ingestion pipeline
- `ingest_markdown_document`: Markdown-specific ingestion pipeline
- `ingest_faq_document`: FAQ-specific ingestion pipeline

## Changelog

### 2025-09-18: Document Ingestion Pipeline Implementation

- ✅ Created comprehensive TDD test suite for parsers (11 tests)
- ✅ Implemented PDFParser with Unstructured API integration
- ✅ Implemented MarkdownParser with file reading capabilities
- ✅ Created TextChunker with smart boundary detection and overlap
- ✅ Created comprehensive TDD test suite for Celery tasks (7 tests)
- ✅ Implemented process_document dispatcher task
- ✅ Implemented ingest_pdf_document and ingest_markdown_document tasks
- ✅ All 61 tests passing (including 18 new ingestion tests)
- ✅ Full mypy type checking compliance
- ✅ Proper error handling for missing files and unsupported types

### 2025-09-19: FAQ Processing Implementation

- ✅ Created comprehensive TDD test suite for FAQ parser (5 tests)
- ✅ Implemented FAQParser for Q&A document format support
- ✅ Created comprehensive TDD test suite for FAQ ingestion tasks (4 tests)
- ✅ Implemented ingest_faq_document Celery task
- ✅ Updated process_document dispatcher to support FAQ context type
- ✅ All 134 tests passing (added 9 new FAQ tests)
- ✅ Full mypy type checking compliance maintained
- ✅ FAQ documents now fully supported in ingestion pipeline

### Implementation Details

- **Chunk Metadata**: Each ContextItem includes chunk_index, total_chunks, and chunk_size
- **File Path Storage**: Original file paths stored for reference
- **Smart Chunking**: Prefers sentence boundaries, falls back to word boundaries
- **Configurable Chunking**: Default 1000 characters with 200 character overlap
- **Task Delegation**: Automatic routing based on Context.context_type

### 2025-09-19: Optimized Document-Type-Specific Chunking

- ✅ Created comprehensive TDD test suite for optimized chunking strategies (3 tests)
- ✅ Implemented MarkdownChunker with structure-aware splitting (headers, sections, code blocks)
- ✅ Implemented FAQChunker that preserves Q&A pairs integrity
- ✅ Implemented PDFChunker with PDF-specific text normalization and formatting
- ✅ Updated ingestion tasks to use document-specific chunkers
- ✅ All 19 ingestion tests passing with optimized chunking integration

### Optimized Chunking Features

**MarkdownChunker** (chunk_size=1200, overlap=200):
- Respects Markdown structure (headers, lists, code blocks)
- Prioritizes section boundaries for clean breaks
- Preserves document hierarchy and formatting

**FAQChunker** (chunk_size=800, overlap=100):
- Keeps Q&A pairs together to maintain context
- Handles various FAQ formats and separators
- Optimized for question-answer relationship preservation

**PDFChunker** (chunk_size=1000, overlap=150):
- Normalizes PDF text extraction artifacts
- Handles mixed formatting and section headers
- Optimized for varied document structure

### Chunking Strategy Benefits

- **Content Integrity**: Document-specific chunkers preserve logical boundaries
- **Search Quality**: Better chunk boundaries improve retrieval relevance
- **Context Preservation**: Structure-aware chunking maintains semantic relationships
- **Optimized Sizes**: Different chunk sizes optimized for each document type

### Next Steps

- Monitor chunking effectiveness in production
- Performance optimization and monitoring
- Additional document type support if needed
