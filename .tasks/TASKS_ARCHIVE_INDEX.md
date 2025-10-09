# Tasks Archive Index

| Slug | Title | Period | Keep Level | Notes |
|------|-------|--------|------------|-------|
| bulk-operations-ui | 대량 작업 UI 구현 | 2025-10-02 | summary | Refine Admin Panel bulk operations |
| celery-async-queue | Celery 비동기 큐 재도입 | 2025-10-02 | summary | 임베딩 재생성 비동기화 |
| chunk-edit-feature | 청크 편집 기능 | 2025-10-02 | summary | Context item 인라인 편집 |
| chunk-preview-ui | 청크 미리보기 UI | 2025-10-02 | summary | Context item 뷰어 |
| chunk-reorder-ui | 청크 재정렬 UI | 2025-10-02 | summary | Drag & drop 재정렬 |
| chunking-strategy-refactor | 청킹 전략 리팩터링 | 2025-10-02 | summary | 전략 패턴 적용 (PDF/FAQ/Markdown) |
| django-remnant-audit | Django 잔재 감사 | 2025-10-02 | summary | Django 의존성 100% 제거 검증 |
| django-removal-and-refactoring | Django 제거 및 리팩터링 | 2025-10-02 | summary | FastAPI 전환 완료 |
| django-to-fastapi-migration | Django→FastAPI 마이그레이션 | 2025-10-02 | summary | Phase 1-8 완료 |
| docker-hybrid-compose | Docker 하이브리드 구성 | 2025-09-30 | summary | Tests: `uv run pytest rag/tests/test_docker_fastapi_service.py -q` |
| docker-nginx-integration | Docker Nginx 통합 | 2025-10-02 | summary | 리버스 프록시 설정 |
| docs-update-and-cleanup | 문서 업데이트 및 정리 | 2025-10-02 | summary | 프로젝트 문서 동기화 |
| enable-pdf-upload-frontend | 프론트엔드 PDF 업로드 활성화 | 2025-10-02 | summary | Refine Admin Panel 파일 업로드 |
| fastapi-contexts-transaction | FastAPI Context DB 동기화 | 2025-09-30 | summary | Tests: `uv run pytest backend/tests/test_contexts.py -q` |
| fastapi-readonly-api | FastAPI Read-Only History API | 2025-09-30 | summary | Tests: `uv run pytest backend/tests/test_history_read.py -q` |
| fastapi-sqlalchemy-alembic-setup | Alembic 초기 설정 | 2025-09-30 | summary | Tests: `uv run pytest backend/tests/test_alembic_setup.py` |
| fastapi-test-harness-alignment | FastAPI Test Harness Alignment | 2025-10-01 | summary | Tests: `uv run pytest backend/tests -q` |
| fastapi-topic-context-relations | FastAPI Topic↔Context 관계 매핑 | 2025-09-30 | summary | Tests: `uv run pytest backend/tests/test_topics_poc.py` |
| fastapi-topics-poc | FastAPI /api/topics POC | 2025-09-30 | summary | Tests: `uv run pytest backend/tests/test_topics_poc.py` |
| feedback-system | 피드백 시스템 (좋아요/싫어요) | 2025-10-02 | summary | RAG 응답 평가 |
| final-fastapi-tests | FastAPI 최종 테스트 | 2025-10-02 | summary | 통합 테스트 완료 |
| fix-context-item-update-tests | Context Item 업데이트 테스트 수정 | 2025-10-02 | summary | SQLAlchemy 트랜잭션 픽스 |
| production-deployment | 프로덕션 배포 준비 | 2025-10-02 | summary | Celery 워커 설정 |
| pydantic-v2-modernization | Pydantic v2 전환 | 2025-10-02 | summary | ConfigDict 패턴 적용 |
| rag-endpoint-tests | RAG 엔드포인트 테스트 | 2025-10-02 | summary | AsyncRAGService mock 테스트 |
| redis-shared-cache | Redis 공유 캐시 | 2025-10-02 | summary | 임베딩 캐시 수평 확장 |
| schema-pattern-docs | 스키마 패턴 문서화 | 2025-10-02 | summary | `backend/schemas/README.md` |
| secure-db-password-config | DB 비밀번호 하드코딩 제거 | 2025-10-01 | summary | Tests: `uv run pytest backend/tests/test_config.py -q` |
| step-6-2-2-shadcn-contexts | Shadcn UI Contexts 페이지 | 2025-10-02 | summary | Refine Admin Panel 컨텍스트 관리 |
| test-warnings-cleanup | 테스트 경고 정리 | 2025-10-02 | summary | Pytest deprecation warnings 해결 |

