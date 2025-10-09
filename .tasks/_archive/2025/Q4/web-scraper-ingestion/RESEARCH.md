# Research: Web Scraper Ingestion

## Goal
KNUE HWP 문서 뷰어 등 JavaScript 렌더링이 필요한 웹 페이지에서 텍스트를 추출하여 컨텍스트로 저장하는 기능 추가.

## Scope
- **Target URL pattern**: `https://www.knue.ac.kr/www/previewMenuCntFile.do?key=392&fileNo=1489`
- **Requirements**:
  - JS 렌더링된 iframe 내부 텍스트 추출
  - Puppeteer를 활용한 스크롤/대기/텍스트 추출 파이프라인
  - PDF/Markdown/FAQ와 동일한 인제스션 패턴 유지

## Related Files/Flows

### Existing Ingestion Architecture
- **Parsers**: `backend/ingestion/parsers.py` (PDFParser, MarkdownParser, FAQParser)
- **Chunkers**: `backend/ingestion/chunkers.py` (TextChunker 기반, 타입별 전략)
- **Strategies**: `backend/ingestion/strategies.py` (`BaseIngestionStrategy`, factory pattern)
- **Service**: `backend/services/ingestion.py` (`ingest_document()` - 파싱→청킹→저장)
- **Models**: `backend/models/context.py` (`Context.context_type`, `ContextItem`)
- **Router**: `backend/routers/contexts.py` (`create_context()` - multipart/form-data)

### Relevant Tests
- `backend/tests/test_ingestion_service.py` - 인제스션 로직 테스트
- `backend/tests/admin/test_admin_contexts.py` - Context CRUD 테스트
- `backend/tests/test_contexts.py` - 컨텍스트 생성 테스트

### Docker Setup
- **Base**: `docker-compose.yml`, `docker-compose.dev.yml`
- **Services**: `backend`, `frontend`, `postgres`, `redis`, `qdrant`, `celery`, `flower`

## Hypotheses

### H1: Puppeteer를 별도 서비스로 분리
- **Rationale**: FastAPI 프로세스에서 직접 Puppeteer 실행 시 메모리/CPU 부담 및 동시성 문제
- **Approach**:
  - `puppeteer` Docker 서비스 추가 (Node.js 기반)
  - FastAPI → HTTP API 호출로 텍스트 추출 요청
  - 또는 공유 Redis 큐를 통한 비동기 처리

### H2: WebScraperParser는 URL을 받아 Puppeteer 서비스 호출
- **Interface**: `parse_url(url: str) -> str` (기존 `parse_file(file_path)` 대신)
- **Flow**:
  1. Puppeteer 서비스에 URL 전송
  2. JS 렌더링 → iframe 탐색 → 스크롤 → 텍스트 추출
  3. 추출된 텍스트 반환

### H3: WebScraperChunker는 HTML 구조 인식
- **특성**: 웹 문서는 `<div class="synap-page">` 등 DOM 구조 유지 가능성
- **Approach**: Markdown처럼 구조 기반 청킹 (섹션/단락 우선)

### H4: context_type = "WEBSCRAPER" 추가
- **Schema**: `ContextCreate`에서 `context_type` 검증 로직 확장
- **DB**: 기존 `VARCHAR(20)` 컬럼에 추가 제약 없음 (변경 불필요)
- **Router**: `create_context()` 엔드포인트에서 URL 필드 추가 (`url: str | None = Form(None)`)

## Evidence

### Puppeteer 스크립트 분석 (제공된 코드)
```javascript
// 1. 메인 페이지 진입 → iframe 대기
await $page.goto($json.preview_link, { waitUntil: 'networkidle2', timeout: 180000 });
await $page.waitForSelector('iframe#innerWrap', { timeout: 180000 });

// 2. iframe src 추출 → 직접 이동
const iframeSrc = await $page.evaluate(() => {
    const iframe = document.querySelector('iframe#innerWrap');
    return iframe ? iframe.src : null;
});
await $page.goto(iframeSrc, { waitUntil: 'networkidle2', timeout: 180000 });

// 3. 스크롤 끝까지 (동적 콘텐츠 로딩 대기)
await $page.evaluate(async () => {
    let prev = 0, sameCount = 0, totalHeight = 0;
    while (true) {
        window.scrollBy(0, 300);
        await new Promise(r => setTimeout(r, 200));
        let sh = document.body.scrollHeight;
        totalHeight += 300;
        if (sh === prev) sameCount++; else { sameCount = 0; prev = sh; }
        if (sameCount >= 5) break;
        if (totalHeight > 1000000) break;
    }
    await new Promise(r => setTimeout(r, 2000));
});

// 4. 텍스트 추출 (선택자 우선순위)
const selectors = ['.synap-page', '.page', '.document-page'];
let texts = [];
for (let sel of selectors) {
    let nodes = await $page.$$eval(sel, nodes => nodes.map(n => n.innerText.trim()).filter(Boolean));
    if (nodes.length) { texts = nodes; break; }
}
if (texts.length === 0) {
    let bodyText = await $page.evaluate(() => document.body.innerText);
    texts = [bodyText];
}
const finalText = texts.join('\n\n');
```

**Key Insights**:
- 3분(180초) 타임아웃 필요 (네트워크 지연 고려)
- 스크롤 완료 조건: scrollHeight 5회 연속 동일
- 페이지별 텍스트 분할 가능 (`.synap-page` 등)

### Existing Context Types
- **PDF**: 파일 업로드 필수, Docling 파싱
- **MARKDOWN**: 파일 선택적, 텍스트 직접 파싱
- **FAQ**: 파일 선택적, Q&A 구조 파싱

→ **WEBSCRAPER**: 파일 불필요, URL 필수

## Assumptions/Open Questions

### A1: Puppeteer 서비스 API 설계
- **Option A**: REST API (`POST /scrape` with `{url: string}` → `{text: string}`)
- **Option B**: Celery 태스크로 통합 (기존 Redis 활용)
- **Decision**: **Option A** 선택 (단순성, 독립성)

### A2: 에러 처리
- **Q**: Timeout/네트워크 오류 시 재시도?
- **A**: 1회 재시도 + `processing_status="FAILED"` 설정

### A3: 보안
- **Q**: 임의 URL 스크래핑 허용?
- **A**: Admin-only 엔드포인트, URL 패턴 검증 (`*.knue.ac.kr` 등) 선택적

### A4: 캐싱
- **Q**: 동일 URL 재요청 시 캐싱?
- **A**: Phase 1에서는 미구현, 향후 Redis 캐시 추가 가능

## Risks

1. **Puppeteer 크래시**: 메모리 부족 시 Docker 재시작 메커니즘 필요
2. **Long-running requests**: 180초 타임아웃이 FastAPI 기본 타임아웃 초과 가능 → uvicorn `--timeout-keep-alive` 조정
3. **XSS/보안**: 추출된 텍스트에 악성 스크립트 포함 가능 → HTML 태그 제거 필수
4. **Rate limiting**: 외부 사이트 스크래핑 시 차단 위험 → User-Agent 설정, 요청 간격 조절

## Next Steps

1. **PLAN.md 작성**: 파일 구조, API 설계, 테스트 계획
2. **Puppeteer Docker 서비스 구현**: `Dockerfile.puppeteer`, `docker-compose` 통합
3. **WebScraperParser 구현**: Puppeteer API 클라이언트
4. **WebScraperChunker/Strategy 구현**: 기존 패턴 확장
5. **API 엔드포인트 수정**: `create_context()` URL 파라미터 추가
6. **테스트 작성**: 단위/통합 테스트
