# Plan: Web Scraper Ingestion

## Objective
KNUE HWP 뷰어 등 JS 렌더링 웹 문서를 Puppeteer로 스크래핑하여 컨텍스트로 저장하는 `WEBSCRAPER` 타입 추가.

## Constraints
- 기존 인제스션 아키텍처(Parser/Chunker/Strategy) 패턴 유지
- Admin-only 기능 (보안)
- Puppeteer는 별도 Docker 서비스로 격리
- 180초 타임아웃 고려

## Target Files & Changes

### 1. Puppeteer Service (New)
**Files**:
- `services/puppeteer/index.js` - Express 서버, `/scrape` 엔드포인트
- `services/puppeteer/package.json` - Puppeteer 의존성
- `services/puppeteer/Dockerfile` - Node.js + Chromium
- `docker-compose.dev.yml` - `puppeteer` 서비스 추가

**Changes**:
- POST `/scrape` with `{url: string}` → `{text: string, metadata: object}`
- Puppeteer 스크립트: iframe 탐색 → 스크롤 → 텍스트 추출
- 타임아웃: 180초, 재시도: 1회

### 2. Backend Parser (New)
**File**: `backend/ingestion/parsers.py`

**Changes**:
```python
class WebScraperParser:
    def __init__(self, puppeteer_url: str = "http://puppeteer:3000"):
        self.puppeteer_url = puppeteer_url

    def parse_url(self, url: str) -> str:
        # POST to puppeteer service
        # Return extracted text
        # Raise if timeout/error
```

### 3. Backend Chunker (New)
**File**: `backend/ingestion/chunkers.py`

**Changes**:
```python
class WebScraperChunker(TextChunker):
    def __init__(self, chunk_size: int = 1000, overlap: int = 150):
        super().__init__(chunk_size, overlap)

    def chunk_text(self, text: str) -> list[str]:
        # HTML-aware chunking (similar to MarkdownChunker)
        # Prefer section/paragraph breaks
```

### 4. Backend Strategy (New)
**File**: `backend/ingestion/strategies.py`

**Changes**:
```python
class WebScraperIngestionStrategy(BaseIngestionStrategy):
    def __init__(self, chunk_size: int = 1000, overlap: int = 150):
        self.parser = WebScraperParser()
        self.chunker = WebScraperChunker(chunk_size, overlap)

    def parse(self, url: str) -> str:  # Note: url not file_path
        return self.parser.parse_url(url)

    def chunk(self, text: str) -> list[str]:
        return self.chunker.chunk_text(text)

# Update factory
def get_ingestion_strategy(context_type: str) -> BaseIngestionStrategy:
    strategy_map = {
        "PDF": PDFIngestionStrategy(),
        "MARKDOWN": MarkdownIngestionStrategy(),
        "FAQ": FAQIngestionStrategy(),
        "WEBSCRAPER": WebScraperIngestionStrategy(),  # ADD
    }
    ...
```

### 5. Backend Service (Modify)
**File**: `backend/services/ingestion.py`

**Changes**:
```python
def ingest_document(
    db: Session,
    context_id: int,
    file_path: str | None = None,  # Optional for WEBSCRAPER
    url: str | None = None,         # ADD
    title: str,
    context_type: str,
) -> int:
    strategy = get_ingestion_strategy(context_type)

    if context_type == "WEBSCRAPER":
        if not url:
            raise ValueError("URL required for WEBSCRAPER")
        content = strategy.parse(url)  # parse_url
    else:
        if not file_path:
            raise ValueError("file_path required")
        content = strategy.parse(file_path)

    chunks = strategy.chunk(content)
    # ... (save to DB)
```

### 6. Backend Router (Modify)
**File**: `backend/routers/contexts.py`

**Changes**:
```python
@router.post("/contexts", ...)
def create_context(
    name: str = Form(...),
    description: str = Form(...),
    context_type: str = Form(...),
    original_content: str | None = Form(None),
    file: UploadFile | None = File(None),
    url: str | None = Form(None),  # ADD
    db: Session = Depends(get_db),
) -> Context:
    # Validate context_type
    if context_type not in ["PDF", "MARKDOWN", "FAQ", "WEBSCRAPER"]:  # ADD
        raise HTTPException(422, "Invalid context_type")

    if context_type == "WEBSCRAPER":
        if not url:
            raise HTTPException(400, "URL required for WEBSCRAPER")
        # Process web scraper
        _process_webscraper_upload(context, url, db)
    elif context_type == "PDF":
        if not file:
            raise HTTPException(400, "File required for PDF")
        _process_pdf_upload(context, file, db)

    return context

def _process_webscraper_upload(context: Context, url: str, db: Session) -> None:
    num_chunks = ingest_document(
        db=db,
        context_id=context.id,
        url=url,
        title=context.name,
        context_type="WEBSCRAPER",
    )

    # Store original_content as extracted text
    if num_chunks > 0:
        strategy = get_ingestion_strategy("WEBSCRAPER")
        text_content = strategy.parse(url)
        context.original_content = text_content
        context.processing_status = "COMPLETED"
    else:
        context.processing_status = "FAILED"

    db.commit()
```

