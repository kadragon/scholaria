# Tasks: Scholaria RAG System

## 🎉 프로젝트 상태: MVP 완료 & 프로덕션 준비

✅ **281개 테스트 통과 | 모든 핵심 기능 구현 완료 | 배포 준비 완료**

---

## 📋 현재 활성 태스크

### Django → FastAPI 전환 (진행 중)

- [x] **조사 & 계획 완료**:
  - [x] 전환 동기 명확화: Django 무게감 제거
  - [x] 관리 UI 전략 결정: Refine Admin Panel
  - [x] React 라이브러리 결정: Refine (헤드리스, FastAPI와 철학 일치)
  - [x] 8단계 상세 계획 수립 (12-18주)
- [x] **Phase 1: 기반 구조 준비** (1-2주) ✅ 완료:
  - [x] POC: 단일 엔드포인트 전환 (GET /api/topics)
  - [x] FastAPI + SQLAlchemy + Alembic 환경 구축
  - [x] ▶ Docker 하이브리드 구성 (Django 8000 + FastAPI 8001) (slug: docker-hybrid-compose)
  - [x] ▶ FastAPI Topic↔Context 관계 매핑 (slug: fastapi-topic-context-relations)
  - [x] ▶ FastAPI Context DB 동기화 (slug: fastapi-contexts-transaction)
- [x] **Phase 2: Read-Only API 전환** (1-2주) ✅ 완료:
  - [x] ▶ FastAPI history read API (slug: fastapi-readonly-api)
  - [x] Topics, Contexts, History 조회 API 구현
  - [x] Django API 응답 동등성 검증
- [x] **Phase 3: RAG 엔드포인트 전환** (완료) ✅:
  - [x] ▶ FastAPI RAG endpoint (slug: fastapi-rag-endpoint)
  - POST /api/rag/ask 구현 (Django AskQuestionView 포팅)
  - Redis 캐싱, AsyncOpenAI, sync_to_async (Django ORM 호환)
  - 7개 테스트 통과
- [x] **Phase 4: Write API 전환** (2-3주) ✅ **완료 (2시간)**:
  - [x] ▶ FastAPI Context Write API (slug: fastapi-write-api)
  - POST/PUT/DELETE /api/contexts 구현
  - 파일 업로드 (UploadFile), PDF/Markdown/FAQ 타입별 워크플로우
  - 16/16 테스트 통과
  - 결정: Celery 통합 제거 (FastAPI에서 Django signal 미작동)
- [ ] **Phase 5-8**: 인증 → Refine Admin → 프론트엔드 → Django 제거 ⬅️ 다음 단계
  - [x] ▶ FastAPI auth write protection (slug: fastapi-auth) — Step 7: apply JWT admin guard to write APIs
  - [ ] ▶ FastAPI auth env sync (slug: fastapi-auth) — Step 8: expose JWT settings & env templates
- **문서**: `docs/agents/tasks/django-to-fastapi-migration/` (RESEARCH, PLAN, PROGRESS)
- **예상 기간**: 12-18주, Critical: Phase 6 (Refine Admin 4-6주)
- **주요 기술**: FastAPI + SQLAlchemy + Refine + shadcn/ui + React Query

### 성능 검증 및 최적화

- [x] **성능 테스트 인프라 검증** ✅ 완료:
  - [x] `test_performance_benchmarks.py`: 6/6 테스트 통과
  - [x] `test_golden_dataset.py`: 5/5 테스트 통과
  - [x] PerformanceBenchmark 클래스 정상 동작 확인
  - [x] GoldenDataset (24 test cases) 정상 동작 확인
  - 결론: 성능 벤치마크 인프라 준비 완료, 실제 데이터 벤치마크는 프로덕션 배포 후 수행
- [ ] **실제 환경 성능 벤치마크** (프로덕션 배포 후):
  - [ ] 테스트 쿼리의 80% 이상에서 관련 인용 반환 검증
  - [ ] 일반적인 쿼리에 대해 답변 지연시간 3초 미만 보장
  - [ ] 동시 사용자 부하 테스트 수행
  - [ ] 메모리 사용량 모니터링 및 필요시 최적화

### 관리 인터페이스 개선

- [ ] **향상된 청크 관리**:
  - [ ] 콘텐츠 미리보기가 포함된 청크 시각화 개선
  - [ ] 청크 레벨 편집 기능 추가
  - [ ] 청크 재정렬 및 관리 도구 구현
  - [ ] 실시간 처리 상태 업데이트 추가

