# Django → FastAPI 전환 - 작업 요약

## Goal
Django 무게감 제거를 위한 FastAPI + React Admin Panel 전환

## Key Changes
- **조사**: 현재 Django 구조 분석 (381개 테스트, 500+ 줄 Admin)
- **계획**: 8단계 점진적 마이그레이션 (12-18주)
  - Phase 1-5: API 전환 (FastAPI, SQLAlchemy, JWT)
  - Phase 6: React Admin Panel (React-Admin, Material-UI)
  - Phase 7-8: 프론트엔드 분리 + Django 제거

## Key Decisions
1. **전환 동기**: Django 무거움 → FastAPI 경량화
2. **관리 UI**: Refine Admin Panel (완전한 커스터마이징)
3. **React 라이브러리**: Refine (헤드리스, FastAPI와 철학 일치, React Query 내장)
4. **UI 프레임워크**: shadcn/ui (권장) 또는 Material-UI
5. **예상 기간**: 12-18주 (Critical: Phase 6 = 4-6주)

## Tests
- 기존 381개 테스트 → FastAPI TestClient로 포팅
- React Admin: E2E 테스트 (Playwright)
- 각 Phase 완료 시 통합 테스트

## Documents
- `RESEARCH.md`: 전환 타당성 분석, 이점/위험 평가
- `PLAN.md`: 8단계 상세 계획, 파일 변경 목록, 롤백 전략
- `PROGRESS.md`: 진행 상황 추적, 결정 로그

## Next Step
Phase 1 시작 대기 (POC: GET /api/topics 전환)
