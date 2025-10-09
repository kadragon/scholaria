# Authentication Specification

## Context & Goal

**Context**: Scholaria는 Django 세션 기반 인증에서 FastAPI JWT 기반 인증으로 전환합니다. 기존 Django User 테이블을 재사용하여 최소 변경으로 구현하며, Phase 5 기간 동안 Django Admin(세션) + FastAPI(JWT)를 병렬 운영합니다.

**Goal**: FastAPI 엔드포인트에 JWT 기반 인증을 적용하여 관리자(admin)만 Write 작업을 수행할 수 있도록 보호하되, Read 엔드포인트는 public으로 유지합니다.

## Scope

**In Scope**:
- JWT 토큰 생성 및 검증
- Django `auth_user` 테이블 읽기 전용 접근 (SQLAlchemy 모델)
- Django 비밀번호 해시 포맷 호환 (`pbkdf2_sha256$...`)
- 인증 의존성: `get_current_user`, `require_admin`
- 인증 엔드포인트: `/api/auth/login`, `/api/auth/me`
- Write 엔드포인트 보호 (POST/PUT/PATCH/DELETE)

**Out of Scope**:
- 사용자 등록/비밀번호 재설정 (Django Admin에서 처리)
- Token refresh/blacklist (초기 단순화)
- 세션 기반 인증 (Django Admin 전용)
- OAuth2 소셜 로그인

## Contract

### 1. User Model (SQLAlchemy, Read-Only)

**위치**: `backend/models/user.py`

```python
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from backend.models.base import Base

class User(Base):
    __tablename__ = "auth_user"  # Django auth_user 테이블

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String(150), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(254))
    password: Mapped[str] = mapped_column(String(128), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_staff: Mapped[bool] = mapped_column(Boolean, default=False)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False)
    first_name: Mapped[str] = mapped_column(String(150))
    last_name: Mapped[str] = mapped_column(String(150))
    date_joined: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    last_login: Mapped[datetime] = mapped_column(DateTime)
```

**제약**:
- FastAPI는 이 모델을 읽기 전용으로만 사용 (INSERT/UPDATE/DELETE 금지)
- Django Admin에서만 사용자 생성/수정

### 2. Authentication Utilities

**위치**: `backend/auth/utils.py`

#### 함수: `verify_password(plain_password: str, hashed_password: str) -> bool`

Django `pbkdf2_sha256` 해시 포맷과 호환되는 비밀번호 검증.

**입력**:
- `plain_password`: 평문 비밀번호
- `hashed_password`: Django 해시 포맷 (`pbkdf2_sha256$600000$...`)

**출력**: `True` (일치) / `False` (불일치)

**구현**:
```python
from passlib.context import CryptContext

pwd_context = CryptContext(
    schemes=["django_pbkdf2_sha256", "bcrypt"],
    deprecated="auto"
)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)
```

#### 함수: `create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str`

JWT 액세스 토큰 생성.

**입력**:
- `data`: 토큰에 포함할 페이로드 (예: `{"sub": user_id}`)
- `expires_delta`: 만료 시간 (기본: 24시간)

**출력**: JWT 문자열

**구현**:
```python
from jose import jwt
from datetime import datetime, timedelta

SECRET_KEY = "your-secret-key"  # 환경 변수에서 로드
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = 24

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
```

#### 함수: `decode_access_token(token: str) -> Optional[dict]`

JWT 토큰 디코드 및 검증.

**입력**: JWT 문자열

**출력**: 페이로드 dict / `None` (검증 실패)

**구현**:
```python
from jose import JWTError, jwt

def decode_access_token(token: str) -> Optional[dict]:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None
```

### 3. Authentication Dependencies

**위치**: `backend/dependencies/auth.py`

#### 의존성: `get_current_user(token: str, db: Session) -> User`

JWT 토큰에서 현재 사용자를 추출하고 DB에서 조회.

**입력**:
- `token`: Bearer 토큰 (OAuth2PasswordBearer)
- `db`: SQLAlchemy 세션

**출력**: `User` 객체

**에러**:
- `401 UNAUTHORIZED`: 토큰 없음/만료/잘못됨
- `401 UNAUTHORIZED`: 사용자 DB에 없음

**구현**:
```python
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception

    user_id: int = payload.get("sub")
    if user_id is None:
        raise credentials_exception

    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise credentials_exception

    return user
```

