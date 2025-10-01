# Plan: Production Deployment with Celery Worker

## Objective
`docker-compose.prod.yml`에 Celery 워커 추가 및 프로덕션 배포 문서 업데이트.

## Constraints
- **No breaking changes**: 기존 프로덕션 서비스 정의 유지
- **Resource limits**: Celery 워커 리소스 제한 설정 (메모리 1GB, CPU 0.5)
- **Health check**: 워커 상태 모니터링 추가
- **Documentation**: 배포 가이드 최신화

## Target Files & Changes

### 1. Modify existing
- **`docker-compose.prod.yml`**
  - `celery-worker` 서비스 추가 (redis, postgres, qdrant depends_on)
  - backend와 동일한 환경변수 공유
  - 리소스 제한 + 로깅 설정
- **`.env.prod.example`**
  - Celery 관련 변수 추가 (선택적, redis_url 재사용)
- **`docs/DEPLOYMENT.md`**
  - Celery 워커 서비스 설명 추가
  - 아키텍처 다이어그램 업데이트
- **`docs/PRODUCTION_DOCKER.md`**
  - Celery Worker 섹션 실제 설정과 일치시키기

### 2. No new files
- 모든 변경사항은 기존 파일 수정으로 처리

## Test/Validation Cases

### Integration Tests
1. **프로덕션 Compose 검증**
   - `docker compose -f docker-compose.prod.yml config` → 유효성 확인
2. **서비스 기동 테스트** (로컬)
   - `.env.prod` 복사 후 `docker compose -f docker-compose.prod.yml up -d`
   - 모든 서비스 `healthy` 상태 확인
3. **Celery 워커 작동 확인**
   - `docker compose -f docker-compose.prod.yml logs celery-worker` → 부팅 로그 확인
   - `docker compose -f docker-compose.prod.yml exec celery-worker celery -A backend.celery_app inspect active` → 워커 응답 확인
4. **비동기 태스크 실행 테스트**
   - Admin API로 `bulk_regenerate_embeddings` 호출 → task_ids 반환 확인
   - Celery 워커 로그에서 태스크 실행 확인

### Edge Cases
5. **Celery 워커 장애 시나리오**
   - 워커 강제 종료 후 재시작 → 미완료 태스크 복구 확인 (Redis persistence)
6. **리소스 제한 테스트**
   - 메모리 한계 도달 시 OOM killer 동작 확인

## Steps (Non-TDD, deployment task)

### [ ] Step 1: docker-compose.prod.yml 업데이트
- Add: `celery-worker` 서비스 정의 (backend 기반 복사 + command 변경)
- Validate: `docker compose -f docker-compose.prod.yml config`

### [ ] Step 2: 문서 업데이트
- Edit: `docs/DEPLOYMENT.md` → Celery 워커 추가 (아키텍처, 서비스 목록)
- Edit: `docs/PRODUCTION_DOCKER.md` → Celery Worker 섹션 실제 설정 반영

### [ ] Step 3: 로컬 프로덕션 시뮬레이션
- Run: `.env.prod` 생성 (`.env.prod.example` 복사 + 실제 값 입력)
- Run: `docker compose -f docker-compose.prod.yml up -d --build`
- Verify: 모든 서비스 healthy, Celery 워커 로그 정상

### [ ] Step 4: 비동기 태스크 통합 테스트
- Run: Admin 로그인 → bulk_regenerate_embeddings API 호출
- Verify: task_ids 반환, Celery 로그에서 태스크 실행 확인
- Verify: Qdrant에 임베딩 저장 확인

### [ ] Step 5: 프로덕션 배포 체크리스트 작성
- Write: `docs/agents/tasks/production-deployment/CHECKLIST.md`
- Include: 환경변수 설정, DB 마이그레이션, 서비스 헬스체크, 모니터링 설정

## Rollback

1. **Step 1 실패 시**: `git checkout HEAD -- docker-compose.prod.yml`
2. **Step 3 실패 시**: `docker compose -f docker-compose.prod.yml down -v` (볼륨 삭제 후 재시도)

## Review Hotspots

- **Resource limits**: Celery 워커 메모리 1GB 충분 여부 (임베딩 생성 시 메모리 사용량)
- **Depends_on vs healthcheck**: backend/postgres/redis 모두 healthy 상태 필요
- **Command override**: `celery -A backend.celery_app worker --loglevel=info` 명령 정확성

## Status

- [x] Step 1: docker-compose.prod.yml update (celery-worker service added)
- [x] Step 2: Documentation update (DEPLOYMENT.md - architecture + service list)
- [ ] Step 3: Local prod simulation (deferred - requires .env.prod with real keys)
- [ ] Step 4: Async task integration test (deferred - requires running services)
- [ ] Step 5: Production checklist (optional - can be created later)
