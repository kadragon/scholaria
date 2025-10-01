# Tasks: Scholaria RAG System

## 🎉 프로젝트 상태: MVP 완료 & 프로덕션 준비

✅ **100개 테스트 통과 | Django→FastAPI 전환 완료 | 배포 준비 완료**

---

## 📋 현재 활성 태스크

### 관리 인터페이스 개선
- [x] **청크 미리보기** ✅ (`docs/agents/tasks/chunk-preview-ui/`)
- [x] **청크 편집** ✅ (`docs/agents/tasks/chunk-edit-feature/`)
- [x] **청크 재정렬** ✅ (`docs/agents/tasks/chunk-reorder-ui/`)
- [x] **타입별 청킹 전략** ✅ (`docs/agents/tasks/chunking-strategy-refactor/`) - 전략 패턴 리팩터링

---

## ✅ 완료된 주요 마일스톤

### Django → FastAPI 전환 ✅
- **Phase 1-6**: 기반 구조, Read/Write API, 인증, Admin Panel, Docker/Nginx 통합 완료
- **Phase 8**: Django 100% 제거, `backend/` + `frontend/` 모노레포 구조
- **문서**: `docs/agents/tasks/django-to-fastapi-migration/`, `django-removal-and-refactoring/`

### 컨텍스트 관리 시스템 ✅
- **타입별 워크플로우**: PDF/FAQ/Markdown 전용 UI + 청킹 전략
- **N:N 관계**: Topics ↔ Contexts 다대다 매핑
- **청크 관리**: 미리보기 + 편집 기능

### 프로덕션 준비 ✅
- Docker Compose + Nginx 리버스 프록시
- JWT 인증 + 환경변수 관리
- Alembic 마이그레이션 + 백업 전략
- 100% 테스트 커버리지 (100 tests passing)

### 라이브러리 마이그레이션 ✅
- Unstructured → Docling (PDF 파싱)
- Pydantic v2 ConfigDict 전환
- Django ORM → SQLAlchemy 완전 전환

---

## 🚀 향후 개선사항 (Backlog)

### 비동기 인프라 복원
- [x] **Celery/비동기 큐 재도입** ✅ (`docs/agents/tasks/celery-async-queue/`) - 임베딩 재생성 비동기화
- [x] **Redis 공유 캐시** ✅ (`docs/agents/tasks/redis-shared-cache/`) - 수평 확장 지원

### 성능 검증 및 최적화
- [ ] **실제 환경 성능 벤치마크** (프로덕션 배포 후):
  - 테스트 쿼리의 80% 이상에서 관련 인용 반환 검증
  - 일반적인 쿼리에 대해 답변 지연시간 3초 미만 보장
  - 동시 사용자 부하 테스트 수행

### 선택적 기능
- [ ] 다크 모드
- [x] **피드백 시스템 (좋아요/싫어요)** ✅ (`docs/agents/tasks/feedback-system/`)
- [ ] 다국어 지원
- [ ] 분석 대시보드
- [ ] SSO 통합

---

## 🎯 Quick Start

```bash
# Quality checks
uv run ruff check . && uv run mypy . && uv run pytest

# Dev server
uv run uvicorn backend.main:app --reload

# Docker
docker compose -f docker-compose.yml -f docker-compose.dev.yml up --build

# Migrations
uv run alembic upgrade head
```

## 📊 Production Readiness
- ✅ 122 tests passing | mypy strict | ruff clean
- ✅ JWT auth + admin API
- ✅ Docker + Nginx production config
- ✅ FastAPI + SQLAlchemy + Refine + shadcn/ui
- ✅ 전략 패턴 기반 인제스션 아키텍처
- ✅ Celery + Redis 비동기 작업 큐

## 🎯 다음 우선순위
1. [x] **프로덕션 배포 준비** ✅ - Celery 워커 설정 완료 (`docs/agents/tasks/production-deployment/`)
2. **성능 벤치마크** - 실제 데이터로 검증 (프로덕션 배포 후)
3. **Celery 모니터링** - Flower 등 대시보드 추가 (선택적)