- [ ] **타입별 콘텐츠 프로세서**:
  - [ ] 더 나은 컨텍스트 타입 처리를 위한 파싱 로직 리팩터링
  - [ ] 타입별 더 스마트한 자동 청킹 전략 구현
  - [ ] 포괄적인 처리 파이프라인 상태 추적 추가
  - [ ] 불필요한 파일 스토리지 의존성 완전 제거

---

## ✅ 완료된 주요 마일스톤

### 컨텍스트 관리 시스템 ✅ 완료

#### **컨텍스트 타입별 워크플로우**
- [x] **PDF 컨텍스트 향상**: ✅ 완료
  - [x] PDF 스토리지에 대한 MinIO 의존성 제거 ✅
  - [x] 업로드 → 파싱 → 청킹 → 파일 폐기 워크플로우 구현 ✅
  - [x] 파일 보존 없이 청크 미리보기 추가 ✅
  - [x] PDF 전용 워크플로우용 관리 인터페이스 업데이트 ✅

- [x] **FAQ 컨텍스트 향상**: ✅ 완료
  - [x] 2단계 FAQ 생성 프로세스 생성 (컨텍스트 생성 → Q&A 추가) ✅
  - [x] 컨텍스트 관리 내 Q&A 쌍 관리 인터페이스 구현 ✅
  - [x] 전용 FAQ 청크 관리 추가 (1 Q&A 쌍 = 1 청크) ✅
  - [x] FAQ 전용 인라인 편집기 생성 ✅

- [x] **Markdown 컨텍스트 향상**: ✅ 완료
  - [x] original_content 필드에서 직접 마크다운 편집 활성화 ✅
  - [x] 스마트 마크다운 청킹 전략 구현 ✅
  - [x] 마크다운 미리보기 및 렌더링 기능 추가 ✅
  - [x] 마크다운 전용 관리 인터페이스 생성 ✅

- [x] **컨텍스트 타입 선택 워크플로우**: ✅ 완료
  - [x] context_type 선택에 기반한 동적 폼 전환 구현 ✅
  - [x] 타입별 생성 양식 생성 ✅
  - [x] 상황별 도움말 및 워크플로우 가이드 추가 ✅

### Development Documentation ✅ COMPLETED
- [x] Contributing guidelines ✅ COMPLETED
- [x] Testing strategy documentation ✅ COMPLETED
- [x] Architecture decision records ✅ COMPLETED

### Production Setup ✅ COMPLETED
- [x] Production Docker Compose configuration ✅ COMPLETED
- [x] Environment variable management ✅ COMPLETED
- [x] Database backup strategy ✅ COMPLETED
- [x] Log aggregation and monitoring ✅ COMPLETED
- [x] Health check endpoints ✅ COMPLETED

### Architecture Improvements (Completed)

- [x] **Refactor Context-Topic Relationship**: Change from 1:N to N:N relationship between Topics and Contexts ✅ COMPLETED
- [x] **Improve Context Model Structure**: ✅ COMPLETED
  - 1 Context = 1 PDF document OR 1 Markdown file OR Multiple FAQ items ✅
  - Hide individual chunks from admin interface - show only Context-level view ✅
  - Context detail view should show chunk statistics (e.g., "25 chunks, 15,487 characters") ✅
- [x] **Enhanced Admin Interface**: ✅ COMPLETED
  - Context creation workflow: select type → upload file → automatic chunking (hidden from user) ✅
  - Context detail page: show full content, chunk count, processing status ✅
  - Topic management: multi-select contexts to associate with topics ✅
- [x] **Database Schema Updates**: ✅ COMPLETED
  - Add Context.original_content field to store full document text ✅ COMPLETED
  - Add Context.chunk_count and Context.processing_status fields ✅ COMPLETED
  - Update Context-Topic relationship to ManyToMany ✅ COMPLETED
  - Create migration scripts for existing data ✅ COMPLETED
- [x] **Update Admin Views**: ✅ COMPLETED
  - Remove ContextItem from main admin navigation ✅ COMPLETED
  - Create custom Context admin with file upload and chunk preview ✅ COMPLETED
  - Add inline Context selector to Topic admin ✅ COMPLETED
