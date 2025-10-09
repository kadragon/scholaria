# FastAPI 인증 구현 계획

## Objective
Django 세션 기반 인증에서 FastAPI JWT 기반 인증으로 전환하되, 기존 Django User 테이블을 재사용하여 최소 변경으로 구현

## Constraints
- Django `auth_user` 테이블 공유 (SQLAlchemy 읽기 전용)
- Django 비밀번호 해시 포맷 호환 필수 (`pbkdf2_sha256$...`)
- Phase 5 기간 동안 Django Admin(세션) + FastAPI(JWT) 병렬 운영
- TDD: 각 단계 테스트 우선 작성

## Target Files & Changes

### 1. 의존성 추가 (`pyproject.toml`)
```toml
dependencies = [
    # ... 기존 의존성
    "python-jose[cryptography]>=3.3.0",  # JWT 생성/검증
    "passlib[bcrypt]>=1.7.4",            # 비밀번호 해싱/검증
    "python-multipart>=0.0.20",          # 이미 있음 (form data)
]
```

### 2. User SQLAlchemy 모델 (`api/models/user.py` 생성)
```python
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from api.models.base import Base

class User(Base):
    __tablename__ = "auth_user"  # Django auth_user 테이블

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(150), unique=True, nullable=False)
    email = Column(String(254))
    password = Column(String(128), nullable=False)  # Django hashed password
    is_active = Column(Boolean, default=True)
    is_staff = Column(Boolean, default=False)
    is_superuser = Column(Boolean, default=False)
    first_name = Column(String(150))
    last_name = Column(String(150))
    date_joined = Column(DateTime, nullable=False)
    last_login = Column(DateTime)
```
- **주의**: Read-only 모델 (FastAPI는 사용자 생성/수정 안 함)

### 3. 인증 유틸리티 (`api/auth/utils.py` 생성)
```python
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional

# Django 비밀번호 호환 설정
pwd_context = CryptContext(
    schemes=["django_pbkdf2_sha256", "bcrypt"],  # Django 우선
    deprecated="auto"
)

SECRET_KEY = "your-secret-key"  # settings에서 로드
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = 24

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Django 해시 포맷 호환 비밀번호 검증"""
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """JWT 액세스 토큰 생성"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def decode_access_token(token: str) -> Optional[dict]:
    """JWT 토큰 디코드 및 검증"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None
```

### 4. 인증 의존성 (`api/dependencies/auth.py` 생성)
```python
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from api.models.user import User
from api.auth.utils import decode_access_token
from api.dependencies.database import get_db

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """JWT 토큰에서 현재 사용자 추출"""
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

async def require_admin(current_user: User = Depends(get_current_user)) -> User:
    """관리자 권한 검증"""
    if not current_user.is_staff:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )
    return current_user
```

### 5. 인증 라우터 (`api/routers/auth.py` 생성)
```python
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from api.models.user import User
from api.auth.utils import verify_password, create_access_token
from api.dependencies.database import get_db
from api.dependencies.auth import get_current_user
from pydantic import BaseModel

router = APIRouter(prefix="/auth", tags=["Authentication"])

class Token(BaseModel):
    access_token: str
    token_type: str

class UserOut(BaseModel):
    id: int
    username: str
    email: str
    is_staff: bool
    is_superuser: bool

    class Config:
        from_attributes = True

@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """사용자 로그인 (JWT 토큰 발급)"""
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )

    access_token = create_access_token(data={"sub": user.id})
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=UserOut)
async def get_me(current_user: User = Depends(get_current_user)):
    """현재 로그인한 사용자 정보 조회"""
    return current_user
```

### 6. 라우터 등록 (`api/main.py` 수정)
```python
from api.routers import auth  # 추가

app.include_router(auth.router, prefix="/api")
```

