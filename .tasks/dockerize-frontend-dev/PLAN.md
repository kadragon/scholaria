# Dockerize Frontend Dev - Plan

## Objective
개발 환경에서 frontend를 Docker 컨테이너로 실행 - HMR 지원, 일관된 개발 환경

## Constraints
- **HMR 필수**: 코드 변경 시 자동 리로드
- **성능**: node_modules 볼륨 캐싱
- **CORS**: 기존 backend CORS 설정 유지
- **선택적**: 로컬 개발 vs Docker 개발 모두 지원

## Target Files & Changes

### Docker 설정
1. **`docker-compose.dev.yml`** - frontend 서비스 추가
   - 이미지: node:20-alpine
   - 커맨드: `npm run dev -- --host 0.0.0.0`
   - 포트: 5173:5173
   - 볼륨: `./frontend:/app`, `node_modules` 익명
   - 환경변수: VITE_API_URL

2. **`frontend/vite.config.ts`** (선택적) - HMR 설정 확인
   - `server.host: '0.0.0.0'` (Docker 네트워크 접근)
   - `server.watch.usePolling: true` (Docker volume 감지)

### 문서
3. **`docs/DEPLOYMENT.md`** 또는 **`README.md`** - Docker 개발 환경 사용법 추가

## Test/Validation Cases

### Docker 실행
- `docker compose -f docker-compose.yml -f docker-compose.dev.yml up` 실행
- frontend 컨테이너 시작 확인
- http://localhost:5173/admin/ 접근 확인
- 소스 파일 변경 시 HMR 동작 확인

### API 연동
- Login 페이지에서 backend API 호출 확인
- CORS 에러 없이 정상 작동 확인

## Steps

1. [ ] **[Structural]** `docker-compose.dev.yml`에 frontend 서비스 추가
2. [ ] **[Structural]** `frontend/vite.config.ts` HMR 설정 확인/추가
3. [ ] **[Behavioral]** Docker compose 실행 테스트
4. [ ] **[Behavioral]** HMR 동작 확인 (파일 변경)
5. [ ] **[Behavioral]** API 연동 확인 (login)
6. [ ] **[Structural]** README.md 개발 환경 섹션 업데이트

## Rollback
- docker-compose.dev.yml 변경 사항만 되돌리면 됨 (기존 로컬 개발 방식 유지)

## Review Hotspots
- Vite HMR over Docker (WebSocket 연결)
- node_modules 볼륨 성능
- VITE_API_URL 환경변수 (컨테이너 내부 vs 브라우저)

## Status
- [ ] Step 1: docker-compose.dev.yml 수정
- [ ] Step 2: vite.config.ts 확인
- [ ] Step 3: Docker compose 실행
- [ ] Step 4: HMR 테스트
- [ ] Step 5: API 연동 테스트
- [ ] Step 6: 문서 업데이트
