# Manual Testing Guide: Web Scraper Ingestion

## Prerequisites
- Docker & Docker Compose installed
- Target URL: `https://www.knue.ac.kr/www/previewMenuCntFile.do?key=392&fileNo=1489`

## Test Steps

### 1. Start Puppeteer Service
```bash
docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d puppeteer
```

Wait for the service to initialize (~30 seconds for first run).

### 2. Verify Health Check
```bash
curl -X GET http://localhost:3000/health
```

**Expected Response:**
```json
{"status":"ok","service":"puppeteer-scraper"}
```

### 3. Test Web Scraping
```bash
curl -X POST http://localhost:3000/scrape \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.knue.ac.kr/www/previewMenuCntFile.do?key=392&fileNo=1489"}' \
  | jq '.'
```

**Expected Response:**
```json
{
  "text": "...(extracted text from HWP viewer)...",
  "metadata": {
    "url": "https://www.knue.ac.kr/www/previewMenuCntFile.do?key=392&fileNo=1489",
    "extractedAt": "2025-10-06T...",
    "chunkCount": 1,
    "textLength": 1234
  }
}
```

### 4. Test via FastAPI
```bash
# Assuming admin token is available
curl -X POST http://localhost:8001/api/admin/contexts \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN" \
  -F "name=KNUE Test Document" \
  -F "description=Test KNUE HWP document" \
  -F "context_type=WEBSCRAPER" \
  -F "url=https://www.knue.ac.kr/www/previewMenuCntFile.do?key=392&fileNo=1489"
```

**Expected Response:**
```json
{
  "id": 1,
  "name": "KNUE Test Document",
  "description": "Test KNUE HWP document",
  "context_type": "WEBSCRAPER",
  "processing_status": "COMPLETED",
  "chunk_count": 0,
  "original_content": "...(extracted text)...",
  "created_at": "2025-10-06T...",
  "updated_at": "2025-10-06T..."
}
```

### 5. Verify Database
```bash
docker exec -it scholaria-postgres-1 psql -U postgres -d scholaria -c \
  "SELECT id, name, context_type, processing_status FROM rag_context WHERE context_type='WEBSCRAPER';"
```

```bash
docker exec -it scholaria-postgres-1 psql -U postgres -d scholaria -c \
  "SELECT id, title, LENGTH(content) as content_length FROM rag_contextitem WHERE context_id=1 LIMIT 5;"
```

## Known Limitations (Local macOS Testing)

### Issue: Chromium Launch Failure
Puppeteer requires a headless browser (Chromium) which doesn't run natively on macOS ARM64 without proper system dependencies.

**Error:**
```
Error: socket hang up
code: 'ECONNRESET'
```

**Workaround:**
- Use Docker environment (Linux container) for Puppeteer
- Cannot test directly on macOS host without Docker

## Automated Tests

All unit tests pass successfully:
```bash
uv run pytest backend/tests/test_webscraper_parser.py backend/tests/test_webscraper_chunker.py -v
```

**Result:** 12/12 tests passing ✅

## Production Deployment Notes

1. Ensure Puppeteer service starts with `docker compose up`
2. Check logs: `docker compose logs puppeteer -f`
3. Monitor memory usage (Chromium can be resource-intensive)
4. Consider adding request queuing for concurrent scraping loads
5. Add URL allowlist for security (e.g., `*.knue.ac.kr` only)

## Troubleshooting

### Puppeteer Container Not Starting
```bash
docker compose -f docker-compose.yml -f docker-compose.dev.yml ps puppeteer
docker compose -f docker-compose.yml -f docker-compose.dev.yml logs puppeteer
```

### Timeout Errors (>180s)
- Check network connectivity to target URL
- Verify iframe rendering completes
- Increase timeout in `services/puppeteer/index.js` if needed

### Empty Text Extracted
- Check if target page structure changed (selectors: `.synap-page`, `.page`, `.document-page`)
- Verify iframe content is accessible
- Check browser console logs in Puppeteer
