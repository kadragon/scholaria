# Task Summary: Performance Benchmark

## Goal
RAG 파이프라인 성능 지표 측정 인프라 구축 (Mock 기반 응답 지연 & 동시성 테스트)

## Key Changes
- **3개 성능 테스트 추가** (`@pytest.mark.performance`)
  - `test_rag_query_response_time_under_3s`: E2E 지연 < 3초 검증
  - `test_rag_pipeline_step_timings`: 파이프라인 단계별 타이밍 측정
  - `test_concurrent_requests_stability`: 10 동시 요청 안정성
- **Golden Dataset 인프라** (`@pytest.mark.golden`)
  - `backend/tests/fixtures/golden_dataset.json` (5개 질문-컨텍스트 쌍)
  - `golden_dataset` pytest 픽스처 추가
  - `test_golden_accuracy.py` 스켈레톤 (통합 테스트는 보류)
- **Mock 전략**: OpenAI API 의존성 차단, 환경변수 주입

## Tests
- **Added:** 4 passed, 2 skipped (총 6개 신규 테스트)
- **Existing:** 기존 테스트 슈트 유지 (1개 preexisting failure 확인)

## Commits
- 대기: feat/performance-benchmark 브랜치에서 커밋 예정

## Notes
- Golden Dataset 정확도 측정은 Qdrant 통합 테스트 필요 (Step 5-6 별도 구현)
- 현재 구현은 Mock 기반으로 외부 의존성 없이 CI 실행 가능
