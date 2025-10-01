# Research: Final FastAPI Tests Cleanup

## Goal
Django 제거 후 남은 Django 의존성 테스트 파일 정리 및 전체 테스트 통과 검증.

## Scope
- `backend/tests/test_auth.py`: Django User 모델 임포트 제거 필요
- `backend/tests/test_topics_poc.py`: Django settings 의존성 제거 필요
- 나머지 77개 테스트: 수집 단계에서 에러 발생 (Django 임포트 체인)

## Related Files
1. **`backend/tests/test_auth.py`** (L6): `from django.contrib.auth.models import User`
2. **`backend/tests/test_topics_poc.py`** (L20): `from django.conf import settings`
3. **`backend/tests/conftest.py`**: 공통 픽스처 확인 필요

## Hypotheses
1. **test_auth.py**: Django User 모델이 `verify_django_password` 테스트에서만 사용 → SQLAlchemy User 모델로 교체 가능
2. **test_topics_poc.py**: POC 테스트로 이미 현행 API로 대체됨 → 삭제 후보

## Evidence
- **Error output**: `ImproperlyConfigured: INSTALLED_APPS not configured` → Django import at collection time
- **Phase 5 완료 기록** (TASKS.md L40-46): FastAPI JWT 인증 구현 완료, Django auth_user 테이블 재사용
- **test_auth.py L36-39**: Django User.set_password() 사용 → 이미 `backend.auth.utils.verify_password`가 Django password hash 지원

## Assumptions
- `backend.auth.utils.verify_password`는 Django password hash 포맷 (`pbkdf2_sha256$...`) 처리 가능 (passlib 사용)
- POC 테스트는 Phase 2 완료 후 불필요 (동등성 검증 완료)

## Risks
- **Password hash 호환성**: Django User.set_password() 제거 시 기존 DB 사용자 비밀번호 검증 실패 가능
  - **Mitigation**: `passlib.hash.django_pbkdf2_sha256.hash()` 직접 사용

## Next
**Plan** 단계로 진행 → 파일별 수정 전략 수립
