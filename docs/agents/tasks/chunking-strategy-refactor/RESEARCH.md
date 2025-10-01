# Research: 타입별 청킹 전략 리팩터링

## Goal
파싱과 청킹 로직을 분리하고 타입별 전략 패턴으로 리팩터링하여 유지보수성 향상

## Scope
- `backend/ingestion/parsers.py` - 3개 파서 (PDF, Markdown, FAQ)
- `backend/ingestion/chunkers.py` - 4개 청커 (Text, Markdown, FAQ, PDF)
- `backend/services/ingestion.py` - 파서/청커 매핑 로직

## Related Files & Flows

### Current Architecture
1. **Parsers** (`backend/ingestion/parsers.py`):
   - `PDFParser` - Docling 기반 PDF 파싱
   - `MarkdownParser` - 단순 텍스트 읽기
   - `FAQParser` - 단순 텍스트 읽기

2. **Chunkers** (`backend/ingestion/chunkers.py`):
   - `TextChunker` - 기본 오버랩 청킹 (1000/200)
   - `MarkdownChunker(TextChunker)` - 섹션 인식 (1200/200)
   - `FAQChunker(TextChunker)` - Q&A 쌍 유지 (800/100)
   - `PDFChunker(TextChunker)` - 정규화 + 구조 인식 (1000/150)

3. **Service Layer** (`backend/services/ingestion.py:18-36`):
   - `_get_chunker()` - 타입별 청커 인스턴스 반환
   - `_get_parser()` - 타입별 파서 인스턴스 반환
   - `ingest_document()` - 파싱 → 청킹 → DB 저장 파이프라인

### References
- **Direct usage**: `backend/routers/contexts.py:136` (PDFParser for preview)
- **Service usage**: `backend/services/ingestion.py:29,32` (전체 파서/청커)
- **Tests**: `backend/tests/test_ingestion_service.py` (Markdown 인제스션 테스트)

## Hypotheses

### H1: 파서와 청커가 밀결합되어 있음
**Evidence:**
- 서비스 레이어에서 타입별로 두 개의 독립적인 딕셔너리 매핑
- 타입 문자열 ("PDF", "MARKDOWN", "FAQ") 중복 사용
- 새 타입 추가 시 3곳(파서, 청커, 서비스) 수정 필요

### H2: 청커 파라미터가 하드코딩됨
**Evidence:**
- `ingestion.py:18-24` chunk_size/overlap 값이 인스턴스화 시점에 고정
- 문서 길이/복잡도에 따른 동적 조정 불가능
- 설정 변경 시 코드 수정 + 재배포 필요

### H3: 타입별 전략이 분산됨
**Evidence:**
- 파서 로직: `parsers.py`
- 청킹 로직: `chunkers.py`
- 매핑 로직: `ingestion.py`
- 관련 코드가 3개 파일에 흩어져 있음

## Assumptions & Open Questions

### Assumptions
- 기존 청크 크기/오버랩 값은 검증된 최적값 (변경 X)
- PDF 미리보기는 파서만 사용 (청커 독립적)
- FAQ 타입의 Q&A 패턴 (`Q:...`) 변경 없음

### Open Questions
- [ ] 향후 타입 추가 예정? (DOCX, HTML, etc.)
- [ ] 청크 크기를 환경변수/DB 설정으로 관리할 필요?
- [ ] 파서/청커 교체 가능성? (Docling → LlamaParse 등)

## Risks

1. **하위 호환성**: 기존 ContextItem의 metadata 스키마 변경 가능성
2. **테스트 커버리지**: 타입별 청킹 로직의 엣지케이스 미검증
3. **성능**: 전략 패턴 도입 시 인스턴스화 오버헤드

## Next
**Plan** 단계로 이동 - 전략 패턴 설계 및 리팩터링 스텝 정의
