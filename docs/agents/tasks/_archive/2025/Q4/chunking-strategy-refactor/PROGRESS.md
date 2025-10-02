# Progress: 타입별 청킹 전략 리팩터링

## Summary
파싱과 청킹 로직을 전략 패턴으로 통합하여 타입별 인제스션 전략 객체 생성

## Goal & Approach
- 전략 패턴을 사용하여 파서와 청커를 하나의 응집도 있는 객체로 통합
- 팩토리 함수로 타입별 전략 인스턴스 관리
- TDD 방식: 각 전략별 테스트 작성 → 구현 → 통합

## Completed Steps
1. **Step 1: 기본 전략 인터페이스 정의** ✅
   - `backend/ingestion/strategies.py` 생성
   - `BaseIngestionStrategy` 추상 클래스: `parse()`, `chunk()` 메서드
   - 테스트: `test_base_strategy_requires_implementation` 통과

2. **Step 2: PDF 전략 구현** ✅
   - `PDFIngestionStrategy` 클래스 작성 (PDFParser + PDFChunker 통합)
   - chunk_size=1000, overlap=150 파라미터
   - 테스트: `test_pdf_strategy_chunk_only` 통과

3. **Step 3: Markdown 전략 구현** ✅
   - `MarkdownIngestionStrategy` 클래스 작성 (MarkdownParser + MarkdownChunker 통합)
   - chunk_size=1200, overlap=200 파라미터
   - 테스트: `test_markdown_strategy_parse_and_chunk` 통과

4. **Step 4: FAQ 전략 구현** ✅
   - `FAQIngestionStrategy` 클래스 작성 (FAQParser + FAQChunker 통합)
   - chunk_size=800, overlap=100 파라미터
   - 테스트: `test_faq_strategy_parse_and_chunk` 통과

5. **Step 5: 팩토리 함수 구현** ✅
   - `get_ingestion_strategy(context_type)` 함수 작성
   - 딕셔너리 매핑으로 타입별 전략 반환
   - 테스트: 4개 테스트 통과 (PDF, Markdown, FAQ, 미지원 타입)

6. **Step 6: 서비스 레이어 리팩터링** ✅
   - `_get_chunker()`, `_get_parser()` 함수 제거
   - `ingest_document()` 내부에서 `get_ingestion_strategy()` 사용
   - 파싱/청킹을 전략 객체로 위임
   - 기존 6개 테스트 모두 통과

7. **Step 7: 회귀 테스트 및 정리** ✅
   - 전체 테스트 스위트: 108 passed (기존 100개 + 신규 8개)
   - mypy: 이슈 없음
   - ruff: 이슈 없음

## Current Failures
(none)

## Decision Log
- ABC를 사용하여 추상 메서드 강제 구현
- `parse()`, `chunk()` 메서드만 정의 (단순화)
- PDF 파싱 테스트는 실제 PDF 파일 필요 → 청킹 로직만 단위 테스트
- Markdown은 간단한 텍스트 파일로 파싱+청킹 통합 테스트 가능
- 모든 전략 클래스에서 파서/청커를 `__init__`에서 인스턴스화하여 재사용
- 팩토리 함수는 매번 새 인스턴스 생성 (간단한 구현)
- 서비스 레이어는 전략 객체만 알고 파서/청커는 몰라도 됨 (캡슐화)

## Files Modified
- **NEW** `backend/ingestion/strategies.py` (123 lines)
- **MODIFIED** `backend/services/ingestion.py` (-30 lines)
- **NEW** `backend/tests/test_ingestion_strategies.py` (8 tests)

## Next Step
(Task Complete)
