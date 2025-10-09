# FastAPI 인증 시스템 조사

## Goal
Django 세션 기반 인증 → FastAPI JWT/OAuth2 전환 및 기존 사용자 마이그레이션

## Scope
- Django 기존 인증 구조 분석 (User 모델, session 기반)
- FastAPI 인증 라이브러리 선택 (fastapi-users vs. custom JWT)
- 기존 사용자 마이그레이션 전략 수립
- Phase 5 계획 검증 및 구체화

## Related Files/Flows

### Django 현재 인증 구조
- **User Model**: Django 기본 `django.contrib.auth.models.User` 사용
- **인증 방식**: 세션 기반 (SessionAuthentication)
  - `core/settings.py:306-308`: DRF `SessionAuthentication`
  - `core/settings.py:309-311`: `IsAuthenticatedOrReadOnly`
- **Admin 보호**: Django Admin은 `@login_required` 데코레이터 의존
- **API 보호**: DRF `IsAuthenticatedOrReadOnly` (읽기는 모두, 쓰기는 인증)

### 사용처 (grep 결과)
- 테스트 코드에서만 User 모델 사용 (8개 파일)
- 실제 API/뷰는 DRF `request.user` 의존

### FastAPI 기존 구조
- **Phase 1-4**: 인증 없음 (모든 엔드포인트 public)
- **의존성**: 없음 (`api/dependencies/` 디렉터리에 `redis.py`만 존재)

## Hypotheses

### H1: fastapi-users vs. Custom JWT
- **fastapi-users**:
  - 장점: 완전한 user management (registration, login, password reset, email verification)
  - 단점: 무거움, over-engineered (Scholaria는 admin-only 인증)
  - 오버헤드: SQLAlchemy User 모델 필수 (Django User와 충돌 가능)
- **Custom JWT (PyJWT + passlib)**:
  - 장점: 가볍고 단순, Django User 테이블 재사용
  - 단점: 직접 구현 (token refresh, blacklist)
  - 적합성: 높음 (Scholaria는 단순 인증만 필요)

### H2: 기존 사용자 마이그레이션
- **Django User 테이블 공유**:
  - SQLAlchemy로 `auth_user` 테이블 읽기 전용 접근
  - 비밀번호 검증은 Django `check_password` 호환 함수 사용
- **일회성 마이그레이션 불필요**:
  - 세션 기반 → JWT 전환은 로그인 시 자동 전환
  - 기존 사용자는 다음 로그인 시 JWT 발급받음

### H3: 하이브리드 인증 (과도기)
- **Phase 5 기간 동안**: Django Admin(세션) + FastAPI(JWT) 병렬
- **Phase 6 이후**: FastAPI만 남고 Django 제거
- **리스크**: 세션/JWT 동시 관리 복잡도

## Evidence

### Django 인증 코드 분석
```python
# core/settings.py:306-308
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.SessionAuthentication",
    ],
    # ...
}
```
- **결론**: API는 세션 쿠키 기반, stateful

### FastAPI 인증 없음
- `api/routers/*.py` 모두 public 엔드포인트
- **Phase 4**: Context Write API도 인증 없이 구현됨 (의도적)
- **리스크**: 현재 프로덕션 배포 불가 (보안 문제)

### FastAPI-Users 조사
- **설치**: `pip install fastapi-users[sqlalchemy]`
- **필수 구성**:
  - User SQLAlchemy 모델 (id, email, hashed_password, is_active, is_superuser, is_verified)
  - UserDB, UserCreate, UserUpdate Pydantic 스키마
  - JWT Strategy + Transport (Bearer token)
- **오버헤드**: 8개 엔드포인트 자동 생성 (register, login, logout, verify, forgot-password, reset-password, read users, update users)
- **평가**: Scholaria에는 과함 (admin-only 인증, user registration 불필요)

### Custom JWT 구현 예시
```python
# 최소 구현 (30줄)
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm="HS256")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)
```
- **Django 비밀번호 호환**: passlib의 `django` scheme 사용 가능

