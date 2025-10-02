# Progress: RAG Endpoint Tests Reactivation

## Summary
스킵된 RAG 엔드포인트 테스트를 재활성화하여 테스트 커버리지 복원 완료

## Goal & Approach
**Goal**: POST /rag/ask 엔드포인트 테스트 작성
**Approach**: AsyncRAGService를 mock하여 엔드포인트 로직만 단위 테스트

## Completed Steps
- [x] Research: 엔드포인트 구조 및 의존성 파악
- [x] Plan: 6개 테스트 케이스 설계
- [x] Step 1-5: 모든 테스트 케이스 작성 및 통과
  - test_ask_question_success (정상 요청/응답)
  - test_ask_question_empty_question_fails (빈 질문 검증)
  - test_ask_question_invalid_topic_id_fails (잘못된 topic_id)
  - test_ask_question_service_value_error (ValueError → 400)
  - test_ask_question_service_connection_error (ConnectionError → 503)
  - test_ask_question_service_generic_error (Exception → 500)
- [x] Code quality: ruff/mypy 통과
- [x] Full test suite: 92/92 통과 (86 → 92, +6)

## Current Failures
없음 (모든 테스트 통과)

## Decision Log
1. **Mock 전략**: AsyncRAGService 전체를 mock (외부 의존성 차단)
2. **테스트 범위**: 엔드포인트 로직만 (서비스 로직은 제외)
3. **환경변수**: 모든 테스트에 OPENAI_API_KEY 설정 (503 회피)

## Files Changed
- backend/tests/test_rag_endpoint.py: 스킵 제거, 6개 테스트 추가

## Next Step
완료 - RAG 엔드포인트 테스트 커버리지 복원 성공