### 7. Backend Config (Modify)
**File**: `backend/config.py`

**Changes**:
```python
class Settings(BaseSettings):
    ...
    PUPPETEER_URL: str = Field(default="http://puppeteer:3000")
```

### 8. Docker Compose (Modify)
**Files**: `docker-compose.yml`, `docker-compose.dev.yml`

**Changes**:
```yaml
services:
  puppeteer:
    build:
      context: ./services/puppeteer
      dockerfile: Dockerfile
    ports:
      - "3000:3000"
    environment:
      NODE_ENV: production
    restart: unless-stopped
```

## Test/Validation Cases

### Unit Tests
**File**: `backend/tests/test_webscraper_parser.py` (new)
- ✅ `test_parse_url_success`: Mock Puppeteer 응답, 텍스트 추출 확인
- ✅ `test_parse_url_timeout`: Timeout 에러 처리
- ✅ `test_parse_url_invalid_response`: 빈 응답 처리

**File**: `backend/tests/test_webscraper_chunker.py` (new)
- ✅ `test_chunk_text_simple`: 단순 텍스트 청킹
- ✅ `test_chunk_text_with_structure`: 단락/섹션 구분 유지
- ✅ `test_chunk_text_empty`: 빈 텍스트 처리

**File**: `backend/tests/test_webscraper_strategy.py` (new)
- ✅ `test_parse_and_chunk`: 전체 파이프라인
- ✅ `test_get_ingestion_strategy_webscraper`: Factory 함수

### Integration Tests
**File**: `backend/tests/test_webscraper_ingestion.py` (new)
- ✅ `test_create_webscraper_context`: API 엔드포인트 호출, DB 저장 확인
- ✅ `test_webscraper_missing_url`: URL 누락 시 400 에러
- ✅ `test_webscraper_invalid_url`: Puppeteer 에러 시 FAILED 상태

**File**: `backend/tests/test_webscraper_e2e.py` (new, optional)
- ✅ `test_real_knue_url`: 실제 KNUE URL 스크래핑 (CI에서 스킵 가능)

## Steps

### Phase 1: Puppeteer Service
1. [ ] Create `services/puppeteer/` directory
2. [ ] Write `services/puppeteer/index.js` (Express + Puppeteer)
3. [ ] Write `services/puppeteer/Dockerfile`
4. [ ] Write `services/puppeteer/package.json`
5. [ ] Update `docker-compose.dev.yml` (add `puppeteer` service)
6. [ ] Test: `docker compose up puppeteer` → curl `/scrape`

### Phase 2: Backend Parser
7. [ ] Add `WebScraperParser` to `backend/ingestion/parsers.py`
8. [ ] Add `PUPPETEER_URL` to `backend/config.py`
9. [ ] Write unit tests: `test_webscraper_parser.py`
10. [ ] Test: Mock Puppeteer, verify parse_url()

### Phase 3: Backend Chunker & Strategy
11. [ ] Add `WebScraperChunker` to `backend/ingestion/chunkers.py`
12. [ ] Add `WebScraperIngestionStrategy` to `backend/ingestion/strategies.py`
13. [ ] Update `get_ingestion_strategy()` factory
14. [ ] Write unit tests: `test_webscraper_chunker.py`, `test_webscraper_strategy.py`
15. [ ] Test: Verify chunking behavior

### Phase 4: API Integration
16. [ ] Modify `ingest_document()` in `backend/services/ingestion.py` (add `url` param)
17. [ ] Add `_process_webscraper_upload()` to `backend/routers/contexts.py`
18. [ ] Modify `create_context()` (add `url` param, validation)
19. [ ] Write integration tests: `test_webscraper_ingestion.py`
20. [ ] Test: POST `/api/admin/contexts` with `context_type=WEBSCRAPER`

### Phase 5: Validation
21. [ ] Run all tests: `uv run pytest`
22. [ ] Manual test: Create WEBSCRAPER context via API
23. [ ] Manual test: Verify chunks in DB, Qdrant embeddings
24. [ ] (Optional) Test with real KNUE URL

## Rollback Plan
1. Remove `puppeteer` service from `docker-compose`
2. Revert changes to `parsers.py`, `chunkers.py`, `strategies.py`
3. Revert `create_context()` router changes
4. Delete test files
5. `git revert` or `git reset --hard`

## Review Hotspots
- **Puppeteer timeout handling**: 180초 vs FastAPI 기본 타임아웃
- **Error propagation**: Puppeteer 에러 → Parser 에러 → processing_status="FAILED"
- **Security**: URL 검증, XSS 방지 (HTML 태그 제거)
- **Concurrency**: Puppeteer 서비스 동시 요청 처리 (queue 필요 여부)

## Status
- [ ] Phase 1: Puppeteer Service
- [ ] Phase 2: Backend Parser
- [ ] Phase 3: Backend Chunker & Strategy
- [ ] Phase 4: API Integration
- [ ] Phase 5: Validation
