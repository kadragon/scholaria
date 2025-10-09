# Plan: RAG Endpoint Tests Reactivation

## Objective
`backend/tests/test_rag_endpoint.py`에 POST /rag/ask 엔드포인트 테스트를 작성하여 테스트 커버리지를 복원한다.

## Constraints
- AsyncRAGService를 mock하여 외부 의존성(OpenAI, Qdrant, Redis) 차단
- 기존 conftest.py 픽스처 패턴 활용
- TDD: 엔드포인트 로직만 테스트 (서비스 로직은 별도)

## Target Files & Changes

### 1. Rewrite test_rag_endpoint.py
**File**: `backend/tests/test_rag_endpoint.py`
- **Remove**: pytest.mark.skip 제거
- **Add**: 다음 테스트 케이스 작성
  1. `test_ask_question_success` - 정상 요청/응답
  2. `test_ask_question_empty_question_fails` - 빈 질문 검증
  3. `test_ask_question_invalid_topic_id_fails` - 잘못된 topic_id 검증
  4. `test_ask_question_service_value_error` - ValueError 처리 (400)
  5. `test_ask_question_service_connection_error` - ConnectionError 처리 (503)
  6. `test_ask_question_service_generic_error` - Exception 처리 (500)

## Test/Validation Cases
- 각 테스트 케이스 개별 통과
- 전체 테스트 스위트 통과 (86 → 92 expected)
- ruff, mypy 검증

## Steps
1. [ ] 테스트 픽스처 설계 (mock AsyncRAGService)
2. [ ] test_ask_question_success 작성 (Red → Green)
3. [ ] 검증 실패 케이스 2개 작성
4. [ ] 예외 처리 케이스 3개 작성
5. [ ] 전체 테스트 실행 및 검증

## Rollback
- Git stash/revert
- 원본 스킵 마크 복원

## Review Hotspots
- Mock 설정의 정확성 (AsyncRAGService.query 반환값)
- Pydantic 검증 vs 엔드포인트 검증 경계

## Status
- [ ] Step 1: 픽스처 설계
- [ ] Step 2: 정상 케이스 작성
- [ ] Step 3: 검증 실패 케이스
- [ ] Step 4: 예외 처리 케이스
- [ ] Step 5: 전체 검증
