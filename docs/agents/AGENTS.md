# Scholaria Project Root - Agent Knowledge Base

## Intent

School-integrated RAG (Retrieval-Augmented Generation) system for question-answering with document context.

## Constraints

- **TDD Mandatory**: All development follows Red → Green → Refactor cycle
- **Code Quality**: Must pass ruff linting and mypy type checking before commits
- **Test Organization**: Use `/tests/` directories, not single `tests.py` files
- **Docker Development**: All services containerized for consistent environments
- **PostgreSQL Required**: JSONField and full-text search capabilities needed
- **Pytest Parallelism**: Default pytest run uses xdist with `-n=auto`; ensure tests are parallel-safe

## Context

### Development Workflow

```bash
# Quality checks before any commit
uv run ruff check . && uv run mypy . && uv run python manage.py test --settings=core.test_settings

# Development server
uv run python manage.py runserver

# Docker services
docker-compose up -d
```

### Project Architecture

- **Django Backend**: RAG app with Topic/Context/ContextItem models
- **Vector Store**: Qdrant for document embeddings
- **File Storage**: MinIO for document files
- **Cache/Queue**: Redis for Celery background tasks
- **Database**: PostgreSQL for structured data

### Folder-Specific Knowledge

- `/rag/`: Core Django app with models, tests in organized structure
- `/docs/tasks.md`: Comprehensive TODO tracking with progress metrics
- Each folder maintains its own `AGENTS.md` for context-specific knowledge

## Changelog

### 2025-09-18: Core Models Foundation

- ✅ Implemented TDD workflow for Context and ContextItem models
- ✅ Refactored test structure across project (moved to `/tests/` dirs)
- ✅ Established code quality pipeline (ruff + mypy)
- ✅ Created database migrations for new models
- ✅ All 29 tests passing with proper validation
- ✅ Implemented N:N relationship between Topics and Contexts

### 2025-09-18: Admin Interface Implementation

- ✅ Created comprehensive TDD test suite for admin functionality (14 tests)
- ✅ Implemented TopicAdmin, ContextAdmin, and ContextItemAdmin
- ✅ All 43 tests passing with proper admin configurations
- ✅ Code quality maintained: ruff linting and mypy type checking passed

### 2025-09-18: Document Ingestion Pipeline Implementation

- ✅ Set up Celery app with Django integration and task discovery
- ✅ Created comprehensive TDD test suite for parsers and chunkers (18 tests)
- ✅ Implemented PDFParser using Unstructured API for text extraction
- ✅ Implemented MarkdownParser for direct file content reading
- ✅ Created intelligent TextChunker with boundary detection and overlap
- ✅ Implemented Celery tasks for document processing and ingestion
- ✅ All 61 tests passing with complete pipeline coverage
- ✅ Full mypy compliance and proper error handling

### Development Standards Established

- **Test Structure**: Organized `/tests/` directories with specific test files
- **Model Patterns**: Proper validation, string representation, and ordering
- **Django Best Practices**: ForeignKey relationships, JSONField usage, proper Meta classes
- **Type Safety**: Full mypy compliance with strict mode

### 2025-09-20: Documentation Implementation

- ✅ Created comprehensive TDD test suite for deployment guide validation (10 tests)
- ✅ Implemented complete deployment guide with production-ready instructions
- ✅ Covered all essential deployment topics: prerequisites, setup, security, monitoring
- ✅ Documented all environment variables and configuration options
- ✅ Provided troubleshooting guides and maintenance procedures
- ✅ All deployment guide tests passing with full coverage validation

### Documentation Features

**Deployment Guide (`docs/DEPLOYMENT.md`):**
- **Production Setup**: Complete Docker Compose deployment instructions
- **Environment Variables**: Comprehensive list of all configuration options
- **Security**: SSL/TLS, password management, API key security
- **Monitoring**: Health checks, log monitoring, performance metrics
- **Troubleshooting**: Common issues and recovery procedures
- **Maintenance**: Backup strategies, updates, regular maintenance tasks

