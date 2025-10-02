# Dockerize Frontend Dev - Research

## Goal
개발 환경에서 frontend를 Docker로 운용 - Hot reload 지원, 일관된 개발 환경

## Scope
- `docker-compose.dev.yml`에 frontend 서비스 추가
- Vite HMR (Hot Module Replacement) 지원
- Nginx 리버스 프록시 설정 유지

## Related Files/Flows

### 기존 구조
- `Dockerfile.frontend` - 프로덕션 빌드 (multi-stage, nginx 서빙)
- `docker-compose.dev.yml` - 개발 환경 (backend만 존재)
- `docker-compose.yml` - 기본 서비스 (postgres, redis, qdrant, celery-worker)
- `nginx/admin-frontend.conf` - 프로덕션 nginx 설정

### 개발 요구사항
- Vite dev server 실행 (port 5173)
- Volume mount로 소스 변경 감지
- HMR 지원 (WebSocket)
- API 프록시 설정 (VITE_API_URL)

## Hypotheses

1. **개발용 Dockerfile**: `Dockerfile.dev`처럼 별도 생성하거나, node:20-alpine 이미지 직접 사용
2. **Vite 설정**: `--host 0.0.0.0` 옵션으로 Docker 네트워크 내 접근 허용
3. **Port 매핑**: 5173:5173
4. **Volume**: `./frontend:/app` (소스 동기화), `node_modules` 익명 볼륨 (성능)
5. **환경변수**: VITE_API_URL=http://localhost:8001/api

## Evidence

- `frontend/package.json` scripts: `"dev": "vite"`
- `frontend/vite.config.ts` - 설정 파일 존재
- `docker-compose.dev.yml` - backend 서비스 패턴 참고 가능
- `Dockerfile.dev` - backend 개발 환경 참고

## Assumptions/Open Questions

1. **Node 패키지 매니저**: package.json 기준 npm 사용 (pnpm 아님, Docker 표준화)
2. **HMR 포트**: Vite 기본 24678 (자동 할당)
3. **의존성 설치**: Docker build 시 또는 entrypoint에서 npm install
4. **프록시 불필요**: frontend → backend API 직접 호출 (CORS 설정 기존 존재)

## Risks

- **빌드 시간**: node_modules 매번 설치 시 느림 → named volume으로 캐싱
- **HMR 실패**: Docker 네트워크에서 WebSocket 연결 문제 → vite.config.ts에 `server.hmr` 설정 필요
- **성능**: Volume 동기화 지연 → 로컬 개발 vs Docker 개발 선택권 유지

## Next

PLAN.md 작성 - docker-compose.dev.yml 수정, Vite 설정 확인, 테스트 계획
