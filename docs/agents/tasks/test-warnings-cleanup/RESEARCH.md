# 테스트 경고 개선 - 조사 보고서

## 목표
테스트 실행 시 발생하는 69개 경고의 원인과 해결 방안 파악

## 경고 분석 결과

### 전체 경고 분포
```
총 경고: 69개
├─ SQLAlchemy datetime.utcnow() Deprecation: 59개 (86%)
├─ Redis close() Deprecation: 6개 (9%)
└─ FastAPI HTTP 상수 Deprecation: 4개 (6%)
```

## 1. SQLAlchemy datetime.utcnow() (59개, 최우선)

### 증상
```
DeprecationWarning: datetime.datetime.utcnow() is deprecated and scheduled for removal
Use timezone-aware objects to represent datetimes in UTC: datetime.datetime.now(datetime.UTC).
```

### 원인
- **위치**: `backend/models/*.py` (context.py, topic.py, history.py, user.py)
- **패턴**: `server_default=func.now()` 사용
- SQLAlchemy가 `func.now()`를 실행할 때 내부적으로 Python의 deprecated `datetime.utcnow()` 호출

### 영향 범위
- `Context.created_at`, `Context.updated_at` (backend/models/context.py:32-36)
- `ContextItem.created_at` (backend/models/context.py:75)
- `Topic.created_at`, `Topic.updated_at` (backend/models/topic.py:26-30)
- `QuestionHistory.created_at` (backend/models/history.py:30)

### 해결 방안 (3가지 옵션)

#### 옵션 A: DB 네이티브 함수 (권장) ⭐
```python
from sqlalchemy import text

created_at: Mapped[datetime] = mapped_column(
    server_default=text("(CURRENT_TIMESTAMP)"), nullable=False
)
```
**장점**: DB 레벨 기본값, Python deprecation 회피, 성능 우수
**단점**: DB 벤더 의존적 (PostgreSQL/SQLite 모두 지원하므로 문제없음)

#### 옵션 B: ORM 레벨 기본값
```python
from datetime import datetime, timezone

created_at: Mapped[datetime] = mapped_column(
    default=lambda: datetime.now(timezone.utc), nullable=False
)
```
**장점**: DB 독립적, timezone-aware
**단점**: DB 레벨 기본값 없음, 마이그레이션 필요

#### 옵션 C: SQLAlchemy 설정 조정
SQLAlchemy 2.0+ 설정으로 경고 억제
**장점**: 코드 변경 최소
**단점**: 근본 해결 아님, Python 3.13+ 제거 시 문제

### 선택: **옵션 A (DB 네이티브 함수)**
- 이유: 프로덕션 환경(PostgreSQL + SQLite 테스트) 모두 `CURRENT_TIMESTAMP` 지원
- 마이그레이션: 기존 `server_default` 유지되므로 데이터 변경 불필요

## 2. Redis aclose() Deprecation (6개)

### 증상
```
DeprecationWarning: Call to deprecated close. (Use aclose() instead)
-- Deprecated since version 5.0.1.
```

### 원인
- **위치**: `backend/dependencies/redis.py:29`
- **코드**: `await client.close()`
- redis-py 5.0.1+에서 async client는 `aclose()` 권장

### 현재 환경
- **설치된 버전**: redis 6.4.0
- **pyproject.toml**: `redis[hiredis]>=5.0.0`

### 해결 방안
```python
# Before
await client.close()

# After
await client.aclose()
```

### 영향
- RAG 엔드포인트 테스트 6개 (test_rag_endpoint.py)
- 프로덕션 코드 1개 파일만 수정

## 3. FastAPI HTTP 상수 Deprecation (4개)

### 증상
```
DeprecationWarning: 'HTTP_422_UNPROCESSABLE_ENTITY' is deprecated.
Use 'HTTP_422_UNPROCESSABLE_CONTENT' instead.
```

### 원인
- FastAPI/Starlette HTTP 상수 명칭 변경 (RFC 9110 준수)
- 구 명칭: `HTTP_422_UNPROCESSABLE_ENTITY`, `HTTP_413_REQUEST_ENTITY_TOO_LARGE`
- 신 명칭: `HTTP_422_UNPROCESSABLE_CONTENT`, `HTTP_413_CONTENT_TOO_LARGE`

### 영향 위치
1. `test_contexts_write.py::test_create_context_invalid_type_fails` (HTTP_422)
2. `test_contexts_write.py::test_upload_file_too_large_fails` (HTTP_413)
3. `test_rag_endpoint.py::test_ask_question_empty_question_fails` (HTTP_422)
4. `test_rag_endpoint.py::test_ask_question_invalid_topic_id_fails` (HTTP_422)

### 해결 방안
테스트 코드에서 직접 status code 사용하지 않고, 새 상수로 교체:
```python
# Before
assert response.status_code == 422

# After (if using constant)
from starlette.status import HTTP_422_UNPROCESSABLE_CONTENT
assert response.status_code == HTTP_422_UNPROCESSABLE_CONTENT
```

**또는** 숫자 리터럴 사용 (더 간단):
```python
assert response.status_code == 422
```

## pytest.ini 현재 상태
```ini
addopts = --tb=short --strict-markers --disable-warnings
```
- `--disable-warnings`로 경고 숨김 중
- 해결 완료 후 제거 예정

## 가설 및 검증

### 가설 1: SQLAlchemy 경고는 모델 정의 시점 발생 ✅
**검증**: `server_default=func.now()` 사용하는 모든 모델에서 발생
**결과**: 59개 경고의 원인 확인 완료

### 가설 2: Redis 경고는 의존성 cleanup 시점 발생 ✅
**검증**: `get_redis()` 함수의 `finally` 블록
**결과**: RAG 테스트 6개에서만 발생 (Redis 사용하는 엔드포인트)

### 가설 3: HTTP 상수 경고는 anyio/pytest 래핑 레이어에서 발생 ✅
**검증**: 스택 트레이스에 `anyio/_backends/_asyncio.py` 또는 `_pytest/python.py` 표시
**결과**: 테스트 프레임워크가 상수를 참조할 때 경고 발생

## 리스크 평가

### 낮은 리스크 ✅
- **Redis aclose()**: 단순 메서드 명칭 변경, 동작 동일
- **HTTP 상수**: 테스트 검증 로직만 영향, 실제 API 동작 무관

### 중간 리스크 ⚠️
- **SQLAlchemy datetime**: 타임스탬프 생성 방식 변경
  - **완화 방안**: 기존 테스트로 동작 검증, DB 기본값은 유지

## 다음 단계
1. Redis aclose() 수정 (5분, 낮은 리스크)
2. SQLAlchemy datetime 수정 (30분, 중간 리스크 - 테스트 필수)
3. HTTP 상수 수정 (10분, 낮은 리스크)
4. pytest.ini 정리 (5분)
5. 전체 테스트 실행 및 검증 (10분)
