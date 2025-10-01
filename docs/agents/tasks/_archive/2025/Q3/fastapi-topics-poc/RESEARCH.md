Goal | Scope | Related Files/Flows | Hypotheses | Evidence | Assumptions/Open Qs | Sub-agent Findings | Risks | Next
--- | --- | --- | --- | --- | --- | --- | --- | ---
FastAPI `/api/topics` POC가 Django `rag:topics`와 동등한 데이터를 반환하도록 최종 검증·정리. | Phase 1 항목: 엔드포인트/스키마/테스트/도커 환경 (Alembic 제외). | `api/routers/topics.py`, `api/schemas/topic.py`, `api/models/*`, `api/tests/test_topics_poc.py`, `rag/views.py`, `rag/tests/test_views.py`, `docker-compose.yml`. | 1) Django는 TopicSerializer로 contexts 포함 응답. 2) FastAPI는 SQLAlchemy 관계 + Pydantic 스키마로 동일 구조 가능. 3) Docker Compose 기반 PostgreSQL로 테스트 가능. | - `rag/views.TopicSerializer`가 contexts 중첩 포함.
- FastAPI 라우터는 `selectinload(Topic.contexts)` 사용.
- 최근 pytest 5 케이스 통과 (PostgreSQL 컨테이너 확인). | - 응답 정렬/필드 순서가 Django와 동일해야 하나 현재는 name 순 정렬; DRF도 ordering by name.
- Contexts 내부 필드 노출은 Django Serializer와 비교 필요 (현재 ContextSerializer 사용). | 없음. | - DRF 대비 누락 필드(예: system_prompt) 가능성.
- Docker 컨테이너 중단 시 테스트 실패 위험. | 1) Django Serializer 및 테스트 기준으로 FastAPI 응답 스키마 갭 체크.
2) TDD로 필드/정렬/메소드 제약 검증 테스트 작성.
3) FastAPI 구현 정비 및 문서화.