**Quality Assurance:**
- TDD approach with 10 validation tests covering content and structure
- Proper markdown formatting and comprehensive coverage
- Production-ready instructions with security best practices
- Complete environment variable documentation
- Docker Compose integration and service health monitoring

### System Status

The RAG system now has comprehensive documentation for production deployment, making it ready for enterprise deployment with proper operational guidance.

### 2025-09-20: Admin User Guide Implementation

- ✅ Created comprehensive TDD test suite for admin user guide validation (12 tests)
- ✅ Implemented complete admin user guide covering all Django admin functionality
- ✅ Documented topic management: creation, editing, system prompts, context assignments
- ✅ Covered context management: types (PDF, Markdown, FAQ), organization strategies
- ✅ Detailed context item management: manual entry, file uploads, automatic processing
- ✅ Comprehensive bulk operations documentation: topic updates, context assignments, embedding regeneration
- ✅ Workflow examples, best practices, troubleshooting, and security considerations
- ✅ All admin guide tests passing with full content validation

### Admin Guide Features

**User Management (`docs/ADMIN_GUIDE.md`):**
- **Getting Started**: Login process, interface navigation, dashboard overview
- **Topic Management**: Creation, editing, system prompt optimization, context associations
- **Context Management**: Types (PDF/Markdown/FAQ), organization, best practices
- **Context Items**: Manual content entry, file upload processing, metadata management
- **File Upload System**: Security validation, automatic content extraction, MinIO integration
- **Bulk Operations**: Multi-item management for topics, contexts, and context items
- **Workflows**: Step-by-step examples for common admin tasks
- **Troubleshooting**: Common issues, error messages, solutions
- **Security**: Access control, file validation, content security guidelines

**Quality Assurance:**
- TDD approach with 12 validation tests covering content structure and completeness
- Comprehensive coverage of all Django admin functionality
- Practical workflows and examples for real-world usage
- Security best practices and troubleshooting guidance
- Professional documentation suitable for non-technical administrators

### System Status

The RAG system now has complete administrator documentation, enabling efficient content management through the Django admin interface with comprehensive guidance for all operations.

### 2025-09-20: End User Guide Implementation

- ✅ Created comprehensive TDD test suite for end user guide validation (13 tests)
- ✅ Implemented complete end user guide covering the Q&A interface and learning workflows
- ✅ Documented topic selection process with practical examples and interface descriptions
- ✅ Covered question formulation with guidelines for effective queries and natural language usage
- ✅ Explained answer interpretation: format, citations, source evaluation, and quality assessment
- ✅ Comprehensive troubleshooting section with common issues and step-by-step solutions
- ✅ FAQ section addressing user concerns about accuracy, privacy, limitations, and academic use
- ✅ All end user guide tests passing with full content validation

### End User Guide Features

**Student Interface Documentation (`docs/USER_GUIDE.md`):**
- **Getting Started**: System overview, access instructions, first-time user workflow
- **Topic Selection**: Understanding topics, choosing appropriate subjects, interface navigation
- **Question Formulation**: Guidelines for effective questions, examples, natural language tips
- **Answer Interpretation**: Understanding AI responses, evaluating quality, using citations
- **Source Evaluation**: Citation system, relevance scores, source quality assessment
- **Learning Optimization**: Follow-up questions, refining queries, using different topics
- **Troubleshooting**: Common issues, error messages, network problems, system limitations
- **Academic Guidelines**: Best practices, limitations, academic integrity, verification methods

**Quality Assurance:**
- TDD approach with 13 validation tests covering content structure and user experience
- Comprehensive coverage of all user interface elements and workflows
- Practical examples and demonstrations for real-world usage scenarios
- Educational focus appropriate for students and learners
- Clear guidance on system limitations and appropriate usage

### System Status

The RAG system now has complete user documentation covering all interfaces - from deployment and administration to end-user learning workflows. The technical documentation suite is complete.

### Next Phase Ready

- Contributing guidelines for development workflows
- Architecture decision records for technical documentation
- Testing strategy documentation for development processes
