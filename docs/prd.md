# Product Requirements Document (PRD)
**Project:** School Integrated RAG System
**Approach:** MVP-first, TDD-driven development

---

## 1. Objective
Build an integrated Retrieval-Augmented Generation (RAG) system for schools, enabling users to query knowledge bases (PDFs, FAQs, Markdown docs) by topic. The system should support administrators in managing topics, contexts, and system prompts, and allow end users to select topics and receive AI-powered answers with references.

---

## 2. Key Users & Roles
1. **Administrator**
   - Manage topics (CRUD)
   - Manage contexts (PDF/FAQ/Markdown sources) and connect them to topics
   - Manage system prompts per topic
   - Upload and update documents (via Admin UI)
2. **End User (Student/Staff)**
   - Select a topic
   - Ask questions and receive answers grounded in context
   - See references/sources for transparency

---

## 3. MVP Scope
### Must Have
- **Admin (Django Admin)**
  - CRUD for Topics, Contexts, FAQ entries, Markdown docs
  - Upload PDF/Markdown to MinIO (via Admin form)
  - Map Topics ↔ Contexts (N:N)
- **User**
  - Topic selection
  - Ask a question → API pipeline:
    - Retrieve context from Qdrant (filtered by topic)
    - Rerank with BGE Reranker
    - Generate answer using OpenAI API (system prompt + context)
    - Return answer + citations
- **Ingestion Worker**
  - Triggered on file/FAQ/MD change
  - Uses Unstructured API to parse docs
  - Chunk + embed (OpenAI or local model)
  - Upsert into Qdrant with metadata (topic_id, source_type, context_item_id)
- **Storage**
  - PostgreSQL for metadata (topics, contexts, mappings, FAQ)
  - Qdrant for vector search
  - MinIO for raw files
  - Redis for queue/caching
- **Tests**
  - Unit tests for models, ingestion, retrieval, reranker, API endpoints
  - Integration test: question → answer (golden test data)

### Nice to Have (Future Iterations)
- Feedback loop (thumbs up/down on answers)
- Multi-language support
- Analytics dashboard (query counts, latency, retrieval hit ratio)
- Authentication/SSO integration

---

## 4. System Components
- **Django Monolith**
  - ORM models (Topic, Context, ContextItem, Mappings)
  - Admin UI for management
  - REST API for Q&A
- **Celery Worker**
  - Background ingestion jobs
- **Qdrant** (vector DB)
- **PostgreSQL** (relational DB)
- **MinIO** (object storage for raw documents)
- **Redis** (queue + cache)
- **Unstructured API** (doc parsing microservice)
- **OpenAI API** (answer generation)

---

## 5. Tech Stack
- Backend: **Django + Django Admin**
- ORM/DB: **Django ORM + PostgreSQL**
- Vector DB: **Qdrant**
- Parser: **Unstructured API**
- RAG Framework: **LlamaIndex** (simple start) or **LangChain/LangGraph** (later flexibility)
- Reranker: **BGE Reranker** (Hugging Face)
- LLM: **OpenAI GPT models**
- Infra: **Docker Compose** (all services containerized)
- **Package Manager: [uv](https://github.com/astral-sh/uv)**
  - Fast dependency resolution, isolated environments, reproducible builds
  - Standardize all Python package management with `uv pip install`, `uv venv`, `uv lock`

---

## 6. Development Approach (TDD + MVP)
1. **Define tests first** for each feature:
   - Model creation/validation (Topic, Context, Mapping)
   - Ingestion pipeline (file upload → parsed chunks → embeddings in Qdrant)
   - API retrieval (mock OpenAI)
   - End-to-end Q&A (query → retrieved chunks → reranked → mock answer)
2. **Implement minimal code** to pass tests (MVP-first).
3. **Iterate**:
   - Add feedback loop tests → implement
   - Add multilingual test cases → implement

---

## 7. Success Metrics
- **MVP Success**
  - Admin can upload PDF/FAQ/Markdown and connect to topics
  - User can ask a question in a selected topic and get an answer with citations
  - Ingestion pipeline runs automatically
- **Quality Metrics**
  - >80% of test queries return relevant citations
  - Answer latency < 3 seconds (excluding ingestion)

---

## 8. Risks & Mitigations
- **Risk:** Large documents slow ingestion
  **Mitigation:** Async workers + chunking + caching
- **Risk:** OpenAI API latency/cost
  **Mitigation:** Add local reranker, cache results, explore local LLM fallback
- **Risk:** Admin overload for content curation
  **Mitigation:** Clear UI, bulk upload support (later)