#### 의존성: `require_admin(current_user: User) -> User`

관리자 권한 검증 (is_staff=True).

**입력**: `current_user` (Depends(get_current_user))

**출력**: `User` 객체

**에러**:
- `403 FORBIDDEN`: `is_staff=False`

**구현**:
```python
async def require_admin(current_user: User = Depends(get_current_user)) -> User:
    if not current_user.is_staff:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )
    return current_user
```

### 4. Authentication Endpoints

**위치**: `backend/routers/auth.py`

#### POST `/api/auth/login`

사용자 로그인 및 JWT 토큰 발급.

**요청 (Form Data)**:
```
username: string (required)
password: string (required)
```

**응답 (200 OK)**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**에러**:
- `401 UNAUTHORIZED`: 잘못된 username/password
- `403 FORBIDDEN`: `is_active=False`

**Pydantic Schema**:
```python
class Token(BaseModel):
    access_token: str
    token_type: str
```

**구현 로직**:
1. DB에서 username으로 사용자 조회
2. `verify_password()`로 비밀번호 검증
3. `is_active` 확인
4. `create_access_token({"sub": user.id})` 생성
5. Token 응답

#### GET `/api/auth/me`

현재 로그인한 사용자 정보 조회.

**요청 Header**:
```
Authorization: Bearer {token}
```

**응답 (200 OK)**:
```json
{
  "id": 1,
  "username": "admin",
  "email": "admin@example.com",
  "is_staff": true,
  "is_superuser": true
}
```

**에러**:
- `401 UNAUTHORIZED`: 토큰 없음/만료/잘못됨

**Pydantic Schema**:
```python
class UserOut(BaseModel):
    id: int
    username: str
    email: str
    is_staff: bool
    is_superuser: bool

    model_config = ConfigDict(from_attributes=True)
```

### 5. Protected Endpoints

Write 엔드포인트에 `require_admin` 의존성 적용.

**적용 대상** (`backend/routers/contexts.py`):
- `POST /api/contexts`
- `PUT /api/contexts/{id}`
- `PATCH /api/contexts/{id}`
- `DELETE /api/contexts/{id}`
- `POST /api/contexts/{id}/qa` (FAQ 추가)

**예시**:
```python
from backend.dependencies.auth import require_admin
from backend.models.user import User

@router.post("/", response_model=ContextOut)
async def create_context(
    context_data: ContextCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)  # 추가
):
    # ...
```

**Read 엔드포인트 (Public 유지)**:
- `GET /api/contexts`
- `GET /api/contexts/{id}`
- `GET /api/topics`
- `POST /api/rag/ask`

## Examples

### Example 1: 로그인 및 토큰 발급

```bash
# 요청
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=admin123"

# 응답
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOjEsImV4cCI6MTY5NjI0ODAwMH0.xyz",
  "token_type": "bearer"
}
```

### Example 2: 보호된 엔드포인트 호출

```bash
# 인증 없이 시도 (401)
curl -X POST http://localhost:8000/api/contexts \
  -H "Content-Type: application/json" \
  -d '{"name": "Test", "description": "Test", "context_type": "PDF"}'

# 응답: 401 Unauthorized
{
  "detail": "Not authenticated"
}

# 관리자 토큰으로 시도 (201)
curl -X POST http://localhost:8000/api/contexts \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -d '{"name": "Test", "description": "Test", "context_type": "PDF"}'

# 응답: 201 Created
{
  "id": 1,
  "name": "Test",
  "description": "Test",
  "context_type": "PDF",
  "created_at": "2025-10-10T08:00:00Z"
}
```

### Example 3: 일반 사용자 권한 거부

```bash
# 일반 사용자 로그인 (is_staff=False)
curl -X POST http://localhost:8000/api/auth/login \
  -d "username=normaluser&password=password123"

# 응답
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.abc",
  "token_type": "bearer"
}

# 보호된 엔드포인트 시도 (403)
curl -X POST http://localhost:8000/api/contexts \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.abc" \
  -d '{"name": "Test", ...}'

# 응답: 403 Forbidden
{
  "detail": "Admin privileges required"
}
```

## Acceptance Criteria

### AC1: Django 비밀번호 호환

- [x] `verify_password()`가 Django `pbkdf2_sha256` 해시를 검증
- [x] 기존 Django User의 비밀번호로 로그인 성공