### 7. 기존 라우터에 인증 적용 (`api/routers/contexts.py` 수정)
```python
from api.dependencies.auth import require_admin  # 추가

# Write 엔드포인트에 적용
@router.post("/", response_model=ContextOut)
async def create_context(
    context_data: ContextCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)  # 추가
):
    # ...
```
- **적용 대상**: POST/PUT/DELETE 엔드포인트만 (Read는 public 유지)

### 8. Database 의존성 (`api/dependencies/database.py` 생성 또는 수정)
```python
from sqlalchemy.orm import Session
from api.config import get_db_session

def get_db() -> Session:
    db = get_db_session()
    try:
        yield db
    finally:
        db.close()
```
- 기존 `api/config.py`에 `get_db_session` 함수가 있는지 확인

### 9. 환경 변수 설정 (`.env` 수정)
```env
# JWT 설정
JWT_SECRET_KEY=your-very-secret-key-change-in-production
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_HOURS=24
```

## Test/Validation Cases

### Step 1: 비밀번호 검증 테스트 (`api/tests/test_auth_utils.py`)
```python
import pytest
from api.auth.utils import verify_password

def test_verify_django_password():
    """Django pbkdf2_sha256 해시 검증"""
    # Django User.objects.create_user('test', password='password123')의 해시
    django_hash = "pbkdf2_sha256$600000$..."  # 실제 Django 해시
    assert verify_password("password123", django_hash) is True
    assert verify_password("wrongpassword", django_hash) is False
```

### Step 2: JWT 토큰 생성/검증 테스트 (`api/tests/test_auth_utils.py`)
```python
from api.auth.utils import create_access_token, decode_access_token

def test_create_and_decode_token():
    """JWT 토큰 생성 및 디코드"""
    token = create_access_token(data={"sub": 123})
    payload = decode_access_token(token)
    assert payload is not None
    assert payload["sub"] == 123
```

### Step 3: 로그인 엔드포인트 테스트 (`api/tests/test_auth_endpoints.py`)
```python
import pytest
from fastapi.testclient import TestClient
from api.main import app
from django.contrib.auth.models import User

client = TestClient(app)

@pytest.mark.django_db
def test_login_success():
    """정상 로그인 시 JWT 토큰 발급"""
    # Django User 생성
    user = User.objects.create_user(username='testuser', password='password123')

    response = client.post("/api/auth/login", data={
        "username": "testuser",
        "password": "password123"
    })

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

@pytest.mark.django_db
def test_login_invalid_credentials():
    """잘못된 인증 정보로 로그인 실패"""
    response = client.post("/api/auth/login", data={
        "username": "nonexistent",
        "password": "wrongpassword"
    })

    assert response.status_code == 401
```

### Step 4: 인증 의존성 테스트 (`api/tests/test_auth_dependencies.py`)
```python
@pytest.mark.django_db
def test_get_current_user():
    """JWT 토큰으로 현재 사용자 조회"""
    user = User.objects.create_user(username='testuser', password='password123')
    token_response = client.post("/api/auth/login", data={
        "username": "testuser",
        "password": "password123"
    })
    token = token_response.json()["access_token"]

    response = client.get("/api/auth/me", headers={
        "Authorization": f"Bearer {token}"
    })

    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "testuser"

@pytest.mark.django_db
def test_require_admin_non_staff():
    """관리자 아닌 사용자는 admin 엔드포인트 접근 불가"""
    user = User.objects.create_user(username='normaluser', password='password123')
    token_response = client.post("/api/auth/login", data={
        "username": "normaluser",
        "password": "password123"
    })
    token = token_response.json()["access_token"]

    # POST /api/contexts (admin 필요)
    response = client.post("/api/contexts", headers={
        "Authorization": f"Bearer {token}"
    }, json={...})

    assert response.status_code == 403
```

