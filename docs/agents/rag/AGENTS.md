# RAG App - Agent Knowledge Base

## Intent

Django app for Retrieval-Augmented Generation system with Topic, Context, and ContextItem models.

## Constraints

- **TDD Required**: All model development follows Red → Green → Refactor cycle
- **Test Structure**: Tests organized in `/tests/` directory, not single `tests.py` file
- **Model Validation**: Custom `clean()` methods for business logic validation
- **ForeignKey Validation**: Use `field_id` checks instead of direct field access in validation
- **Type Safety**: All models have proper type annotations and pass mypy strict mode

## Context

### Model Architecture

- **Topic**: Course subjects with system prompts for LLM context
- **Context**: Document containers (PDF, FAQ, MARKDOWN types)
- **ContextItem**: Individual content pieces with file references and metadata

### Key Relationships

- Context → ContextItem (1:N via ForeignKey with CASCADE delete)
- Topic ↔ Context (N:N mapping via ManyToManyField)

### Testing Patterns

```python
# Standard model test structure
class ModelNameTest(TestCase):
    def setUp(self):
        # Create required related objects

    def test_creation_with_required_fields(self):
        # Test basic object creation

    def test_field_required(self):
        # Test validation for each required field

    def test_string_representation(self):
        # Test __str__ method

    def test_field_max_length(self):
        # Test field constraints
```

### Django Patterns

- **Choices**: Use tuple choices for enum-like fields
- **JSONField**: For flexible metadata storage (PostgreSQL native)
- **Ordering**: Default ordering in Meta class
- **Related Names**: Descriptive related_name for reverse relationships

## Changelog

### 2025-09-18: Core Models Implementation

- ✅ Refactored test structure from single `tests.py` to `/tests/test_models.py`
- ✅ Implemented Context model with PDF/FAQ/MARKDOWN type choices
- ✅ Implemented ContextItem model with ForeignKey to Context
- ✅ Added JSONField for flexible metadata storage
- ✅ All 23 tests passing with proper TDD cycle
- ✅ Created migration 0002 for new models
- ✅ Fixed ForeignKey validation using `context_id` instead of `context`

### 2025-09-18: Topic-Context N:N Relationship

- ✅ Written 6 comprehensive tests for ManyToMany relationship functionality
- ✅ Implemented `contexts` ManyToManyField on Topic model with reverse `topics` relation
- ✅ Added proper type annotations with mypy compatibility
- ✅ Created migration 0003_topic_contexts for the relationship
- ✅ All 29 tests passing (including 6 new relationship tests)
- ✅ Code quality: ruff linting passed, mypy type checking passed

### 2025-09-18: Admin Interface Implementation

- ✅ Created comprehensive TDD test suite for admin functionality (14 tests)
- ✅ Implemented TopicAdmin with list_display, list_filter, search_fields, and fieldsets
- ✅ Implemented ContextAdmin with context_type filtering and proper display fields
- ✅ Implemented ContextItemAdmin with readonly fields for timestamps
- ✅ All 43 tests passing (including 14 new admin tests)
- ✅ Code quality maintained: ruff linting and mypy type checking passed

### 2025-09-18: Document Ingestion Pipeline Implementation

- ✅ Set up Celery app configuration with Django integration
- ✅ Created comprehensive TDD test suite for document parsing (11 tests)
- ✅ Implemented PDFParser using Unstructured API for text extraction
- ✅ Implemented MarkdownParser for direct file content reading
- ✅ Created TextChunker with intelligent boundary detection and overlap
- ✅ Created comprehensive TDD test suite for Celery tasks (7 tests)
- ✅ Implemented process_document dispatcher for routing by context type
- ✅ Implemented ingest_pdf_document and ingest_markdown_document tasks
- ✅ All 61 tests passing with full pipeline coverage
- ✅ Complete mypy type checking compliance

### 2025-09-18: RAG Query Pipeline Implementation

- ✅ Implemented complete RAG retrieval pipeline with TDD approach
- ✅ Created EmbeddingService for OpenAI text-embedding-3-small integration
- ✅ Created QdrantService for vector storage and similarity search
- ✅ Created RerankingService for BGE reranker integration
- ✅ Created RAGService for complete pipeline orchestration
- ✅ All 35 retrieval tests passing with comprehensive coverage
- ✅ Full mypy type checking compliance maintained

### 2025-09-18: API Endpoints Implementation

