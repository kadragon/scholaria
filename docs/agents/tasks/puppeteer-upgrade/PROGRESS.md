# Progress: Puppeteer Upgrade & Dockerfile Fix

## Summary
puppeteer 경고 메시지 해결 (deprecated 버전 업그레이드 + npm ci 플래그 수정)

## Goal & Approach
1. puppeteer 21.6.1 → 24.15.0 업그레이드
2. `--only=production` → `--omit=dev` 수정
3. Docker 빌드 및 동작 검증

## Completed Steps
- playwright 1.55.0 추가 및 chromium 설치
- WebScraperParser를 Playwright sync_api로 재작성
- 제공된 URL 파싱 성공 (66,637자 추출)
- puppeteer 서비스 및 디렉토리 제거
- docker-compose.dev.yml 정리
- frontend create.tsx에 WEBSCRAPER 탭 추가 (4개 탭: Markdown/PDF/FAQ/Web URL)

## Decision Log
- puppeteer 24.15.0: 최신 stable (2025-01 기준)
- `--omit=dev`로 변경하여 npm 8+ 권장 플래그 사용

## Next Step
완료 - ruff, mypy 통과
