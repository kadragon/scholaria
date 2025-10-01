# Task Summary: 타입별 청킹 전략 리팩터링

## Goal
파싱과 청킹 로직을 전략 패턴으로 리팩터링하여 타입별 인제스션 로직 응집도 향상

## Key Changes
1. **NEW** `backend/ingestion/strategies.py` (123 lines)
   - `BaseIngestionStrategy` 추상 베이스 클래스
   - `PDFIngestionStrategy`, `MarkdownIngestionStrategy`, `FAQIngestionStrategy` 구현
   - `get_ingestion_strategy(context_type)` 팩토리 함수

2. **MODIFIED** `backend/services/ingestion.py` (-30 lines)
   - `_get_parser()`, `_get_chunker()` 제거
   - `ingest_document()` 내부에서 전략 객체 사용

3. **NEW** `backend/tests/test_ingestion_strategies.py` (8 tests)
   - 타입별 전략 단위 테스트
   - 팩토리 함수 테스트

## Tests
- **신규**: 8개 테스트 (`test_ingestion_strategies.py`)
- **회귀**: 기존 6개 테스트 통과 (`test_ingestion_service.py`)
- **전체**: 108 passed (100 → 108)

## Commit
- SHA: `f5e6f0b`
- Type: [Structural]
- Message: 타입별 인제스션 전략 패턴 도입

## Benefits
- 파서와 청커를 하나의 응집도 있는 객체로 통합
- 새 타입 추가 시 1곳만 수정 (strategies.py)
- 서비스 레이어는 전략 인터페이스만 의존 (캡슐화)