- ✅ Created comprehensive TDD test suite for API endpoints (23 tests total)
- ✅ Implemented TopicListView and TopicDetailView with proper serialization
- ✅ Implemented AskQuestionView with full RAG pipeline integration
- ✅ Added comprehensive input validation and error handling
- ✅ Implemented custom exception handler with structured error responses
- ✅ Added rate limiting (30 questions/min) to prevent abuse
- ✅ Added request validation limits (3-5000 character questions)
- ✅ Integrated complete RAG pipeline with citations and context
- ✅ All 23 tests passing with full error scenario coverage
- ✅ Production-ready error handling with proper logging

### API Endpoints Available

**Topic Management:**
- `GET /api/topics/` - List all available topics
- `GET /api/topics/{id}/` - Get specific topic details

**Question-Answer:**
- `POST /api/ask/` - Ask questions and receive RAG-generated answers with citations

### Error Handling Features

- Custom exception handler with structured error responses
- Input validation (question length, topic ID validation, type checking)
- Rate limiting to prevent abuse (30 requests/min for questions)
- Comprehensive logging for debugging and monitoring
- Graceful handling of external service failures
- User-friendly error messages

### 2025-09-19: MinIO File Storage Integration

- ✅ Created comprehensive TDD test suite for MinIO file operations (12 tests)
- ✅ Implemented MinIOStorage service with full CRUD operations
- ✅ Added file upload/download, existence checking, deletion, and URL generation
- ✅ Integrated MinIO with Django admin interface for ContextItem uploads
- ✅ Added uploaded_file field to ContextItem model with proper validation
- ✅ Updated admin interface with file upload capabilities and MinIO integration
- ✅ All 17 new tests passing with existing 146 tests (163 total)

### File Storage Features

- **MinIO Integration**: Complete S3-compatible object storage integration
- **File Upload**: Secure file upload with automatic MinIO storage
- **File Management**: Download, delete, list, and generate presigned URLs
- **Admin Interface**: Enhanced Django admin with file upload capabilities

### 2025-09-19: File Validation and Security System

- ✅ Created comprehensive TDD test suite for file validation (12 tests)
- ✅ Implemented FileValidator service with security-focused validation
- ✅ Added support for PDF, Markdown, and Text file validation
- ✅ Implemented magic byte validation for file type verification
- ✅ Added filename sanitization and security checks
- ✅ Integrated validation with Django admin forms
- ✅ Added protection against malicious files and path traversal attacks

### File Security Features

- **File Type Validation**: Magic byte verification for PDF files
- **Size Limits**: 10MB maximum file size enforcement
- **Filename Security**: Path traversal and malicious filename detection
- **Content Scanning**: Basic virus signature detection (EICAR test)
- **Content Safety**: Script injection detection in text files
- **Filename Sanitization**: Automatic cleanup of unsafe characters
- **Double Extension Detection**: Protection against disguised executables

### File Validation Rules

- **Supported Types**: PDF (.pdf), Markdown (.md, .markdown), Plain Text (.txt)
- **Security Checks**: Path traversal, null bytes, Windows reserved names
- **Content Validation**: Magic bytes for PDFs, encoding validation for text
- **Size Limits**: Maximum 10MB per file
- **Filename Rules**: Alphanumeric, hyphens, underscores, and dots only

### 2025-09-19: Bulk Admin Operations Implementation

- ✅ Fixed Django templates configuration in settings (added BASE_DIR / "templates" to DIRS)
- ✅ Verified all bulk admin operation templates exist and are properly implemented
- ✅ Fixed test case for bulk context type update to use valid choice ("MARKDOWN" instead of "URL")
- ✅ All 14 bulk operations tests now passing (context assignment, system prompt updates, context type updates, embeddings regeneration, item movement)
- ✅ Complete admin interface with comprehensive bulk operations functionality

### Bulk Admin Operations Features

- **Topic Management**: Bulk assign contexts to multiple topics, bulk update system prompts
- **Context Management**: Bulk update context types for multiple contexts
- **Context Item Management**: Bulk regenerate embeddings, bulk move items between contexts
- **Standard Operations**: Bulk delete with confirmation for all models
- **Error Handling**: Graceful handling of invalid selections and edge cases
- **UI Integration**: Professional Django admin templates with proper form handling

### 2025-09-19: End-to-End Integration Testing

- ✅ Created comprehensive end-to-end integration test suite (`test_e2e_integration.py`)
- ✅ Implemented complete ingestion flow testing: upload → parse → chunk → embed → store
- ✅ Added tests for all document types: PDF, Markdown, and FAQ
- ✅ Tested embedding service integration with OpenAI API mocking
- ✅ Tested Qdrant vector database integration with proper metadata handling
- ✅ Added error handling tests for file and context validation
- ✅ All 6 new end-to-end tests passing, bringing total test count to 190
- ✅ Full mypy type safety compliance and ruff code quality standards

