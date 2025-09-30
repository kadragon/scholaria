# Django → FastAPI 전환 진행 상황

## Summary
Django 무게감 제거를 위해 FastAPI + React Admin Panel로 전환 진행 중

## Goal & Approach
- **전환 동기**: Django 무거움 → FastAPI 경량화, 비동기 성능 개선
- **관리 UI**: React Admin Panel (React-Admin 라이브러리)
- **접근법**: 8단계 점진적 마이그레이션 (병렬 실행 → 완전 전환)

## Completed Steps
- [x] **조사 (RESEARCH.md)**
  - 현재 Django 구조 분석 (381개 테스트, 500+ 줄 Admin 커스터마이징)
  - 전환 이점/위험 평가 (성능 vs Admin 손실)
  - 관리 UI 옵션 비교 (React Admin vs 하이브리드 vs 라이브러리)
- [x] **계획 수립 (PLAN.md)**
  - 8단계 상세 계획 (12-18주)
  - React Admin Panel 구조 설계 (6.1-6.3)
  - 테스트/검증 전략, 롤백 계획

## Current Failures
없음 (아직 구현 시작 전)

## Decision Log
| 날짜 | 결정 | 근거 |
|------|------|------|
| 2025-09-30 | 전환 동기: Django 무게감 제거 | 사용자 요구사항 |
| 2025-09-30 | 관리 UI: Refine Admin Panel (Option A) | 완전한 커스터마이징, 모던 UX, Django 의존성 제거 |
| 2025-09-30 | React 라이브러리: Refine (vs React-Admin) | 헤드리스 아키텍처, FastAPI와 철학 일치, React Query 내장, UI 프레임워크 자유 선택, 비동기 친화적 |
| 2025-09-30 | ORM: SQLAlchemy 2.0 | 비동기 지원, 성숙도, Django ORM 호환 가능 |
| 2025-09-30 | UI 프레임워크: shadcn/ui (권장) 또는 Material-UI | Refine에서 선택 가능, shadcn/ui는 Tailwind 기반으로 더 가볍고 모던함 |

## Next Step
**Phase 1 시작 준비** (대기 중 - 사용자 승인 필요)
- FastAPI 기반 구조 구축
- POC: 단일 엔드포인트 전환 (GET /api/topics)
- 예상 기간: 1주 (POC) + 1주 (전체 Phase 1)
