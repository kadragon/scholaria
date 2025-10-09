# 테스트 경고 제거 - 진행 상황

## 목표
테스트 실행 시 발생하는 69개 경고를 0개로 줄이기

## 현재 접근 방식
단계별로 경고 유형을 처리하며, 각 단계 후 테스트 실행하여 검증

## 완료된 단계
1. ✅ **Redis aclose() 마이그레이션** - `backend/dependencies/redis.py` 수정, 6개 경고 제거
2. ✅ **SQLAlchemy datetime 수정** - 모든 모델에서 `server_default=text("(CURRENT_TIMESTAMP)")` 사용, 59개 경고 제거
3. ✅ **User 모델 datetime.utcnow() 수정** - `default=lambda: datetime.now(timezone.utc)` 사용
4. ✅ **pytest.ini 정리** - `--disable-warnings` 제거, anyio/pytest 내부 경고만 필터링
5. ✅ **전체 테스트 검증** - 122개 테스트 통과, 경고 0개

## 현재 실패/이슈
_없음_

## 결정 로그
- SQLAlchemy datetime 해결 방안으로 **옵션 A (DB 네이티브 함수)** 선택
  - 이유: PostgreSQL/SQLite 모두 CURRENT_TIMESTAMP 지원, 성능 우수, Python deprecation 회피
- FastAPI HTTP 상수 경고는 라이브러리 내부(anyio/_backends/_asyncio.py) 이슈로 필터링 처리
  - 우리 코드에서 직접 해결 불가능
  - pytest filterwarnings로 안전하게 억제

## 다음 단계
문서화 및 커밋