## 아카이브 위치
- `docs/agents/tasks/_archive/2025/Q4/` - 2025년 4분기 완료 태스크
- `docs/agents/tasks/_archive/2025/Q3/` - 2025년 3분기 완료 태스크

## 보존 정책
- **summary**: `TASK_SUMMARY.md`만 보존
- **plan**: `PLAN.md` + `TASK_SUMMARY.md` 보존
- **full**: 모든 문서(RESEARCH/PLAN/PROGRESS) 보존

## frontend-readme-update (2025-10-08)
- **Title:** Frontend README Update
- **Status:** Complete
- **Dates:** 2025-10-08
- **Keep Level:** full
- **Commits:** 1f14ce6, 533176d
- **Tests:** N/A (documentation)
- **Artifacts:** `_archive/2025/Q4/frontend-readme-update/`

## performance-benchmark (2025-10-08)
- **Title:** Performance Benchmark (Initial)
- **Status:** Initial implementation complete
- **Dates:** 2025-10-08
- **Keep Level:** summary
- **Commits:** 8f249ef, bc04488
- **Tests:** 4 passed, 2 skipped (6 new tests)
- **Artifacts:** `_archive/2025/Q4/performance-benchmark/TASK_SUMMARY.md`

## dark-mode (2025-10-09)
- **Title:** Dark Mode Implementation
- **Status:** Complete
- **Dates:** 2025-10-09
- **Keep Level:** full
- **Commits:** d42296f, ee39050, 2fc1314 (PR #50)
- **Tests:** 37 passed (13 new: ThemeProvider 7, ThemeToggle 6)
- **Artifacts:** `_archive/2025/Q4/dark-mode/` (RESEARCH.md, PLAN.md, PROGRESS.md, TASK_SUMMARY.md)

## add-missing-indexes (2025-10-10)

- **Title:** Add Missing Database Indexes
- **Status:** Complete
- **Dates:** 2025-10-10
- **Keep Level:** summary
- **Commits:** PR #55
- **Tests:** 197 passed, 83% coverage
- **Artifacts:** `_archive/2025/Q4/add-missing-indexes/` (PLAN.md, PROGRESS.md)

## admin-datetime-serialization (2025-10-10)

- **Title:** Admin Datetime Serialization
- **Status:** Complete
- **Dates:** 2025-10-10
- **Keep Level:** summary
- **Commits:** 0e200af, 292b01b, 70b085e
- **Tests:** 195 passed
- **Artifacts:** `_archive/2025/Q4/admin-datetime-serialization/` (PLAN.md, PROGRESS.md, RESEARCH.md, TASK_SUMMARY.md)

## backend-coverage-threshold (2025-10-10)

- **Title:** Backend Coverage Threshold and CI
- **Status:** Complete
- **Dates:** 2025-10-10
- **Keep Level:** summary
- **Commits:** [Structural] feat(backend): Add coverage threshold and CI workflow
- **Tests:** 195 passed, 85.01% coverage (80% threshold)
- **Artifacts:** `_archive/2025/Q4/backend-coverage-threshold/` (PLAN.md, PROGRESS.md, RESEARCH.md, TASK_SUMMARY.md)

## frontend-lint-fix (2025-10-10)

- **Title:** Frontend Lint and Type Error Fixes
- **Status:** Complete
- **Dates:** 2025-10-10
- **Keep Level:** summary
- **Commits:** (pending)
- **Tests:** ESLint + TypeScript clean
- **Artifacts:** `_archive/2025/Q4/frontend-lint-fix/` (PLAN.md, PROGRESS.md)

## analytics-data-parsing (2025-10-10)

- **Title:** Analytics Data Parsing Type Safety
- **Status:** Complete
- **Dates:** 2025-10-02
- **Keep Level:** summary
- **Tests:** Type safety improvements
- **Artifacts:** `_archive/2025/Q4/analytics-data-parsing/` (PLAN.md, PROGRESS.md, RESEARCH.md, TASK_SUMMARY.md)

## backup-restore-guide (2025-10-10)

- **Title:** Backup & Restore Guide
- **Status:** Complete
- **Dates:** 2025-10-08
- **Keep Level:** summary
- **Commits:** 06c0218
- **Artifacts:** `_archive/2025/Q4/backup-restore-guide/` (PLAN.md, PROGRESS.md, RESEARCH.md, TASK_SUMMARY.md)

## celery-monitoring (2025-10-10)

- **Title:** Celery Flower Monitoring
- **Status:** Complete
- **Dates:** 2025-10-03
- **Keep Level:** summary
- **Commits:** 0966ff5
- **Artifacts:** `_archive/2025/Q4/celery-monitoring/` (PLAN.md, PROGRESS.md, RESEARCH.md, TASK_SUMMARY.md)

## centralize-api-client (2025-10-10)

- **Title:** Centralize API Client
- **Status:** Complete
- **Dates:** 2025-10-08
- **Keep Level:** summary
- **Commits:** 8315f96
- **Tests:** 136 lines of duplication removed
- **Artifacts:** `_archive/2025/Q4/centralize-api-client/` (PLAN.md, PROGRESS.md, RESEARCH.md, TASK_SUMMARY.md)

## frontend-phase2-component-tests (2025-10-10)

- **Title:** Frontend Phase 2 Component Tests
- **Status:** Complete
- **Dates:** 2025-10-09
- **Keep Level:** summary
- **Tests:** 65 tests passed
- **Artifacts:** `_archive/2025/Q4/frontend-phase2-component-tests/` (PLAN.md, PROGRESS.md, RESEARCH.md, TASK_SUMMARY.md)

## pdf-upload-progress (2025-10-10)

- **Title:** PDF Upload Progress Indicator
- **Status:** Complete
- **Dates:** 2025-10-03
- **Keep Level:** summary
- **Commits:** 963d8af
- **Artifacts:** `_archive/2025/Q4/pdf-upload-progress/` (PLAN.md, PROGRESS.md, RESEARCH.md, TASK_SUMMARY.md)

## puppeteer-upgrade (2025-10-10)

- **Title:** Puppeteer to Playwright Migration
- **Status:** Complete
- **Dates:** 2025-10-06
- **Keep Level:** summary
- **Artifacts:** `_archive/2025/Q4/puppeteer-upgrade/` (PLAN.md, PROGRESS.md, TASK_SUMMARY.md)

## topic-context-connection-ui (2025-10-10)

- **Title:** Topic-Context N:N UI
- **Status:** Complete
- **Dates:** 2025-10-03
- **Keep Level:** summary
- **Tests:** 148 tests passing, 5 new tests
- **Artifacts:** `_archive/2025/Q4/topic-context-connection-ui/` (PLAN.md, PROGRESS.md, RESEARCH.md, TASK_SUMMARY.md)

## topic-slug (2025-10-10)

- **Title:** Topic Slug Implementation
- **Status:** Complete
- **Dates:** 2025-10-07
- **Keep Level:** summary
- **Commits:** 9fdf043
- **Tests:** 40 tests passing
- **Artifacts:** `_archive/2025/Q4/topic-slug/` (PLAN.md, PROGRESS.md, RESEARCH.md, TASK_SUMMARY.md)

## analytics-dashboard (2025-10-10)

- **Title:** Analytics Dashboard
- **Status:** Complete
- **Dates:** 2025-10-09
- **Keep Level:** summary
- **Tests:** 8/8 tests passed
- **Artifacts:** `_archive/2025/Q4/analytics-dashboard/` (PLAN.md, PROGRESS.md, RESEARCH.md)

## bento-grid-layout (2025-10-10)

- **Title:** Bento Grid Layout
- **Status:** Complete
- **Dates:** 2025-10-06
- **Keep Level:** summary
- **Artifacts:** `_archive/2025/Q4/bento-grid-layout/` (PLAN.md, PROGRESS.md, RESEARCH.md)

## command-palette (2025-10-10)

- **Title:** ⌘K Command Palette
- **Status:** Complete
- **Dates:** 2025-10-06
- **Keep Level:** summary
- **Artifacts:** `_archive/2025/Q4/command-palette/` (PLAN.md, PROGRESS.md, RESEARCH.md)

## data-table-filters (2025-10-10)

- **Title:** Data Table Faceted Filters
- **Status:** Complete
- **Dates:** 2025-10-06
- **Keep Level:** summary
- **Tests:** 0 errors
- **Artifacts:** `_archive/2025/Q4/data-table-filters/` (PLAN.md, PROGRESS.md, RESEARCH.md)

## fastapi-auth (2025-10-10)

- **Title:** FastAPI JWT Authentication
- **Status:** Complete
- **Dates:** 2025-10-01
- **Keep Level:** summary
- **Tests:** 12/12 tests passed
- **Artifacts:** `_archive/2025/Q4/fastapi-auth/` (PLAN.md, PROGRESS.md, RESEARCH.md)

## fastapi-rag-endpoint (2025-10-10)

- **Title:** FastAPI RAG Endpoint
- **Status:** Complete
- **Dates:** 2025-10-01
- **Keep Level:** summary
- **Tests:** 7/7 tests passed
- **Artifacts:** `_archive/2025/Q4/fastapi-rag-endpoint/` (PLAN.md, PROGRESS.md)

## fastapi-write-api (2025-10-10)

- **Title:** FastAPI Write API
- **Status:** Complete
- **Dates:** 2025-10-01
- **Keep Level:** summary
- **Tests:** 16/16 tests passed
- **Artifacts:** `_archive/2025/Q4/fastapi-write-api/` (PLAN.md, PROGRESS.md, RESEARCH.md)

## glassmorphism-ui (2025-10-10)

- **Title:** Glassmorphism UI Effects
- **Status:** Complete
- **Dates:** 2025-10-06
- **Keep Level:** summary
- **Artifacts:** `_archive/2025/Q4/glassmorphism-ui/` (PLAN.md, PROGRESS.md, RESEARCH.md)

## inline-editing-optimistic (2025-10-10)

- **Title:** Inline Editing with Optimistic Updates
- **Status:** Complete
- **Dates:** 2025-10-06
- **Keep Level:** summary
- **Artifacts:** `_archive/2025/Q4/inline-editing-optimistic/` (PLAN.md, PROGRESS.md, RESEARCH.md)

## rag-performance-benchmark (2025-10-10)

- **Title:** RAG Performance Benchmark
- **Status:** Complete
- **Dates:** 2025-10-01
- **Keep Level:** summary
- **Tests:** 11/11 tests passed
- **Artifacts:** `_archive/2025/Q4/rag-performance-benchmark/` (PROGRESS.md, RESEARCH.md)

## skeleton-loading (2025-10-10)

- **Title:** Skeleton Loading States
- **Status:** Complete
- **Dates:** 2025-10-06
- **Keep Level:** summary
- **Artifacts:** `_archive/2025/Q4/skeleton-loading/` (PLAN.md, PROGRESS.md, RESEARCH.md)

## tasks-md-compaction (2025-10-10)

- **Title:** TASKS.md Compaction
- **Status:** Complete
- **Dates:** 2025-10-07
- **Keep Level:** summary
- **Artifacts:** `_archive/2025/Q4/tasks-md-compaction/` (PLAN.md, PROGRESS.md, RESEARCH.md)

## user-qa-interface (2025-10-10)

- **Title:** User Q&A Streaming Interface
- **Status:** Complete
- **Dates:** 2025-10-03
- **Keep Level:** summary
- **Artifacts:** `_archive/2025/Q4/user-qa-interface/` (PLAN.md, PROGRESS.md, RESEARCH.md)

## web-scraper-ingestion (2025-10-10)

- **Title:** Web Scraper Ingestion
- **Status:** Complete
- **Dates:** 2025-10-06
- **Keep Level:** summary
- **Artifacts:** `_archive/2025/Q4/web-scraper-ingestion/` (PLAN.md, PROGRESS.md, RESEARCH.md, MANUAL_TEST.md)
