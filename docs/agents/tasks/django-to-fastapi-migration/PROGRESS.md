# Django → FastAPI 전환 진행 상황

## Summary
Django 무게감 제거를 위해 FastAPI + React Admin Panel로 전환 진행 중

## Goal & Approach
- **전환 동기**: Django 무거움 → FastAPI 경량화, 비동기 성능 개선
- **관리 UI**: React Admin Panel (React-Admin 라이브러리)
- **접근법**: 8단계 점진적 마이그레이션 (병렬 실행 → 완전 전환)

## Completed Steps
- [x] **조사 (RESEARCH.md)**
  - 현재 Django 구조 분석 (381개 테스트, 500+ 줄 Admin 커스터마이징)
  - 전환 이점/위험 평가 (성능 vs Admin 손실)
  - 관리 UI 옵션 비교 (React Admin vs 하이브리드 vs 라이브러리)
- [x] **계획 수립 (PLAN.md)**
  - 8단계 상세 계획 (12-18주)
  - Refine Admin Panel 구조 설계 (6.1-6.3)
  - 테스트/검증 전략, 롤백 계획
- [x] **Phase 1: 기반 구조 준비 (완료)**
  - ✅ FastAPI 앱 초기화 (`api/main.py`)
  - ✅ SQLAlchemy 모델 생성 (`api/models/`)
  - ✅ Alembic 마이그레이션 구성 (`alembic/`)
  - ✅ Docker 하이브리드 구성 (Django 8000 + FastAPI 8001)
  - ✅ POC: GET /api/topics 엔드포인트
  - Validation: FastAPI `/docs` 동작, SQLAlchemy 모델 DB 읽기 성공
- [x] **Phase 2: Read-Only API 전환 (완료)**
  - ✅ `api/routers/topics.py`: GET /api/topics, GET /api/topics/{id}
  - ✅ `api/routers/contexts.py`: GET /api/contexts, GET /api/contexts/{id}
  - ✅ `api/routers/history.py`: GET /api/history
  - ✅ Pydantic 스키마 (`api/schemas/`)
  - ✅ 테스트 (`api/tests/test_topics_poc.py`, `test_contexts.py`, `test_history_read.py`)
  - ✅ Django API 응답 동등성 검증 (test_topics_response_matches_django)
  - Note: 서비스 레이어는 단순 CRUD에는 불필요, 복잡한 RAG 로직은 Phase 3에서 구현
  - Validation: 모든 read-only 엔드포인트 동작 확인
- [x] **Phase 3: RAG 엔드포인트 전환 (완료)**
  - ✅ `api/routers/rag.py`: POST /api/rag/ask
  - ✅ `api/services/rag_service.py`: AsyncRAGService (Django RAGService 포팅)
  - ✅ `api/dependencies/redis.py`: Redis 캐싱 (redis.asyncio)
  - ✅ OpenAI AsyncOpenAI 사용
  - ✅ **핵심**: sync_to_async로 Django ORM 호출 래핑 (EmbeddingService, QdrantService, RerankingService)
  - ✅ 테스트 (`api/tests/test_rag_endpoint.py`, 7개 테스트 통과)
  - Validation: RAG 응답 동등성, 캐싱 동작 확인
  - 예상 vs 실제: 5-7일 예상 → **1일** 완료 (최소 변경 전략 효과)

## Current Failures
없음 (Phase 3 완료)

## Decision Log
| 날짜 | 결정 | 근거 |
|------|------|------|
| 2025-09-30 | 전환 동기: Django 무게감 제거 | 사용자 요구사항 |
| 2025-09-30 | 관리 UI: Refine Admin Panel (Option A) | 완전한 커스터마이징, 모던 UX, Django 의존성 제거 |
| 2025-09-30 | React 라이브러리: Refine (vs React-Admin) | 헤드리스 아키텍처, FastAPI와 철학 일치, React Query 내장, UI 프레임워크 자유 선택, 비동기 친화적 |
| 2025-09-30 | ORM: SQLAlchemy 2.0 | 비동기 지원, 성숙도, Django ORM 호환 가능 |
| 2025-09-30 | UI 프레임워크: shadcn/ui (권장) 또는 Material-UI | Refine에서 선택 가능, shadcn/ui는 Tailwind 기반으로 더 가볍고 모던함 |

- [x] **Phase 4: Write API 전환 (완료)** ✅:
  - ✅ `api/routers/contexts.py`: POST/PUT/PATCH/DELETE 엔드포인트
  - ✅ `api/schemas/context.py`: ContextCreate, ContextUpdate, FAQQACreate
  - ✅ 파일 업로드 처리 (PDF → 파싱 → 폐기)
  - ✅ 16/16 테스트 통과
  - ✅ ruff + mypy 통과
  - 예상 vs 실제: 2-3주 예상 → **2시간** 완료
  - 결정: Celery 통합 제거 (FastAPI에서 Django signal 미작동)

## Next Step
- Phase 5 Step 8: JWT 설정/환경 변수 정리 (환경 변수 템플릿 및 설정 동기화)
- Phase 6 준비: Refine Admin 통합을 위한 인증 흐름 정리

### Phase 3 완료 요약
- **전환 전략**: Option A (최소 변경) ✅ 성공
- **핵심 구현**:
  - AsyncRAGService with AsyncOpenAI
  - Redis 캐싱 (redis.asyncio)
  - sync_to_async로 Django ORM 호출 래핑
- **결과**:
  - 7개 테스트 통과 (17.43초)
  - RAG 응답 동등성 확인
  - 캐싱 동작 확인
- **예상 vs 실제**: 5-7일 예상 → **1일** 완료 (매우 효율적)
- **교훈**: 최소 변경 전략이 효과적, sync_to_async가 Django↔FastAPI 브릿지로 완벽
