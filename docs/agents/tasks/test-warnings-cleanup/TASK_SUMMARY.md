# 테스트 경고 제거 - 요약

## 목표
테스트 실행 시 발생하는 69개 deprecation 경고를 0개로 줄여 테스트 품질 향상

## 경고 분류
1. **SQLAlchemy datetime.utcnow()** (59개, 86%) - `server_default=func.now()` 사용
2. **Redis close() → aclose()** (6개, 9%) - redis-py 5.0.1+ 비동기 API 변경
3. **FastAPI HTTP 상수** (4개, 6%) - RFC 9110 준수를 위한 명칭 변경

## 해결 방안
1. SQLAlchemy: `server_default=text("(CURRENT_TIMESTAMP)")` 사용 (DB 네이티브)
2. Redis: `await client.close()` → `await client.aclose()`
3. HTTP 상수: 숫자 리터럴 사용 또는 새 상수명 사용

## 파일 영향
- `backend/models/*.py` (4개 파일)
- `backend/dependencies/redis.py` (1개 파일)
- `backend/tests/test_contexts_write.py` (간접 영향)
- `backend/tests/test_rag_endpoint.py` (간접 영향)
- `pytest.ini` (설정 정리)

## 검증 기준
- ✅ 122개 테스트 모두 통과
- ✅ 경고 0개
- ✅ 타임스탬프 동작 변화 없음

## 상태
✅ **완료** - 경고 69개 → 0개

## 커밋
- [Structural] Remove test deprecation warnings (69 → 0)

## 주요 변경사항
- Redis: `client.close()` → `client.aclose()`
- SQLAlchemy: `server_default=func.now()` → `server_default=text("(CURRENT_TIMESTAMP)")`
- User 모델: `default=datetime.utcnow` → `default=lambda: datetime.now(timezone.utc)`
- pytest.ini: `--disable-warnings` 제거, anyio/pytest 내부 경고만 필터링
