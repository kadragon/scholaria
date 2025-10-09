# Analytics Dashboard - Plan

## Objective
분석 대시보드 구현: 사용량 통계, 피드백 분포, 토픽별 활동, 컨텍스트 사용 현황 제공

## Constraints
- **TDD**: 테스트 먼저 작성 (집계 로직, API 응답 검증)
- **Admin 전용**: `require_admin` 의존성 사용
- **성능**: 인덱스 활용 (created_at, topic_id, session_id 기존 인덱스)
- **차트 라이브러리**: Recharts (React 생태계 표준, shadcn/ui 호환)

## Target Files & Changes

### 백엔드 (신규)
1. **`backend/schemas/admin.py`** - Analytics 스키마 추가
   - `AnalyticsSummaryOut`: 전체 요약 (총 질문 수, 총 피드백, 활성 세션 수)
   - `TopicStatsOut`: 토픽별 통계 (질문 수, 평균 피드백)
   - `OpenAIUsageOut`: OpenAI API 사용량 (선택적, 나중에 추가 가능)
   - `QuestionTrendOut`: 시계열 데이터 (일자별 질문 수)

2. **`backend/routers/admin/analytics.py`** - Analytics 라우터 (신규)
   - `GET /admin/analytics/summary` - 전체 요약
   - `GET /admin/analytics/topics` - 토픽별 통계
   - `GET /admin/analytics/questions/trend?days=7` - 질문 추세 (기간별)
   - `GET /admin/analytics/feedback/distribution` - 피드백 점수 분포
   - `GET /admin/analytics/feedback/comments?topic_id=&limit=` - 최신 피드백 코멘트

3. **`backend/routers/admin/__init__.py`** - analytics_router export

4. **`backend/main.py`** - `/admin/analytics` 라우터 등록

### 백엔드 (테스트)
5. **`backend/tests/admin/test_analytics.py`** - 유닛 테스트
   - 각 엔드포인트 응답 검증
   - 빈 데이터 케이스
   - 날짜 범위 필터링
   - Admin 권한 체크

### 프론트엔드 (신규)
6. **`frontend/package.json`** - recharts 의존성 추가

7. **`frontend/src/pages/analytics.tsx`** - Analytics 대시보드 페이지
   - 전체 요약 카드 (총 질문, 피드백, 세션)
   - 질문 추세 차트 (Line Chart)
   - 토픽별 활동 차트 (Bar Chart)
   - 피드백 분포 차트 (Pie Chart)
   - 최신 피드백 코멘트 리스트 + 토픽 필터, 로딩 상태

8. **`frontend/src/App.tsx`** - `/analytics` 라우트 추가

## Test/Validation Cases

### Backend Tests
- `test_analytics_summary_empty_data` - 데이터 없을 때 기본값 반환
- `test_analytics_summary_with_data` - QuestionHistory 있을 때 집계 검증
- `test_analytics_topics_stats` - 토픽별 질문 수, 평균 피드백 검증
- `test_analytics_questions_trend_7days` - 7일간 일자별 집계
- `test_analytics_feedback_distribution` - 피드백 점수 분포 (positive/negative/neutral)
- `test_feedback_comments_empty` - 피드백 코멘트가 없을 때 빈 배열 반환
- `test_feedback_comments_with_data` - 토픽 필터/정렬/제한 검증
- `test_analytics_require_admin` - 비관리자 접근 시 403

### Frontend Validation
- 대시보드 페이지 렌더링
- 차트 데이터 바인딩 (Recharts 컴포넌트)
- 빈 데이터 시 placeholder 메시지
- 날짜 범위 필터 (7일/30일 선택)
- 피드백 코멘트 리스트 로딩/필터링 동작

## Steps

### Backend (TDD)
1. [ ] **[Structural]** Schemas: `backend/schemas/admin.py`에 Analytics 스키마 추가
2. [ ] **[Behavioral]** Router: `backend/routers/admin/analytics.py` 생성 + 5개 엔드포인트
3. [ ] **[Structural]** Register: `backend/routers/admin/__init__.py`, `backend/main.py` 라우터 등록
4. [ ] **[Behavioral]** Tests: `backend/tests/admin/test_analytics.py` 8개 테스트 작성 + 검증

### Frontend
5. [ ] **[Structural]** Dependencies: recharts 설치 (`pnpm add recharts`)
6. [ ] **[Behavioral]** Page: `frontend/src/pages/analytics.tsx` 대시보드 UI 구현
7. [ ] **[Structural]** Routing: `frontend/src/App.tsx` 라우트 추가

### Validation
8. [ ] **[Behavioral]** Integration: 프론트엔드에서 API 호출 확인, 차트 렌더링 확인
9. [ ] **[Behavioral]** Quality: `uv run ruff check . && uv run mypy . && uv run pytest`

## Rollback
- Git commit 단위로 복원 (Structural/Behavioral 분리)
- 신규 파일만 추가 (기존 코드 수정 없음)

## Review Hotspots
- SQLAlchemy 집계 쿼리 (func.count, func.avg, group_by)
- 날짜 범위 필터링 (created_at >= cutoff_date)
- 피드백 점수 범주화 (양수/0/음수)
- Recharts 데이터 형식 (배열 객체, key-value)

## Status
- [x] Step 1: Schemas 추가
- [x] Step 2: Router 생성
- [x] Step 3: Register routers
- [x] Step 4: Tests 작성 (6/6 passed)
- [x] Step 5: Dependencies (recharts)
- [x] Step 6: Frontend page
- [x] Step 7: Routing
- [x] Step 8: Integration check (수동 검증 필요)
- [x] Step 9: Quality checks (ruff + mypy 통과, analytics 테스트 통과)
