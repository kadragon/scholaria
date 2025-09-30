# Refine Admin Panel — Progress

## Summary
Django Admin → Refine + FastAPI Admin API 전환 (Phase 6.1 시작)

## Goal & Approach
- **Phase 6.1**: FastAPI Admin API 구현 (CRUD, 대량 작업, 파일 업로드)
- **TDD**: 각 Admin API 테스트 우선 작성
- **Refine 규약**: `{ data, total }` 형식, REST API 표준 준수

## Completed Steps
없음 (태스크 시작)

## Current Failures
없음

## Decision Log
| 날짜 | 결정 | 근거 |
|------|------|------|
| 2025-10-01 | Admin API 별도 라우터 (`/api/admin`) | 권한 분리 명확, 일반 API와 독립적 버전 관리 |
| 2025-10-01 | REST Data Provider (Refine) | FastAPI 완벽 호환, 단순성 우선 |
| 2025-10-01 | SSE (처리 상태 스트리밍) | 실시간 업데이트 + 단순성, 단방향만 필요 |
| 2025-10-01 | Celery 유지 (PDF 처리) | FastAPI에서 Django signal 제한, 기존 인프라 재사용 |

## Next Step
**Step 1: Admin 라우터 기반 구조** (1일)
- `api/routers/admin/` 폴더 생성
- Topics/Contexts Admin 라우터 파일 생성
- `require_admin` 의존성 적용 확인
