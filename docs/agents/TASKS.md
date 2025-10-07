# Tasks: Scholaria RAG System

## 상태 스냅샷
- MVP 완성, FastAPI + Refine 스택 프로덕션 준비 완료
- 134개 테스트 통과, ruff/mypy 클린, Celery/Redis 비동기 인프라 운영 중
- 세부 이력은 `docs/agents/tasks/_archive/` 및 `TASKS_ARCHIVE_INDEX.md` 참고

## 진행 중
- [ ] **성능 벤치마크** — 프로덕션 데이터 기준 관련 인용 80% 이상, 응답 지연 3초 미만, 동시 사용자 부하 테스트 수행

## 단기 백로그
- [ ] **Frontend README 정리** — `frontend/README.md` TODO 목록을 최신 상태로 반영하고 완료 항목 체크
- [ ] **Admin datetime 직렬화** — `backend/schemas/admin.py`의 `AdminTopicOut`, `AdminContextOut`에 ISO 포맷 직렬화 추가
- [ ] **운영 데이터 백업/복원 가이드** — PostgreSQL 및 Qdrant 백업·복원 절차 수립, 자동화 스크립트와 복구 리허설 포함
- [ ] **다크 모드** — UI 테마 토글 및 사용자 선호 저장
- [ ] **다국어 지원** — 핵심 UI 번역 및 Q&A 프롬프트 대응
- [ ] **SSO 통합** — 우선순위 공급자 결정 후 인증 흐름 통합

## 선택적 향상안
- [ ] **성능 관측 강화** — OpenTelemetry + 대시보드로 RAG 체인의 메트릭 가시화
- [ ] **피드백 루프 확장** — 좋아요/싫어요 외에 자유 서술 피드백 수집 UX 추가

## 최근 완료 하이라이트
- FastAPI 전환, 인제스션 워크플로우, Refine 기반 Admin UI, 스트리밍 Q&A 인터페이스 제공 완료
- Celery + Redis 재도입으로 임베딩 재생성 및 캐시 공유 인프라 복원

## 운영 참고
- 품질 점검: `uv run ruff check . && uv run mypy . && uv run pytest`
- 개발 서버: `uv run uvicorn backend.main:app --reload`
- Docker(dev): `docker compose -f docker-compose.yml -f docker-compose.dev.yml up --build`
- 마이그레이션: `uv run alembic upgrade head`
