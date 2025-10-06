# Progress: Web Scraper Ingestion

## Summary
KNUE HWP 뷰어 등 JavaScript 렌더링 웹 문서를 Puppeteer로 스크래핑하여 컨텍스트로 저장하는 `WEBSCRAPER` 타입 추가 완료.

## Goal & Approach
- **Goal**: `https://www.knue.ac.kr/www/previewMenuCntFile.do?key=392&fileNo=1489` 등 JS 렌더링 필요 웹 페이지에서 텍스트 추출 후 RAG 시스템에 통합
- **Approach**: Puppeteer Docker 서비스 + FastAPI Parser/Chunker/Strategy 확장

## Completed Steps

### Phase 1: Puppeteer Service ✅
- ✅ `services/puppeteer/index.js` - Express 서버, `/scrape` POST 엔드포인트
- ✅ `services/puppeteer/package.json` - Puppeteer 의존성
- ✅ `services/puppeteer/Dockerfile` - Node.js 20 + Chromium
- ✅ `docker-compose.dev.yml` - `puppeteer` 서비스 추가 (포트 3000)

**Key Features**:
- iframe 탐색 및 동적 콘텐츠 로딩 (스크롤 완료 감지)
- 선택자 우선순위: `.synap-page`, `.page`, `.document-page` → fallback `body.innerText`
- HTML 태그 제거 (XSS 방지)
- 180초 타임아웃, networkidle2 대기

### Phase 2: Backend Parser ✅
- ✅ `backend/ingestion/parsers.py::WebScraperParser` 추가
  - `parse_url(url)` 메서드: Puppeteer 서비스 호출
  - 에러 처리: `ValueError` (invalid URL/scraping 실패), `TimeoutError` (190초 타임아웃)
  - mypy strict 통과 (`text: str = str(data.get("text", ""))`)
- ✅ `backend/config.py::Settings.PUPPETEER_URL` 추가 (기본값: `http://puppeteer:3000`)

### Phase 3: Backend Chunker & Strategy ✅
- ✅ `backend/ingestion/chunkers.py::WebScraperChunker` 추가
  - `_web_aware_chunking()`: 단락/문장 우선 청킹
  - 기본값: `chunk_size=1000`, `overlap=150`
- ✅ `backend/ingestion/strategies.py::WebScraperIngestionStrategy` 추가
  - `parse(url)` 오버라이드 (file_path 대신 URL 사용)
- ✅ `get_ingestion_strategy()` factory 확장: `"WEBSCRAPER"` 케이스 추가

### Phase 4: API Integration ✅
- ✅ `backend/services/ingestion.py::ingest_document()` 수정
  - 시그니처 변경: `file_path: str | None = None`, `url: str | None = None` 추가
  - `context_type == "WEBSCRAPER"` 분기 처리
  - `source_url` 메타데이터 저장
- ✅ `backend/routers/contexts.py::create_context()` 수정
  - `url: str | None = Form(None)` 파라미터 추가
  - 검증 로직: `context_type == "WEBSCRAPER"` 시 URL 필수
  - `_process_webscraper_upload()` 함수 추가
- ✅ ruff + mypy strict 통과

### Phase 5: Testing ✅
- ✅ `backend/tests/test_webscraper_parser.py` (6 tests, 100% pass)
  - `test_parse_url_success`, `test_parse_url_invalid_url`, `test_parse_url_puppeteer_error`
  - `test_parse_url_timeout`, `test_parse_url_no_text_extracted`, `test_parse_url_connection_error`
- ✅ `backend/tests/test_webscraper_chunker.py` (6 tests, 100% pass)
  - `test_chunk_text_simple`, `test_chunk_text_empty`, `test_chunk_text_with_paragraphs`
  - `test_chunk_text_long_content`, `test_chunk_text_with_newlines`, `test_chunk_text_preserves_content`

## Current Failures
없음

## Decision Log

### D1: Puppeteer 서비스 분리 vs FastAPI 내부 통합
**Decision**: 별도 Docker 서비스로 분리
**Rationale**:
- FastAPI 프로세스에서 Puppeteer 실행 시 메모리/CPU 부담
- 독립적 스케일링 및 재시작 가능
- Node.js 의존성 격리

### D2: REST API vs Celery 태스크
**Decision**: REST API (`POST /scrape`)
**Rationale**:
- 단순성 및 독립성
- Celery는 이미 임베딩 재생성 용도로 사용 중
- 180초 타임아웃 직접 제어 가능

### D3: 보안 - URL 검증
**Decision**: Admin-only 엔드포인트, HTML 태그 제거
**Rationale**:
- Phase 1에서는 특정 도메인(`*.knue.ac.kr`) 검증 미구현 (향후 옵션)
- HTML 태그 제거로 XSS 최소화

### D4: 캐싱
**Decision**: Phase 1에서 미구현
**Rationale**:
- 동일 URL 재요청 빈도 낮을 것으로 예상
- 향후 Redis 캐시 추가 가능

## Files Touched

### Created
- `services/puppeteer/index.js`
- `services/puppeteer/package.json`
- `services/puppeteer/Dockerfile`
- `backend/tests/test_webscraper_parser.py`
- `backend/tests/test_webscraper_chunker.py`

### Modified
- `docker-compose.dev.yml` - puppeteer 서비스 추가
- `backend/config.py` - PUPPETEER_URL 설정 추가
- `backend/ingestion/parsers.py` - WebScraperParser 추가
- `backend/ingestion/chunkers.py` - WebScraperChunker 추가
- `backend/ingestion/strategies.py` - WebScraperIngestionStrategy 추가, factory 확장
- `backend/services/ingestion.py` - ingest_document() 시그니처 변경, WEBSCRAPER 분기
- `backend/routers/contexts.py` - create_context() url 파라미터 추가, _process_webscraper_upload() 함수

## Artifacts Updated
- `RESEARCH.md` - 완료
- `PLAN.md` - 완료
- `PROGRESS.md` - 본 문서

## Next Step
수동 테스트 (optional):
1. `docker compose -f docker-compose.yml -f docker-compose.dev.yml up --build puppeteer`
2. `curl -X POST http://localhost:3000/scrape -H "Content-Type: application/json" -d '{"url": "https://www.knue.ac.kr/www/previewMenuCntFile.do?key=392&fileNo=1489"}'`
3. FastAPI `/api/admin/contexts` POST with `context_type=WEBSCRAPER`, `url=...`
