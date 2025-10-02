# Django → FastAPI 전환 조사

## Goal
현재 Django 기반 Scholaria RAG 시스템을 FastAPI로 전환하기 위한 타당성 분석 및 이행 전략 수립

## Scope
- 현재 Django 구조 분석
- FastAPI 전환 시 이점/위험 평가
- 단계별 마이그레이션 경로 식별
- 기존 기능 보존 방안

## Related Files/Flows

### 핵심 Django 구조
- **설정**: `core/settings.py`, `core/urls.py`, `core/wsgi.py`, `core/asgi.py`
- **모델**: `rag/models.py` (Topic, Context, ContextItem, QuestionHistory)
- **뷰/API**: `rag/views.py` (DRF APIView, GenericView), `rag/web_urls.py` (템플릿 뷰)
- **관리자**: `rag/admin.py` (Django Admin 커스터마이징)
- **백그라운드 작업**: `core/celery.py`, `rag/tasks.py` (Celery 통합)
- **인증/권한**: Django 세션 기반, DRF 인증
- **미들웨어**: `core/logging.py` (요청 로깅)
- **템플릿**: `templates/` (Django 템플릿 엔진)

### 핵심 의존성
- Django 5.0+, DRF 3.14+
- PostgreSQL (django.db)
- Redis (django-redis cache)
- Celery 5.3+ (django-celery-beat)
- OpenAPI: drf-spectacular

### 현재 규모
- 381개 테스트 (pytest)
- ~23,792 Python 파일 (프로젝트 + 의존성)
- 프로덕션 배포 완료 (Docker Compose)

## Hypotheses

### 전환 시 예상 이점
1. **성능**: 비동기 I/O, 더 낮은 메모리 오버헤드 (예상 20-40% 응답 시간 단축)
2. **타입 안전성**: Pydantic 네이티브 통합, 자동 검증
3. **OpenAPI**: 더 나은 문서화 지원 (drf-spectacular → 네이티브)
4. **간결성**: 보일러플레이트 코드 감소

### 전환 시 예상 손실/위험
1. **관리 인터페이스**: Django Admin 완전 손실 → 별도 구축 필요 (대규모 작업)
2. **ORM**: Django ORM → SQLAlchemy/Tortoise/Raw SQL (학습 곡선, 코드 재작성)
3. **인증/세션**: Django 세션 → JWT/OAuth2 재구현
4. **템플릿**: Django templates → Jinja2 또는 프론트엔드 분리
5. **마이그레이션 도구**: Django migrations → Alembic
6. **테스트 인프라**: django-pytest → 순수 pytest (DB 픽스처 재작성)
7. **플러그인 생태계**: django-celery-beat 등 Django 전용 패키지 대체 필요

## Evidence

### Django Admin 사용량 (Critical)
- `rag/admin.py` 500+ 줄 (타입별 Context 워크플로우, 인라인 편집, 대량 작업)
- 관리자 템플릿 커스터마이징: `templates/admin/` (7개 파일)
- Admin은 **현재 MVP의 핵심 UX** → 전환 시 완전 재구축 필요

### API vs Web 비중
- **API**: 10개 엔드포인트 (Topics, Contexts, RAG, History)
- **Web**: 3개 템플릿 뷰 (topic selection, Q&A interface)
- **결론**: API 중심이지만 관리 인터페이스 의존도 높음

### Celery 통합
- `rag/tasks.py`: 비동기 임베딩 생성, 백그라운드 작업
- FastAPI 대안: `celery` 유지 가능 (FastAPI와 독립적), 또는 `dramatiq`, `arq`

### 마이그레이션 도구
- Django: `migrations/` (6개 마이그레이션 파일)
- FastAPI: Alembic으로 전환 필요 (호환 가능, 추가 작업)

## Assumptions/Open Questions

### 가정
- 비즈니스 요구사항 변경 없음 (기존 기능 유지)
- 프로덕션 다운타임 최소화 요구
- 팀 FastAPI 경험 부족 (학습 시간 필요)

### 해결된 질문
1. **관리 인터페이스**: ✅ **Refine + FastAPI Admin API** (Option A 선택)
   - 이유: Django 무게감 제거, 모던 UX, 완전한 커스터마이징 가능
   - 예상 기간: 4-6주
2. **ORM**: SQLAlchemy 2.0 (비동기 지원, 성숙도)
3. **인증**: JWT 전환 (fastapi-users 라이브러리)
4. **React Admin 라이브러리**: ✅ **Refine** (vs React-Admin vs Custom)
   - **Refine 장점**:
     - 헤드리스 아키텍처 → FastAPI와 철학 일치 (유연성, 커스터마이징)
     - 15+ 백엔드 통합 (REST, GraphQL 네이티브 지원)
     - 빌트인 Data Provider 패턴 → FastAPI API 연동 간단
     - shadcn/ui, Ant Design, Material-UI, Mantine, Chakra UI 선택 가능
     - React Query 기반 → 캐싱, 낙관적 업데이트 자동
     - 엔터프라이즈 기능: 인증, 권한, 감사 로그, 멀티테넌시
     - Y Combinator 백킹, 성숙한 커뮤니티
   - **React-Admin 대비**:
     - React-Admin: Material-UI 고정, 더 무겁고 제약적
     - Refine: UI 프레임워크 자유 선택, 더 가벼움, 비동기 친화적

### 미해결 질문
1. **템플릿**: 프론트엔드 완전 분리 시기? (Phase 7 또는 Phase 6과 병행)
2. **Refine UI 프레임워크**: shadcn/ui (모던, Tailwind) vs Material-UI (풍부한 컴포넌트)?

## Risks

### High Risk
- **관리 인터페이스 공백**: 전환 중 관리 기능 상실 (운영 중단)
- **대규모 재작성**: ORM, 인증, 관리 → 버그 유입 가능성 높음
- **테스트 커버리지 저하**: 381개 테스트 재작성 중 누락 가능

### Medium Risk
- **성능 검증**: 실제 환경에서 FastAPI 이점 미미할 수 있음
- **팀 생산성**: 학습 곡선으로 단기 개발 속도 저하
- **플러그인 호환성**: Qdrant, MinIO 클라이언트는 문제 없으나 Celery Beat 등 재검증 필요

### Low Risk
- Docker 배포: FastAPI도 동일하게 컨테이너화 가능
- OpenAI/Qdrant 통합: 프레임워크 독립적

## Next Steps

1. **비즈니스 목표 명확화**: 왜 전환하는가? (성능? 기술 스택 통일? 트렌드?)
2. **관리 인터페이스 전략 결정**: Option A/B/C 선택 (가장 큰 변수)
3. **POC 수행**: 소규모 엔드포인트 FastAPI 전환 (1-2주)
4. **상세 계획 수립**: 단계별 마이그레이션 타임라인, 리소스, 롤백 전략
