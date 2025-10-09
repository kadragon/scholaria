# Plan: 타입별 청킹 전략 리팩터링

## Objective
파서와 청커를 하나의 전략 객체로 통합하여 타입별 인제스션 로직을 응집도 있게 관리

## Constraints
- 기존 청크 크기/오버랩 파라미터 변경 금지 (하위 호환성)
- `backend/routers/contexts.py:136` PDF 미리보기 로직 유지
- 100% 테스트 통과 유지 (특히 `test_ingestion_service.py`)
- 기존 API 시그니처 변경 최소화

## Target Files & Changes

### 1. **NEW** `backend/ingestion/strategies.py`
새 파일 생성 - 타입별 전략 클래스 정의
- `BaseIngestionStrategy` (추상 베이스)
- `PDFIngestionStrategy`
- `MarkdownIngestionStrategy`
- `FAQIngestionStrategy`
- `get_ingestion_strategy(context_type: str)` 팩토리 함수

### 2. **MODIFY** `backend/services/ingestion.py`
- `_get_chunker()`, `_get_parser()` 제거
- `ingest_document()` 내부에서 `get_ingestion_strategy()` 사용
- 파싱/청킹 로직을 전략 객체에 위임

### 3. **MODIFY** `backend/routers/contexts.py` (미리보기)
- `_process_pdf_upload:136-139` 유지 (파서 직접 임포트)
- 또는 전략에서 파서만 추출하는 헬퍼 추가 고려

### 4. **NEW** `backend/tests/test_ingestion_strategies.py`
타입별 전략 단위 테스트
- 각 전략의 파싱/청킹 동작 검증
- 엣지케이스: 빈 문서, 큰 문서, 비정상 포맷

## Test & Validation Cases

### TDD Cycle
1. `test_base_strategy_interface()` - 추상 메서드 정의 검증
2. `test_pdf_strategy_parse_and_chunk()` - PDF 전략 통합
3. `test_markdown_strategy_section_handling()` - Markdown 섹션 분할
4. `test_faq_strategy_qa_pairs()` - FAQ Q&A 쌍 유지
5. `test_strategy_factory()` - 팩토리 함수 타입 매핑
6. `test_existing_ingestion_service()` - 기존 테스트 회귀 방지

### Integration Tests
- `test_ingest_markdown_document()` (기존) - 변경 없이 통과 확인
- `test_ingest_document_context_not_found()` (기존) - 에러 핸들링 유지

## Steps

### Step 1: 기본 전략 인터페이스 정의
- [ ] `BaseIngestionStrategy` 추상 클래스 작성
  - `parse(file_path: str) -> str` 추상 메서드
  - `chunk(text: str) -> list[str]` 추상 메서드
- [ ] 테스트: 추상 메서드 미구현 시 에러 검증

### Step 2: PDF 전략 구현
- [ ] `PDFIngestionStrategy` 구현
  - 기존 `PDFParser` + `PDFChunker` 통합
  - 파라미터: chunk_size=1000, overlap=150
- [ ] 테스트: PDF 파싱 + 청킹 검증

### Step 3: Markdown 전략 구현
- [ ] `MarkdownIngestionStrategy` 구현
  - 기존 `MarkdownParser` + `MarkdownChunker` 통합
  - 파라미터: chunk_size=1200, overlap=200
- [ ] 테스트: 섹션 기반 분할 검증

### Step 4: FAQ 전략 구현
- [ ] `FAQIngestionStrategy` 구현
  - 기존 `FAQParser` + `FAQChunker` 통합
  - 파라미터: chunk_size=800, overlap=100
- [ ] 테스트: Q&A 쌍 유지 검증

### Step 5: 팩토리 함수 구현
- [ ] `get_ingestion_strategy(context_type)` 작성
- [ ] 테스트: 유효/무효 타입 처리

### Step 6: 서비스 레이어 리팩터링
- [ ] `ingestion.py` 수정
  - `_get_chunker()`, `_get_parser()` 제거
  - `ingest_document()` 내부에서 전략 사용
- [ ] 테스트: 기존 통합 테스트 통과 확인

### Step 7: 회귀 테스트 및 정리
- [ ] 전체 테스트 스위트 실행 (`uv run pytest`)
- [ ] mypy, ruff 체크
- [ ] 사용되지 않는 임포트 정리

## Rollback
각 Step 후 커밋 → 실패 시 `git reset --hard HEAD~1`

## Review Hotspots
- `strategies.py` - 파서/청커 인스턴스화 타이밍 (메모리 효율)
- `ingestion.py:ingest_document()` - 전략 호출 부분 (에러 핸들링)
- `test_ingestion_service.py` - 기존 테스트 변경 없이 통과 여부

## Status
- [x] Step 1: 기본 전략 인터페이스 정의 - `BaseIngestionStrategy` 추상 클래스 작성 완료
- [x] Step 2: PDF 전략 구현 - `PDFIngestionStrategy` 완료 (chunk_size=1000, overlap=150)
- [x] Step 3: Markdown 전략 구현 - `MarkdownIngestionStrategy` 완료 (chunk_size=1200, overlap=200)
- [x] Step 4: FAQ 전략 구현 - `FAQIngestionStrategy` 완료 (chunk_size=800, overlap=100)
- [x] Step 5: 팩토리 함수 구현 - `get_ingestion_strategy()` 완료, 4개 테스트 통과
- [x] Step 6: 서비스 레이어 리팩터링 - `_get_chunker()`, `_get_parser()` 제거, 전략 사용
- [x] Step 7: 회귀 테스트 및 정리 - 108개 테스트 통과, mypy/ruff 클린