### Step 5: 보호된 엔드포인트 테스트 (`api/tests/test_contexts_write.py` 수정)
```python
@pytest.mark.django_db
def test_create_context_requires_auth():
    """인증 없이 Context 생성 시도 시 401"""
    response = client.post("/api/contexts", json={...})
    assert response.status_code == 401

@pytest.mark.django_db
def test_create_context_with_admin():
    """관리자 인증으로 Context 생성 성공"""
    admin = User.objects.create_superuser(username='admin', password='admin123')
    token = client.post("/api/auth/login", data={
        "username": "admin",
        "password": "admin123"
    }).json()["access_token"]

    response = client.post("/api/contexts", headers={
        "Authorization": f"Bearer {token}"
    }, json={...})

    assert response.status_code == 201
```

## Steps

### 1. 의존성 추가 및 설치 (5분)
- [ ] `pyproject.toml` 수정 (python-jose, passlib 추가)
- [ ] `uv sync` 실행

### 2. User 모델 생성 (10분)
- [ ] `api/models/user.py` 생성
- [ ] `api/models/__init__.py`에 import 추가

### 3. 인증 유틸리티 구현 (20분)
- [ ] `api/auth/utils.py` 생성
- [ ] Django 비밀번호 검증 테스트 작성 및 통과

### 4. 인증 의존성 구현 (15분)
- [ ] `api/dependencies/auth.py` 생성
- [ ] `api/dependencies/database.py` 확인/생성

### 5. 인증 라우터 구현 (20분)
- [ ] `api/routers/auth.py` 생성
- [ ] `/auth/login`, `/auth/me` 엔드포인트
- [ ] `api/main.py`에 라우터 등록

### 6. 테스트 작성 및 검증 (30분)
- [ ] `api/tests/test_auth_utils.py` 작성
- [ ] `api/tests/test_auth_endpoints.py` 작성
- [ ] `api/tests/test_auth_dependencies.py` 작성
- [ ] 모든 테스트 통과 확인

### 7. 기존 라우터에 인증 적용 (20분)
- [x] `api/routers/contexts.py` Write 엔드포인트에 `require_admin` 적용
- [x] `api/routers/rag.py`는 public 유지 (인증 불필요)
- [x] 기존 테스트 수정 (admin 토큰 추가 + 무단 요청 401 케이스 및 per-worker SQLite 분리)

### 8. 환경 변수 및 설정 (10분)
- [ ] `.env.example` 업데이트
- [ ] `api/config.py`에 JWT 설정 추가

### 9. 통합 테스트 (15분)
- [ ] 전체 테스트 실행 (`uv run pytest`)
- [ ] Swagger UI에서 수동 테스트 (`/docs`)

## Rollback
- **Step 1-5**: FastAPI 인증 코드 제거, Django는 영향 없음
- **Step 7**: Write 엔드포인트에서 `Depends(require_admin)` 제거하면 복구

## Review Hotspots
- **Django 비밀번호 호환**: passlib의 `django_pbkdf2_sha256` scheme 검증 필수
- **JWT Secret Key**: 프로덕션에서 반드시 강력한 키 사용
- **Token Storage**: Refine Admin에서 LocalStorage vs. HttpOnly Cookie 결정 필요 (Phase 6에서 처리)

## Risks
- **High**: passlib가 Django 해시 미지원 → 테스트 우선 검증
- **Medium**: JWT 만료 후 UX (24시간 후 재로그인) → 초기 구현 단순화
- **Low**: 하이브리드 인증 복잡도 (세션 + JWT) → Phase 5는 FastAPI만 JWT

## Status
- [x] Step 1: 의존성 추가
- [x] Step 2: User 모델
- [x] Step 3: 인증 유틸리티
- [x] Step 4: 인증 의존성
- [x] Step 5: 인증 라우터
- [x] Step 6: 테스트 작성
- [x] Step 7: 기존 라우터 보호
- [x] Step 8: 환경 변수 (완료 — JWT 설정 노출 및 문서화)
- [x] Step 9: 기본 테스트 (12/12 auth 테스트 통과, conftest.py 공통 DB 설정)
