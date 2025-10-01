# Research: RAG Endpoint Tests Reactivation

## Goal
현재 스킵되어 있는 `backend/tests/test_rag_endpoint.py`를 SQLAlchemy 기반으로 재작성하여 RAG 엔드포인트의 테스트 커버리지를 복원한다.

## Scope
- `backend/tests/test_rag_endpoint.py` 재작성
- Django ORM 의존성을 SQLAlchemy로 전환
- 기존 테스트 픽스처 패턴 활용 (`conftest.py`)

## Related Files
- `backend/tests/test_rag_endpoint.py` - 현재 스킵됨
- `backend/tests/conftest.py` - 공통 픽스처
- `backend/routers/rag.py` - RAG 엔드포인트
- `backend/services/rag_service.py` - RAG 서비스 로직

## Hypotheses
1. 기존 테스트가 Django ORM fixture를 사용했을 가능성
2. conftest.py의 SQLAlchemy 픽스처 패턴으로 대체 가능
3. Mock/patch가 필요한 외부 의존성: OpenAI, Qdrant, Redis

## Evidence

### Current State
- `test_rag_endpoint.py`: 전체 스킵, 내용 없음
- `routers/rag.py`: POST /rag/ask 엔드포인트 1개
  - QuestionRequest (topic_id, question) 수신
  - AsyncRAGService에 위임
  - AnswerResponse (answer, citations, topic_id) 반환
  - 예외 처리: ValueError (400), ConnectionError (503), Exception (500)

### Dependencies to Mock
1. **Redis**: `get_redis` 의존성 (캐싱)
2. **OpenAI API**: AsyncRAGService 내부에서 사용
3. **Qdrant**: AsyncRAGService 내부에서 사용
4. **EmbeddingService, RerankingService**: AsyncRAGService 내부

### Test Strategy
- AsyncRAGService를 mock하여 외부 의존성 차단
- 엔드포인트 로직만 테스트 (입력 검증, 응답 형식, 오류 처리)
- 단위 테스트 수준 (통합 테스트는 별도)

## Assumptions
- RAG 엔드포인트 자체는 정상 동작 중 (수동 테스트 또는 프로덕션 검증됨)
- 테스트 작성 패턴은 다른 엔드포인트 테스트와 유사

## Open Questions
- 기존 test_rag_endpoint.py에 어떤 테스트 케이스가 있었는지?
- Mock이 필요한 의존성은 무엇인지?

## Risks
- Low: 기존 동작하는 코드의 테스트 추가이므로 리스크 낮음

## Next
Plan 단계로 진행