### AC2: JWT 토큰 생성/검증

- [x] `create_access_token()`이 유효한 JWT 생성 (HS256)
- [x] `decode_access_token()`이 토큰 페이로드 반환
- [x] 만료된 토큰은 검증 실패 (`None` 반환)

### AC3: 인증 의존성

- [x] `get_current_user()`가 유효한 토큰으로 User 객체 반환
- [x] 잘못된 토큰은 401 에러
- [x] `require_admin()`이 is_staff=False 사용자 거부 (403)

### AC4: 인증 엔드포인트

- [x] `POST /api/auth/login` 성공 시 토큰 발급
- [x] 잘못된 인증 정보는 401
- [x] `is_active=False` 사용자는 403
- [x] `GET /api/auth/me` 토큰으로 사용자 정보 조회

### AC5: 보호된 엔드포인트

- [x] Write 엔드포인트는 관리자 토큰 필수
- [x] 토큰 없이 요청 시 401
- [x] is_staff=False 사용자는 403
- [x] Read 엔드포인트는 인증 불필요 (public)

### AC6: 테스트 커버리지

- [x] 12개 인증 테스트 통과 (auth utils, endpoints, dependencies)
- [x] per-worker SQLite 분리로 병렬 테스트 안정성 확보

## Dependencies

| Name | Latest | Chosen | Rationale | Link |
|------|--------|--------|-----------|------|
| python-jose | 3.3.0 | 3.3.0 | JWT 생성/검증, cryptography 백엔드 지원 | https://github.com/mpdavis/python-jose |
| passlib | 1.7.4 | 1.7.4 | Django 비밀번호 해시 호환 (django_pbkdf2_sha256) | https://passlib.readthedocs.io/ |
| python-multipart | 0.0.20 | 0.0.20 | OAuth2PasswordRequestForm 지원 (이미 설치됨) | https://github.com/andrew-d/python-multipart |

## Versioning & Migration

### Version: 1.0.0 (Initial Implementation)

**릴리스**: Phase 5 (2025-09-30)

**변경사항**:
- JWT 기반 인증 시스템 도입
- Django User 테이블 SQLAlchemy 읽기 전용 모델
- Write 엔드포인트 관리자 보호

**마이그레이션**:
- **DB 마이그레이션**: 불필요 (기존 `auth_user` 테이블 재사용)
- **사용자 마이그레이션**: 불필요 (기존 비밀번호 호환)
- **클라이언트 변경**: Refine Admin에서 `/api/auth/login` 호출 후 토큰 저장 필요 (Phase 6)

### Future: Version 2.0.0 (Token Refresh)

**계획**:
- Refresh token 도입 (access token TTL 단축: 24h → 15min)
- Token blacklist (로그아웃 처리)
- HttpOnly Cookie 저장 (XSS 방지)

**하위 호환성**: 기존 access token은 만료 전까지 유효

## Security Considerations

### 1. JWT Secret Key

**리스크**: Secret key 노출 시 토큰 위조 가능

**완화**:
- 환경 변수에서 로드 (`JWT_SECRET_KEY`)
- 프로덕션에서 강력한 키 사용 (최소 256비트)
- `.env` 파일 Git 제외

### 2. Token Storage (Client)

**리스크**: LocalStorage는 XSS 공격에 취약

**완화** (Phase 6):
- HttpOnly Cookie 사용 (브라우저가 자동 전송)
- SameSite=Strict/Lax 설정 (CSRF 방지)

### 3. Password Hashing

**리스크**: Django `pbkdf2_sha256` 해시 역호환성 손실

**완화**:
- passlib `django_pbkdf2_sha256` scheme 테스트 검증
- Django User 생성 테스트로 실제 해시 포맷 확인

### 4. Token Expiration

**리스크**: 24시간 TTL로 탈취 시 장기간 유효

**완화**:
- 초기 구현 단순화 (refresh token 없음)
- 향후 TTL 단축 + refresh token 도입

## References

- **PLAN**: `.tasks/fastapi-auth/PLAN.md` (구현 계획)
- **RESEARCH**: `.tasks/fastapi-auth/RESEARCH.md` (조사 결과)
- **Tests**: `backend/tests/test_auth_*.py` (12개 테스트)
- **Django Password Hashing**: https://docs.djangoproject.com/en/5.1/topics/auth/passwords/
- **FastAPI Security**: https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/
