# Performance Validation Research

## Goal
실제 환경에서의 RAG 시스템 성능 검증 및 최적화 기회 식별

## Scope
- 응답 시간 벤치마크 (단일 쿼리 < 3초 요구사항)
- 동시 사용자 부하 테스트
- 메모리 사용량 분석
- 인용 정확도 검증 (>80% 요구사항)

## Related Files/Flows
- `rag/tests/performance_benchmarks.py`: 종합적인 성능 테스트 프레임워크
- `rag/tests/test_performance_benchmarks.py`: 기존 성능 테스트
- `rag/retrieval/rag.py`: 핵심 RAG 서비스 구현
- `rag/management/commands/run_performance_benchmark.py`: CLI 벤치마크 도구

## Hypotheses
1. **현재 성능**: 기본적인 3초 응답 시간 요구사항은 충족할 것
2. **동시성**: 3-5명 동시 사용자는 성능 저하 없이 지원 가능
3. **병목지점**: 임베딩 검색과 LLM API 호출이 주요 지연 원인
4. **메모리**: 적절한 수준에서 안정적으로 유지

## Evidence
- 기존 134개 테스트 모두 통과
- `PerformanceBenchmark` 클래스가 포괄적인 측정 도구 제공
- 실제 RAG 파이프라인: Qdrant 벡터 검색 → 재순위 → OpenAI API 호출

## Current Implementation Analysis
- **3초 임계값**: `three_second_threshold = 3.0` 하드코딩
- **부하 테스트**: 기본 20 요청/10초 설정 (상당히 보수적)
- **동시성 테스트**: ThreadPoolExecutor로 3명 사용자 시뮬레이션
- **메모리 모니터링**: psutil로 RSS 메모리 추적

## Assumptions/Open Questions
- 실제 데이터 규모에서의 성능 특성
- 프로덕션 환경 vs 개발 환경 성능 차이
- OpenAI API 응답 시간 변동성 영향
- 인용 정확도 측정을 위한 golden dataset 필요성

## Risks
- **외부 의존성**: OpenAI API 지연이 성능에 직접 영향
- **데이터 규모**: 컨텍스트/청크 수 증가 시 성능 저하 가능
- **동시성 제한**: 스레드 기반 테스트의 한계

## Next
1. 기존 성능 테스트 실행 및 결과 분석
2. 실제 환경에서 벤치마크 수행
3. 성능 보고서 생성 및 개선 방안 제시
