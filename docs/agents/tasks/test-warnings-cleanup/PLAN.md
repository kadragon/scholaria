# 테스트 경고 개선 계획

## 목표
테스트 실행 시 발생하는 69개 경고를 0개로 줄여 테스트 출력을 깔끔하게 만들고, 향후 실제 문제를 놓치지 않도록 개선

## 현재 상태
- **총 경고**: 69개
- **테스트**: 122개 모두 통과
- **pytest.ini**: `--disable-warnings` 옵션으로 경고 숨김

## 경고 유형 분석

### 1. SQLAlchemy datetime.utcnow() Deprecation (59개)
**위치**: `sqlalchemy/sql/schema.py:3624`
**영향**: 15개 admin contexts, 13개 admin topics, 10개 bulk ops, 5개 auth, 16개 contexts write
**원인**: SQLAlchemy 모델의 `server_default=func.now()`가 내부적으로 deprecated `datetime.utcnow()` 사용
**해결**:
- `backend/models/` 의 모든 모델에서 `server_default=func.now()` → timezone-aware 대안 사용
- 또는 SQLAlchemy 버전 업그레이드 후 설정 조정

### 2. FastAPI HTTP Status 상수 Deprecation (4개)
**위치**: 테스트 코드
**종류**:
- `HTTP_422_UNPROCESSABLE_ENTITY` → `HTTP_422_UNPROCESSABLE_CONTENT` (3개)
- `HTTP_413_REQUEST_ENTITY_TOO_LARGE` → `HTTP_413_CONTENT_TOO_LARGE` (1개)
**영향**: `test_contexts_write.py`, `test_rag_endpoint.py`
**해결**: 테스트 코드에서 status code 검증 시 새 상수 사용

### 3. Redis async close() Deprecation (6개)
**위치**: `backend/dependencies/redis.py:29`
**원인**: `client.close()` → `client.aclose()` 권장
**영향**: RAG 엔드포인트 테스트 6개
**해결**: `get_redis()` 함수에서 `await client.close()` → `await client.aclose()`

## 단계별 실행 계획

### Step 1: Redis aclose() 마이그레이션 ✅
- [ ] `backend/dependencies/redis.py` 수정
  - `await client.close()` → `await client.aclose()`
- [ ] 테스트 실행하여 RAG 엔드포인트 경고 6개 제거 확인

### Step 2: FastAPI HTTP 상수 업데이트 ✅
- [ ] `test_contexts_write.py::test_create_context_invalid_type_fails` - HTTP_422 검증
- [ ] `test_contexts_write.py::test_upload_file_too_large_fails` - HTTP_413 검증
- [ ] `test_rag_endpoint.py::test_ask_question_empty_question_fails` - HTTP_422 검증
- [ ] `test_rag_endpoint.py::test_ask_question_invalid_topic_id_fails` - HTTP_422 검증
- [ ] 테스트 실행하여 4개 경고 제거 확인

### Step 3: SQLAlchemy datetime 경고 조사 및 해결 ✅
- [ ] 모든 모델 파일 검토 (`backend/models/*.py`)
- [ ] `created_at`, `updated_at` 필드의 `server_default` 설정 확인
- [ ] 옵션 1: `server_default=text("(CURRENT_TIMESTAMP)")`로 DB 네이티브 함수 사용
- [ ] 옵션 2: SQLAlchemy 2.0+ 권장 패턴 적용
- [ ] 옵션 3: `default=lambda: datetime.now(timezone.utc)` + `onupdate` (ORM 레벨)
- [ ] 마이그레이션 생성 (필요 시)
- [ ] 테스트 실행하여 59개 경고 제거 확인

### Step 4: pytest.ini 설정 정리 ✅
- [ ] `--disable-warnings` 제거
- [ ] 필요시 특정 경고만 필터링하는 설정 추가
- [ ] 전체 테스트 실행하여 경고 0개 확인

### Step 5: 문서화 및 검증 ✅
- [ ] PROGRESS.md 작성
- [ ] AGENTS.md 업데이트 (테스트 품질 섹션)
- [ ] CI/CD 파이프라인 확인 (경고를 에러로 취급하는 옵션 검토)

## 롤백 계획
- 각 단계별로 개별 커밋
- 문제 발생 시 해당 커밋만 revert
- pytest.ini 변경은 마지막 단계로 분리하여 안전성 확보

## 리스크
1. **SQLAlchemy 변경**: 타임스탬프 동작 변경 가능 → 기존 테스트로 검증
2. **HTTP 상수 변경**: FastAPI 버전 호환성 → import 확인
3. **Redis aclose()**: redis-py 버전 확인 필요 → requirements 검토

## 성공 기준
- ✅ 테스트 122개 모두 통과
- ✅ 경고 0개
- ✅ 기능 동작 변화 없음
- ✅ CI/CD 통과

## 예상 소요 시간
- Step 1: 10분
- Step 2: 15분
- Step 3: 30-45분 (조사 포함)
- Step 4: 5분
- Step 5: 10분
- **총합**: 약 1-1.5시간
