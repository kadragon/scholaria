# Research: Production Deployment Verification

## Goal
Celery 워커를 포함한 프로덕션 환경 배포 검증 및 전체 시스템 통합 테스트.

## Scope
- `docker-compose.prod.yml` 설정 검증 (Celery 워커 누락 확인)
- 프로덕션 환경 설정 파일 완성도 점검
- 배포 전 체크리스트 수립

## Related Files & Flows

### 1. Production Configuration
- **`docker-compose.prod.yml`** → 프로덕션 서비스 정의
  - backend, postgres, redis, qdrant, frontend, nginx 존재
  - **Celery 워커 누락** (최근 docker-compose.yml에만 추가됨)
- **`docker-compose.yml`** → 개발 환경 (Celery 워커 존재)
- **`.env.prod.example`** → 프로덕션 환경변수 템플릿 (확인 필요)

### 2. Documentation
- **`docs/DEPLOYMENT.md`** (489 lines) → 배포 가이드
  - Celery 워커 언급 **없음** (구식)
  - 서비스 목록에 celery-worker 누락
- **`docs/PRODUCTION_DOCKER.md`** (340 lines) → 프로덕션 Docker 가이드
  - Celery Worker/Beat 언급 있음 (lines 10-11)
  - 하지만 실제 compose 설정과 불일치

### 3. Deployment Scripts
- **`scripts/deploy.sh`** → 배포 자동화 스크립트 (확인 필요)
- **`Dockerfile.backend`** → 백엔드 프로덕션 이미지 (Celery 실행 가능 여부 확인 필요)

## Hypotheses

**H1**: `docker-compose.prod.yml`에 Celery 워커 서비스 누락 → 추가 필요.
**H2**: `.env.prod.example`에 Celery 관련 환경변수 부재 가능성.
**H3**: 문서와 실제 구성 간 불일치 → 문서 업데이트 필요.

## Evidence

1. **docker-compose.yml vs docker-compose.prod.yml 비교**:
   - `docker-compose.yml:34-49` → `celery-worker` 서비스 존재
   - `docker-compose.prod.yml` → Celery 워커 **없음**
2. **PRODUCTION_DOCKER.md 불일치**:
   - Line 11: "Celery Worker: Background task processing" 명시
   - 실제 compose 파일에는 정의 없음
3. **최근 변경사항**:
   - 직전 커밋 `ce6ed1a`에서 `docker-compose.yml`에만 워커 추가
   - 프로덕션 파일 누락

## Assumptions

- `Dockerfile.backend`는 Celery 명령 실행 가능 (dependencies 포함)
- Redis는 프로덕션 환경에서 이미 작동 중
- 프로덕션 배포는 로컬에서 Docker Compose로 시뮬레이션 가능

## Open Questions

1. **Health check**: Celery 워커의 헬스체크 전략? (worker control inspect 사용?)
2. **Resource limits**: 워커 메모리/CPU 제한 설정?
3. **Scaling**: 워커 레플리카 수 설정 (기본 1, 향후 스케일 업 가능)?
4. **.env.prod.example**: `CELERY_*` 환경변수 필요 여부?

## Risks

- **Deployment regression**: 프로덕션 배포 시 Celery 태스크 실행 불가 → 임베딩 재생성 실패
- **Documentation debt**: 문서 업데이트 누락 시 운영팀 혼란
- **Missing monitoring**: Celery 워커 모니터링 없이 배포 시 장애 감지 지연

## Next

1. **Plan**: `docker-compose.prod.yml`에 celery-worker 추가 + 문서 업데이트
2. **Verify**: 로컬 프로덕션 시뮬레이션 (`docker-compose.prod.yml` 기동 테스트)
3. **Checklist**: 프로덕션 배포 체크리스트 작성
