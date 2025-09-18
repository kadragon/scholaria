# TODO: School Integrated RAG System

## Project Setup & Infrastructure ✅

### Development Environment ✅
- [x] Set up uv package manager configuration
- [x] Create Docker Compose configuration for all services
- [x] Set up PostgreSQL container
- [x] Set up Redis container
- [x] Set up Qdrant vector database container
- [x] Set up MinIO object storage container
- [x] Configure Unstructured API service

### Django Project Setup ✅
- [x] Initialize Django project with uv
- [x] Configure Django settings for development/production
- [x] Set up Django database configuration (PostgreSQL)
- [x] Configure Django admin interface
- [x] Set up Celery for background tasks
- [x] Configure Redis as Celery broker

### Code Quality & Development Tools ✅
- [x] Set up ruff (linting + formatting)
- [x] Configure pre-commit hooks
- [x] Add mypy type checking with Django stubs
- [x] Configure test settings (SQLite for fast testing)
- [x] Create comprehensive README.md with uv commands

## Core Models & Database (TDD)

### Test-First Model Development (Partial ✅)
- [x] Write tests for Topic model
- [x] Implement Topic model (name, description, system_prompt)
- [x] Add proper type annotations to Topic model
- [x] Create initial migration for Topic model
- [ ] Write tests for Context model
- [ ] Implement Context model (name, description, context_type)
- [ ] Write tests for ContextItem model
- [ ] Implement ContextItem model (PDF, FAQ, Markdown content)
- [ ] Write tests for Topic-Context mapping (N:N relationship)
- [ ] Implement Topic-Context mapping
- [ ] Write tests for model validation and constraints
- [ ] Implement model validation logic

### Database Migrations
- [x] Create initial migration for Topic model
- [ ] Create migrations for remaining models
- [ ] Test migration rollback/forward compatibility

## Admin Interface (TDD)

### Admin Tests & Implementation
- [ ] Write tests for Topic admin CRUD operations
- [ ] Implement Topic admin interface
- [ ] Write tests for Context admin CRUD operations
- [ ] Implement Context admin interface
- [ ] Write tests for ContextItem admin with file upload
- [ ] Implement ContextItem admin with MinIO integration
- [ ] Write tests for Topic-Context mapping in admin
- [ ] Implement Topic-Context mapping interface
- [ ] Write tests for bulk operations
- [ ] Implement bulk upload/update functionality

## Document Ingestion Pipeline (TDD)

### Ingestion Worker Tests & Implementation
- [ ] Write tests for PDF parsing via Unstructured API
- [ ] Implement PDF parsing integration
- [ ] Write tests for Markdown parsing
- [ ] Implement Markdown parsing
- [ ] Write tests for FAQ entry processing
- [ ] Implement FAQ processing
- [ ] Write tests for document chunking strategy
- [ ] Implement document chunking
- [ ] Write tests for embedding generation (OpenAI)
- [ ] Implement embedding generation
- [ ] Write tests for Qdrant upsert with metadata
- [ ] Implement Qdrant integration
- [ ] Write tests for Celery task orchestration
- [ ] Implement Celery ingestion tasks

### File Storage Integration
- [ ] Write tests for MinIO file upload/download
- [ ] Implement MinIO integration
- [ ] Write tests for file validation and security
- [ ] Implement file validation logic

## RAG Query Pipeline (TDD)

### Retrieval Tests & Implementation
- [ ] Write tests for Qdrant vector search by topic
- [ ] Implement Qdrant query functionality
- [ ] Write tests for BGE Reranker integration
- [ ] Implement BGE Reranker
- [ ] Write tests for context preparation for LLM
- [ ] Implement context formatting
- [ ] Write tests for OpenAI API integration
- [ ] Implement OpenAI answer generation
- [ ] Write tests for citation extraction
- [ ] Implement citation/reference system

### API Endpoints (TDD)
- [ ] Write tests for topic selection endpoint
- [ ] Implement topic selection API
- [ ] Write tests for question-answer endpoint
- [ ] Implement Q&A API endpoint
- [ ] Write tests for API error handling
- [ ] Implement comprehensive error handling
- [ ] Write tests for API rate limiting
- [ ] Implement rate limiting

## User Interface

### Topic Selection
- [ ] Create topic selection interface
- [ ] Test topic selection functionality
- [ ] Implement responsive design

### Q&A Interface
- [ ] Create question input interface
- [ ] Create answer display with citations
- [ ] Test Q&A user flow
- [ ] Implement loading states and error handling

## Integration Testing

