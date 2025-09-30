# Scholaria Project Root - Agent Knowledge Base

## Intent

MVP-완료된 학교 통합 RAG 시스템 - 문서 컨텍스트 기반 Q&A 플랫폼

## Constraints

- **TDD 필수**: Red → Green → Refactor 사이클 준수
- **코드 품질**: 커밋 전 ruff + mypy 통과 필수
- **테스트 구조**: `/tests/` 디렉터리 사용, 병렬 실행 안전성 보장
- **컨테이너화**: 모든 서비스 Docker 컨테이너 필수
- **PostgreSQL**: JSONField, 전문 검색 지원
- **Python 3.13+**: uv 패키지 매니저 사용

## Context

### 아키텍처 (Production Ready)
- **Backend**: Django 5.0+ + DRF + Admin Interface
- **Vector DB**: Qdrant (임베딩 검색)
- **Storage**: 파일 업로드 → 파싱 → 청킹 → 폐기 워크플로우 (MinIO 의존성 제거)
- **Cache**: Redis (Celery 백엔드)
- **Database**: PostgreSQL (메인 데이터)
- **AI**: OpenAI GPT + 임베딩, BGE Reranker

### 핵심 워크플로우
```bash
# 전체 품질 검사
uv run ruff check . && uv run ruff format . && uv run mypy . && uv run python manage.py test --settings=core.test_settings

# 개발 서버 실행
uv run python manage.py runserver

# Docker 서비스 시작
docker-compose up -d

# 빠른 테스트 (248개, 1-2분)
./scripts/test-fast.sh

# 느린 테스트 (33개, 통합/성능/마이그레이션)
./scripts/test-slow.sh
```

## Changelog

### 프로젝트 상태 (2025-09-30 기준)
- **MVP 완료**: 281개 테스트 통과, 모든 핵심 기능 구현 완료
- **프로덕션 준비**: Docker 배포, 보안 검증, 성능 최적화 완료
- **코드 품질**: ruff (2개 이슈), mypy 엄격 모드, pytest 병렬 실행

### 핵심 구현사항
- **데이터 모델**: Topic ↔ Context (N:N), Context → ContextItem (1:N)
- **수집 파이프라인**: Celery 백그라운드 작업으로 PDF/Markdown/FAQ 처리
  - PDF: Docling 파서 → 업로드 → 파싱 → 청킹 → 파일 폐기
  - FAQ: 2단계 생성 프로세스 (Context 생성 → Q&A 쌍 추가)
  - Markdown: 직접 편집 → 섹션별 스마트 청킹
- **검색 엔진**: 완전한 RAG 파이프라인 (임베딩 → 벡터 검색 → 리랭킹 → LLM)
- **API**: REST 엔드포인트, OpenAPI 문서화, 속도 제한
- **관리 인터페이스**: Django Admin 커스터마이징, 대량 작업, 타입별 워크플로우
- **웹 UI**: 토픽 선택, Q&A 인터페이스, 질문 히스토리

### 아키텍처 개선사항
- **Context-Topic 관계**: 1:N → N:N 변경으로 유연성 확보
- **파일 스토리지**: MinIO 의존성 제거, 임시 파일 처리 워크플로우
- **관리 워크플로우**: 타입별 Context 생성 양식, 청크 통계 표시
- **데이터베이스**: original_content, chunk_count, processing_status 필드 추가
- **라이브러리 마이그레이션**: Unstructured → Docling으로 PDF 파싱 개선

### FastAPI 마이그레이션 메모 (2025-09-30)
- SQLAlchemy가 Django DB 테이블을 직접 재사용하며 Topic↔Context 다대다 조인 테이블은 `rag_topic_contexts` (BigAuto id + `topic_id`, `context_id`).
- FastAPI POC 테스트(`api/tests/test_topics_poc.py`)는 로컬 PostgreSQL(5432) 접근이 필요하므로 샌드박스/CI에서는 연결 불가 시 실패함.
- FastAPI Pydantic 스키마는 `settings.TIME_ZONE` 기준 ISO 문자열로 datetime을 직렬화하여 Django 응답 포맷과 일치.

### 프로덕션 기능
- **모니터링**: 헬스 체크 엔드포인트, 구조화된 로깅, 성능 메트릭
- **보안**: 파일 업로드 검증, 매직 바이트 체크, 크기 제한
- **배포**: Docker Compose, 환경 변수 관리, 백업 전략
- **CI/CD**: GitHub Actions, 코드 품질 검사, 보안 스캔