### End-to-End Test Coverage

- **Complete Ingestion Pipeline**: File upload, parsing, chunking, embedding generation, vector storage
- **Multiple Document Types**: PDF, Markdown, FAQ with proper format handling
- **Service Integration**: EmbeddingService, QdrantService with mocked external APIs
- **Error Scenarios**: Non-existent files, invalid contexts, service failures
- **Data Validation**: Metadata integrity, content preservation, relationship consistency
- **Quality Assurance**: Type safety, linting compliance, comprehensive assertions

### 2025-09-19: Complete Q&A Flow End-to-End Testing

- ✅ Extended end-to-end integration test suite with comprehensive Q&A flow testing
- ✅ Implemented complete Q&A pipeline testing: topic selection → question → RAG processing → answer + citations
- ✅ Added test coverage for RAG service orchestration (embedding, search, rerank, LLM generation)
- ✅ Tested multiple topics selection and cross-topic querying capabilities
- ✅ Added comprehensive error handling tests (empty queries, no results, invalid inputs)
- ✅ Implemented API endpoint integration testing for both topic selection and Q&A
- ✅ All 6 new Q&A flow tests passing, bringing total test count to 196
- ✅ Full type safety and code quality compliance maintained

### Complete Q&A Flow Test Coverage

- **RAG Pipeline Integration**: Embedding generation, vector search, reranking, LLM answer generation
- **Topic Selection**: API endpoints for topic listing and detail retrieval
- **Multi-Topic Support**: Testing with multiple selected topics for broader context search
- **Citation System**: Proper formatting and validation of sources/citations in responses
- **Error Scenarios**: Empty queries, no relevant context found, service failures
- **API Integration**: Full HTTP endpoint testing with proper request/response validation
- **Response Quality**: Answer structure, citation accuracy, metadata preservation

### 2025-09-19: Complete Admin Workflow End-to-End Testing

- ✅ Extended end-to-end integration test suite with comprehensive admin workflow testing
- ✅ Implemented complete admin workflow testing: topic creation → context creation → file upload → context mapping
- ✅ Added comprehensive Django admin interface testing with HTTP request simulation
- ✅ Tested file upload validation and MinIO integration with proper mocking
- ✅ Added bulk operations testing for admin efficiency workflows
- ✅ Implemented security and permissions testing for admin access control
- ✅ Added error handling tests for form validation and data integrity
- ✅ All 6 new admin workflow tests passing, bringing total test count to 202
- ✅ Full type safety and code quality compliance maintained

### Complete Admin Workflow Test Coverage

- **Topic Management**: Creation, editing, bulk operations, context assignments
- **Context Management**: Creation, configuration, document organization
- **File Upload Operations**: PDF/Markdown/FAQ uploads, validation, MinIO storage integration
- **Context Mapping**: Topic-context relationships, bulk assignments, data consistency
- **Bulk Operations**: System prompt updates, context assignments, item management
- **Security Testing**: Authentication, authorization, permission validation
- **Error Handling**: Form validation, file validation, data integrity checks
- **Integration Testing**: Complete admin interface workflow simulation

### 2025-09-19: Test Coverage Analysis and Rate Limiting Fix

- ✅ Fixed critical test failure issue by disabling rate limiting in test settings
- ✅ Analyzed comprehensive test coverage across all RAG module components
- ✅ **Models**: 100% coverage (58 statements, fully tested)
- ✅ **Ingestion Pipeline**: 97% coverage (chunkers.py and parsers.py well-covered)
- ✅ **Retrieval Pipeline**: 92% coverage (all services properly tested)
- ✅ **API Endpoints**: 85% coverage (views.py exceeds 80% target)
- ✅ Updated test settings to override production rate limiting for test reliability

### Test Coverage Achievement

**All Quality Gates Met:**
- **Models**: 100% test coverage achieved
- **Ingestion Pipeline**: 97% test coverage achieved
- **Retrieval Pipeline**: 92% test coverage achieved
- **API Endpoints**: 85% test coverage achieved

**Critical Fix Applied:**
- Rate limiting configuration was breaking tests (HTTP 429 errors)
- Added REST_FRAMEWORK override in core/test_settings.py to disable throttling during tests
- All test suites now pass consistently without rate limit interference

### Next Steps

- Optimize Qdrant query performance
- Implement caching for frequent queries
- Optimize chunking strategy for different document types
- Monitor and optimize OpenAI API usage