### End-to-End Tests
- [ ] Write test for complete ingestion flow (upload → parse → embed → store)
- [ ] Write test for complete Q&A flow (select topic → ask question → get answer)
- [ ] Write test for admin workflow (create topic → upload docs → map contexts)
- [ ] Create golden test dataset for quality validation
- [ ] Implement performance benchmarks (< 3 second response time)

### System Integration
- [ ] Test all services working together via Docker Compose
- [ ] Test data consistency across PostgreSQL and Qdrant
- [ ] Test MinIO file integrity and access
- [ ] Test Celery task processing and error handling

## Quality & Performance

### Testing Coverage
- [ ] Achieve >80% test coverage for models
- [ ] Achieve >80% test coverage for ingestion pipeline
- [ ] Achieve >80% test coverage for retrieval pipeline
- [ ] Achieve >80% test coverage for API endpoints

### Performance Optimization
- [ ] Optimize Qdrant query performance
- [ ] Implement caching for frequent queries
- [ ] Optimize chunking strategy for different document types
- [ ] Monitor and optimize OpenAI API usage

## Documentation

### Technical Documentation
- [ ] API documentation (OpenAPI/Swagger)
- [ ] Deployment guide
- [ ] Admin user guide
- [ ] End user guide

### Development Documentation
- [ ] Contributing guidelines
- [ ] Testing strategy documentation
- [ ] Architecture decision records

## Deployment & Operations

### Production Setup
- [ ] Production Docker Compose configuration
- [ ] Environment variable management
- [ ] Database backup strategy
- [ ] Log aggregation and monitoring
- [ ] Health check endpoints

### CI/CD Pipeline
- [ ] Set up automated testing pipeline
- [ ] Set up code quality checks (linting, type checking)
- [ ] Set up automated deployment
- [ ] Set up monitoring and alerting

## Future Enhancements (Nice to Have)

### Feedback System
- [ ] Design feedback data model
- [ ] Implement thumbs up/down functionality
- [ ] Create feedback analytics

### Multi-language Support
- [ ] Research multi-language embedding models
- [ ] Implement language detection
- [ ] Add language-specific processing

### Analytics Dashboard
- [ ] Design analytics data model
- [ ] Implement query tracking
- [ ] Create analytics dashboard
- [ ] Add performance metrics

### Authentication & Authorization
- [ ] Research SSO integration options
- [ ] Implement user authentication
- [ ] Add role-based access control
- [ ] Integrate with school directory systems

---

## Current Status Summary 📊

### ✅ **COMPLETED** (MVP Foundation Ready)
- **Infrastructure**: Docker Compose with PostgreSQL, Redis, Qdrant, MinIO, Unstructured API
- **Django Setup**: Project initialized with proper settings for dev/prod
- **Code Quality**: Ruff linting, mypy type checking, pre-commit hooks
- **Testing**: TDD setup with comprehensive Topic model tests (6 tests passing)
- **Topic Model**: Fully implemented with validation and type annotations
- **Development Tools**: justfile commands, test configuration

### 🚧 **IN PROGRESS** (Next Steps)
- Context and ContextItem models (tests + implementation)
- N:N relationship mapping between Topics and Contexts

### 📋 **PENDING** (Remaining MVP Work)
- Admin interface implementation
- Document ingestion pipeline (Celery + Qdrant)
- RAG query pipeline (retrieval + reranking + LLM)
- API endpoints for Q&A functionality
- End-to-end integration tests

### 🎯 **Ready for Development**
The project foundation is solid and ready for TDD development of remaining features.
All tools are configured and working:
```bash
# Run all quality checks
uv run ruff check . && uv run mypy . && uv run python manage.py test --settings=core.test_settings

# Start development server
uv run python manage.py runserver

# Start Docker services
docker-compose up -d
```

### 📈 **Progress Metrics**
- **Foundation Setup**: 100% (13/13 tasks complete)
- **Topic Model**: 100% (4/4 tasks complete)
- **Overall MVP Progress**: ~15% (17/110+ tasks complete)
- **Code Quality**: mypy strict mode, ruff formatting, 6 tests passing
- **Infrastructure**: All services containerized and ready

---

## Success Criteria

**MVP Success Metrics:**
- [ ] Admin can upload PDF/FAQ/Markdown and connect to topics
- [ ] User can ask a question in a selected topic and get an answer with citations
- [ ] Ingestion pipeline runs automatically
- [ ] >80% of test queries return relevant citations
- [ ] Answer latency < 3 seconds (excluding ingestion)

**Quality Gates:**
- [ ] All tests passing
- [ ] No critical security vulnerabilities
- [ ] Performance benchmarks met
- [ ] Code coverage targets achieved
