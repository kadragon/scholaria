# Analytics Dashboard - Progress

## Summary
분석 대시보드 구현 시작 - TDD 방식으로 백엔드 API부터 개발

## Goal & Approach
1. 백엔드: Analytics API 라우터 + 스키마 (TDD)
2. 프론트엔드: Recharts 기반 대시보드 UI
3. 테스트: 집계 로직, 권한, 엣지 케이스 검증

## Completed Steps
- [x] RESEARCH.md 작성 - 모델 분석, API 설계, 가정
- [x] PLAN.md 작성 - 9단계 상세 계획, 테스트 케이스
- [x] Step 1 [Structural]: Analytics 스키마 4개 추가 (backend/schemas/admin.py:132-165)
- [x] Step 2 [Behavioral]: Analytics 라우터 4개 엔드포인트 구현 (backend/routers/admin/analytics.py)
- [x] Step 3 [Structural]: 라우터 등록 (backend/routers/admin/__init__.py, backend/main.py:13,42)
- [x] Step 4 [Behavioral]: 테스트 6개 작성 및 통과 (backend/tests/admin/test_analytics.py, 6 passed)
- [x] Step 5 [Structural]: recharts 설치 (frontend/package.json:27)
- [x] Step 6 [Behavioral]: 대시보드 페이지 구현 (frontend/src/pages/analytics.tsx)
- [x] Step 7 [Structural]: 라우트 추가 (frontend/src/App.tsx:13,91)

## Current Failures
- 기존 테스트 3개 실패 (test_admin_contexts.py) - 이는 기존 문제로, analytics 태스크와 무관

## Decision Log
1. **차트 라이브러리**: Recharts 선택 (React 표준, shadcn/ui 호환)
2. **집계 방식**: 요청 시 계산 (초기), 추후 Redis 캐시/Celery 스케줄링으로 개선 가능
3. **시간 범위**: 기본 7일, 필터 옵션 (1/30/90일)
4. **권한**: `require_admin` 의존성 사용 (is_staff 체크)
5. **테스트 픽스처**: `db_session` 사용 (conftest.py 공용 픽스처)
6. **User 패스워드**: `pwd_context.hash()` 사용 (set_password 메서드 없음)

## Next Step
**Step 8 [Behavioral]**: 통합 테스트 - 프론트엔드에서 API 호출 확인 (수동 검증)
