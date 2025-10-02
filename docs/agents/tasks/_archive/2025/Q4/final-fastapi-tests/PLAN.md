# Plan: Final FastAPI Tests Cleanup

## Objective
Django 의존성 제거 후 모든 FastAPI 테스트 통과 (79개 → 77개 실행 목표).

## Constraints
- Django password hash 호환성 유지 (기존 DB 사용자 검증)
- 테스트 커버리지 유지 또는 향상

## Target Files & Changes

### 1. `backend/tests/test_auth.py`
- **Remove**: L6 `from django.contrib.auth.models import User`
- **Update**: L34-39 `test_verify_django_password` → passlib로 Django hash 직접 생성
  ```python
  from passlib.hash import django_pbkdf2_sha256

  def test_verify_django_password(self) -> None:
      hashed = django_pbkdf2_sha256.hash("testpass123")
      assert auth_utils.verify_password("testpass123", hashed)
      assert not auth_utils.verify_password("wrongpass", hashed)
  ```

### 2. `backend/tests/test_topics_poc.py`
- **Decision**: **DELETE** (POC 완료, 현행 테스트로 대체됨)
- **Rationale**: Phase 2에서 Django API 동등성 검증 완료, 더 이상 불필요

### 3. `backend/tests/conftest.py`
- **Verify**: Django 임포트 확인 후 제거 (있다면)

## Test/Validation
1. **Unit test**: `uv run pytest backend/tests/test_auth.py -v`
2. **Full suite**: `uv run pytest backend/tests/ -v`
3. **Coverage check**: 테스트 수 77개 이상 수집, 에러 0개

## Steps
- [x] Step 1: Research 완료
- [x] Step 2: Plan 완료
- [ ] Step 3: conftest.py 확인
- [ ] Step 4: test_auth.py 수정
- [ ] Step 5: test_topics_poc.py 삭제
- [ ] Step 6: 전체 테스트 실행 및 검증
- [ ] Step 7: TASKS.md 업데이트 (Phase 8 Step 6 완료 표시)

## Rollback
```bash
git checkout backend/tests/test_auth.py
git checkout backend/tests/test_topics_poc.py
```

## Review Hotspots
- **Password hash 생성**: Django 호환 포맷 보장
- **삭제된 POC 테스트**: 기능 커버리지 누락 확인

## Status
- [x] Step 1: Research
- [x] Step 2: Plan
- [ ] Step 3: conftest.py 확인
- [ ] Step 4: test_auth.py 수정
- [ ] Step 5: test_topics_poc.py 삭제
- [ ] Step 6: 전체 테스트 실행 및 검증
- [ ] Step 7: TASKS.md 업데이트
