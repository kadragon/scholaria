# Task Summary: Puppeteer to Playwright Migration

## Goal
puppeteer 별도 서비스 제거 및 backend에서 playwright 직접 사용

## Key Changes
- **backend/ingestion/parsers.py**: WebScraperParser를 playwright.sync_api로 재작성
- **pyproject.toml**: playwright 1.55.0 추가
- **services/puppeteer/**: 전체 삭제
- **docker-compose.dev.yml**: puppeteer 서비스 제거
- **frontend/src/pages/contexts/create.tsx**: WEBSCRAPER 타입 및 Web URL 탭 추가

## Tests
- 제공된 URL 파싱 성공 (66,637자 추출)
- ruff, mypy 통과

## Commits
- (미커밋)