## Assumptions/Open Qs

### 가정
1. **User 모델 공유**: FastAPI는 Django `auth_user` 테이블을 읽기 전용으로 사용
2. **JWT 전용**: FastAPI는 JWT만 지원 (세션 불필요)
3. **Admin-only**: 일반 사용자 등록/관리는 Django Admin에서만 (FastAPI는 인증만)

### 열린 질문
1. **Token Refresh 필요?**: Access token 만료 시 refresh token 발급? → 단순화: access token만 (24시간 TTL)
2. **Token Storage**: JWT를 어디에 저장? → LocalStorage (XSS 위험) vs. HttpOnly Cookie (CSRF 위험) → **결정**: HttpOnly Cookie (Refine Admin에서 자동 전송)
3. **Django User 비밀번호 호환**: `pbkdf2_sha256$...` 해시 → passlib `django` scheme으로 검증 가능
4. **Logout 처리**: JWT는 stateless → 블랙리스트 필요? → **단순화**: 클라이언트에서 토큰 삭제 (서버 블랙리스트 없음)

## Sub-agent Findings
없음 (단일 에이전트로 충분)

## Risks

### High
- **Django 비밀번호 호환 실패**: passlib가 Django 해시 포맷 미지원 → 모든 사용자 비밀번호 재설정 필요
  - 완화: passlib `django` scheme 테스트 필수

### Medium
- **하이브리드 인증 복잡도**: 세션(Django) + JWT(FastAPI) 동시 관리 → 버그 가능성
  - 완화: Phase 5는 FastAPI만 JWT 구현, Django는 현상 유지

### Low
- **Token Refresh 부재**: 24시간 후 재로그인 필요 → UX 저하
  - 완화: 초기 구현 단순화, 향후 refresh token 추가 가능

## Next
**PLAN.md 작성** → 구체적인 구현 단계, 파일 목록, 테스트 케이스
## Step 7 Focus (2025-09-30)
- `api/routers/contexts.py`: POST/PUT/PATCH/DELETE/POST-qa 엔드포인트 모두 공개 상태로 운영 중, Phase 5에서 JWT 보호 필요.
- `api/dependencies/auth.py`: `require_admin` 의존성을 통해 관리자( `is_staff` )만 쓰기 작업 허용 가능.
- `api/tests/test_contexts_write.py`: 현재 인증 없이 성공을 가정하는 테스트(POST/PUT/PATCH/DELETE/FAQ 추가)로 구성되어 있어, JWT 토큰 도입 후 실패/성공 케이스 재정의 필요.
- 테스트 환경: `TestClient(app)` + SQLite 임시 DB 오버라이드(`override_get_db`). JWT 검증은 DB 세션 교체와 무관하므로 동일 설정 활용 가능.

### Assumptions
- Phase 5 초기 단계에서는 읽기 엔드포인트는 공개 유지. 쓰기 엔드포인트만 보호.
- 관리자 토큰 발급은 `/api/auth/login`으로 가능하므로 테스트에서 Django User fixture 활용 예정.

### Open Questions
- FastAPI write 라우터가 Django ORM 모델이 아닌 SQLAlchemy 세션만 사용하므로, Django User 생성이 JWT 검증에 필요한 최소 조건인지 확인 필요 (→ 인증 테스트에서 Django User 생성으로 충족).

### Risks
- `TestClient` 기반 테스트에서 Django DB와 독립된 SQLite 사용으로 인해 JWT 토큰 검증 시 사용자 조회 실패 가능성 → Django ORM 기반 fixture로 사용자 생성 후 토큰 발급, FastAPI 측 SQLAlchemy 세션에서도 동일 사용자 조회 가능한지 검증 필요.
- 기존 테스트가 전부 성공을 기대하므로, 인증 추가 후 401/403 응답을 명확히 검증해야 함.

### Findings (2025-09-30)
- per-worker SQLite 테스트 DB(`test_write_{worker}.db`) 분리로 xdist 병렬 실행 시 `auth_user` 충돌/경쟁 상태 제거.
