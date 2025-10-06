# Plan: Puppeteer Upgrade & Dockerfile Fix

## Objective
puppeteer 서비스 제거 및 backend에서 직접 puppeteer 공식 이미지 사용

## Constraints
- 기존 WebScraperParser API 호환성 유지
- Docker 빌드 최적화

## Target Files & Changes
1. **services/puppeteer/** - 삭제 (별도 서비스 불필요)
2. **docker-compose.dev.yml** - puppeteer 서비스를 공식 이미지로 변경 (CDP 전용)
3. **backend/ingestion/parsers.py** - WebScraperParser를 pyppeteer 또는 playwright로 변경

## Test/Validation
- Docker 빌드 경고 없음
- puppeteer 컨테이너 정상 실행
- `POST /scrape` 엔드포인트로 제공된 URL 파싱 테스트

## Steps
- [x] Step 1: playwright 의존성 추가
- [x] Step 2: WebScraperParser를 playwright로 재작성
- [x] Step 3: 동작 검증 (제공된 URL 파싱 성공)
- [x] Step 4: puppeteer 서비스 제거
- [x] Step 5: docker-compose.dev.yml에서 puppeteer 제거

## Rollback
`git restore services/puppeteer/package.json services/puppeteer/Dockerfile`

## Review Hotspots
- puppeteer API 변경사항 확인
