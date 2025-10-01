# FastAPI 인증 구현 진행 상황

## Summary
Django 세션 기반 → FastAPI JWT 인증 전환 완료 (Step 1-7)

## Goal & Approach
- Django `auth_user` 테이블 재사용 (SQLAlchemy 읽기 전용)
- Custom JWT 구현 (python-jose + passlib)
- Django 비밀번호 호환 (passlib `django_pbkdf2_sha256`)
- TDD: 11개 테스트 작성 및 통과

## Completed Steps
- ✅ **Step 1: 의존성 추가**
  - `python-jose[cryptography]>=3.3.0`, `passlib[bcrypt]>=1.7.4` 추가
  - `uv sync` 실행, passlib Django support 검증
- ✅ **Step 2: User SQLAlchemy 모델**
  - `api/models/user.py` 생성 (Django `auth_user` 테이블 매핑)
  - Read-only 모델 (FastAPI는 사용자 생성/수정 안 함)
- ✅ **Step 3: 인증 유틸리티**
  - `api/auth/utils.py` 생성
  - `verify_password`: Django 비밀번호 검증 (passlib `django_pbkdf2_sha256`)
  - `create_access_token`: JWT 생성 (24시간 TTL)
  - `decode_access_token`: JWT 검증
  - **핵심**: JWT `sub` claim은 문자열이어야 함 (`str(user.id)`)
- ✅ **Step 4: 인증 의존성**
  - `api/dependencies/auth.py` 생성
  - `get_current_user`: JWT → User 추출
  - `require_admin`: is_staff 검증
- ✅ **Step 5: 인증 라우터**
  - `api/routers/auth.py` 생성
  - `POST /api/auth/login`: 로그인 (JWT 발급)
  - `GET /api/auth/me`: 현재 사용자 정보
  - `api/main.py`에 라우터 등록
  - **핵심**: Django setup 필요 (`django.setup()` in main.py)
- ✅ **Step 6: 테스트 작성**
  - `api/tests/test_auth.py` 생성 (11개 테스트)
  - Utils 테스트 (3개): 비밀번호 검증, JWT 생성/디코드
  - Endpoint 테스트 (6개): 로그인 성공/실패, /me 엔드포인트
  - Dependency 테스트 (2개): admin 권한 검증
  - **핵심**: `@pytest.mark.django_db(transaction=True)` 필수 (Django ORM ↔ SQLAlchemy 세션 공유)

- ✅ **Step 7: 기존 Write 라우터 보호**
  - `api/routers/contexts.py`: POST/PUT/PATCH/DELETE 및 FAQ 추가 엔드포인트에 `Depends(require_admin)` 적용
  - `api/tests/test_contexts_write.py`: 관리자 토큰 fixture 추가, 무단 요청 401 테스트 및 per-worker SQLite DB 분리
  - 테스트: `uv run pytest api/tests/test_contexts_write.py` (20개)

## Current Failures
없음 (11/11 테스트 통과)

## Decision Log
| 날짜 | 결정 | 근거 |
|------|------|------|
| 2025-09-30 | Custom JWT vs. fastapi-users | fastapi-users는 과함 (user registration 불필요), Custom JWT가 가볍고 단순 |
| 2025-09-30 | JWT `sub` claim을 문자열로 | JWT spec: `sub`는 StringOrURI 타입, int는 불가 |
| 2025-09-30 | passlib `django_pbkdf2_sha256` scheme | Django 비밀번호 호환 검증 성공 |
| 2025-09-30 | `@pytest.mark.django_db(transaction=True)` | Django ORM과 SQLAlchemy 세션 분리 문제 해결 |
| 2025-09-30 | FastAPI write 라우터 JWT 보호 | `require_admin` 의존성 + per-worker SQLite 테스트 DB로 JWT 검증 신뢰성 확보 |

## Completed Steps (cont'd)
- ✅ **Step 8: 환경 변수 및 설정 정리**
  - `api/config.py`에 `JWT_SECRET_KEY`, `JWT_ALGORITHM`, `JWT_ACCESS_TOKEN_EXPIRE_HOURS` 추가
  - `api/auth/utils.py`가 `api/config.settings` 사용하도록 변경
  - `.env.example` 및 `.env.prod.example`에 JWT 설정 섹션 추가
  - `docs/ENVIRONMENT.md`에 JWT 설정 문서화 (생성 명령 포함)
  - 테스트: 12/12 통과 (환경변수 재로드 검증 포함)

## Decision Log (Step 8)
| 날짜 | 결정 | 근거 |
|------|------|------|
| 2025-10-01 | `api/config.py`에 JWT 설정 추가 | 환경변수 중앙 관리, 테스트 환경 reload 가능 |
| 2025-10-01 | `api/auth/utils.py`가 `api/config.settings` 사용 | 하드코딩 제거, 테스트 환경 주입 가능 |
| 2025-10-01 | `api/tests/conftest.py` 생성 | 모든 FastAPI 테스트가 공통 SQLite DB 사용, xdist worker 분리 |

## Next Step
**Phase 5-8 완료** → Phase 6: Refine Admin Panel로 이동
- FastAPI 인증 시스템 구현 완료 (JWT 환경변수 노출 포함)
- 다음 단계: Refine Admin Panel 구현 (TASKS.md 업데이트 필요)