- [x] **API Endpoint Updates**: ✅ COMPLETED
  - Update context endpoints to return full content + metadata ✅ COMPLETED
  - Add chunk-level endpoints for internal use only ✅ COMPLETED
  - Update topic endpoints to handle multiple contexts ✅ COMPLETED

### Library Migration: Unstructured → Docling ✅ COMPLETED
- [x] **Update Dependencies**: Remove `unstructured`, add `docling` ✅
- [x] **Refactor PDF Parser**: Replace Unstructured with Docling API ✅
- [x] **Update Tests**: All ingestion and Docker tests updated ✅
- [x] **Validate Migration**: 134 tests passing with new implementation ✅
- [x] **Clean Up**: Removed unused code, updated documentation ✅

---

---

## 🚀 향후 개선사항 (선택사항)

### 향상된 Q&A 사용자 인터페이스 ✅ 대부분 완료

- [x] 실시간 타이핑 인디케이터 및 더 나은 UX 애니메이션 추가 ✅ 완료
- [x] 질문 히스토리 및 즐겨찾기 기능 구현 ✅ 완료
- [x] 모바일 반응형 개선 및 터치 최적화 추가 ✅ 완료
- [x] 더 나은 네비게이션으로 개선된 랜딩 페이지 생성 ✅ 완료
- [x] 토픽 콘텐츠 기반 질문 제안 추가 ✅ 완료

**선택적 완성 항목:**
- [ ] 다크 모드 지원 및 테마 전환 추가
- [ ] 파워 유저를 위한 키보드 단축키 구현

### 피드백 시스템

- [ ] 피드백 데이터 모델 설계
- [ ] 좋아요/싫어요 기능 구현
- [ ] 피드백 분석 생성

### 다국어 지원

- [ ] 다국어 임베딩 모델 연구
- [ ] 언어 감지 구현
- [ ] 언어별 처리 추가

### 분석 대시보드

- [ ] 분석 데이터 모델 설계
- [ ] 쿼리 추적 구현
- [ ] 분석 대시보드 생성
- [ ] 성능 메트릭 추가

### 인증 및 권한 부여

- [ ] SSO 통합 옵션 연구
- [ ] 사용자 인증 구현
- [ ] 역할 기반 접근 제어 추가
- [ ] 학교 디렉터리 시스템과 통합

---

## 🎯 Quick Start Commands

```bash
# Run all quality checks
uv run ruff check . && uv run mypy . && uv run python manage.py test --settings=core.test_settings

# Start development server
uv run python manage.py runserver

# Start Docker services
docker-compose up -d

# Apply migrations (if needed)
uv run python manage.py migrate
```

---

## ✅ Production Readiness Checklist

- ✅ All 134 tests passing
- ✅ Type safety with mypy strict mode
- ✅ Code quality with ruff linting
- ✅ Comprehensive error handling
- ✅ API rate limiting and validation
- ✅ Database migrations ready
- ✅ Docker containerization complete

## 📊 MVP Success Metrics - ALL ACHIEVED ✅

- ✅ Admin can upload PDF/FAQ/Markdown and connect to topics
- ✅ User can ask a question in a selected topic and get an answer with citations
- ✅ Ingestion pipeline runs automatically with proper error handling
- ✅ All tests passing (134/134 tests pass)
- ✅ No critical security vulnerabilities
- ✅ Code coverage targets achieved
- ✅ Type safety enforced with mypy strict mode
- ✅ Production Docker configuration ready
- ✅ Comprehensive documentation complete

## 🎯 현재 집중 영역

프로젝트의 **핵심 MVP가 완료**되었으므로, 현재는 다음에 집중:

1. **성능 검증**: 실제 환경에서의 응답 품질과 속도 테스트
2. **관리 인터페이스 개선**: 청크 관리 및 처리 상태 표시 향상
3. **선택적 기능**: 다크 모드, 피드백 시스템 등 부가 기능

### 다음 우선순위

1. **성능 벤치마크 실행** - 현재 RAG 파이프라인의 실제 성능 측정
2. **청크 관리 UI 개선** - 관리자를 위한 더 직관적인 콘텐츠 관리 도구
3. **코드 품질 유지** - ruff 이슈 해결 (현재 2개), 테스트 커버리지 유지

### 장기 목표

- **확장성**: 다중 학교/기관 지원을 위한 멀티테넌시
- **고급 기능**: AI 기반 콘텐츠 분류, 자동 태그 생성
- **통합**: 기존 LMS(Learning Management System)와의 연동
