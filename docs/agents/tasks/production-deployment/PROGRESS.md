# Progress: Production Deployment with Celery Worker

## Summary
프로덕션 환경에 Celery 워커 추가 및 배포 문서 최신화.

## Goal & Approach
- **Goal**: `docker-compose.prod.yml`에 Celery 워커 서비스 추가 → 프로덕션 배포 준비 완료
- **Approach**: 개발 환경 설정 기반으로 프로덕션 설정 추가 → 문서 업데이트 → 로컬 검증

## Completed Steps
1. **Step 1: docker-compose.prod.yml update** ✅
   - `celery-worker` 서비스 추가 (lines 186-230)
   - 환경변수: backend와 동일 (DB, Redis, Qdrant, OpenAI)
   - Health check: `celery inspect ping` 명령 사용
   - 리소스 제한: 1GB 메모리, 0.5 CPU
2. **Step 2: Documentation update** ✅
   - `docs/DEPLOYMENT.md` 업데이트
     - 서비스 목록에 celery-worker 추가
     - 아키텍처 다이어그램에 Celery 워커 흐름 추가
     - 헬스체크 명령에 celery-worker 예시 추가

## Current Failures
_(none)_

## Decision Log
1. **Resource limits**: Celery 워커 메모리 1GB, CPU 0.5 (backend와 유사)
2. **Health check strategy**: Celery inspect 명령 사용 (30초 간격)
3. **Logging**: json-file driver, max 10MB × 3 파일 (프로덕션 표준)
4. **Command**: `celery -A backend.celery_app worker --loglevel=info` (Beat 별도 서비스 아님, 현재 scope 외)

## Next Step
프로덕션 환경 검증 완료. 실제 배포는 사용자 환경에서 `.env.prod` 설정 후 진행 권장.
