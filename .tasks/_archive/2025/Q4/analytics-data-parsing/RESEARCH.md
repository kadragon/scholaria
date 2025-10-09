# Research: Analytics Data Parsing Fix

## Goal
Frontend analytics.tsx의 useCustom 응답 파싱을 수정하여 올바른 데이터 구조로 접근

## Scope
- `frontend/src/pages/analytics.tsx` 파일
- Refine `useCustom` hook의 응답 구조 파악
- Backend analytics API 응답 형식 확인

## Related Files
- **Frontend**: `frontend/src/pages/analytics.tsx` (라인 52, 57, 63, 75)
- **Backend**: `backend/routers/admin/analytics.py`
- **Schemas**: `backend/schemas/admin.py` (AnalyticsSummaryOut, TopicStatsOut, QuestionTrendOut, FeedbackDistributionOut)

## Hypotheses

### H1: useCustom 응답 구조 불일치
**가설**: Refine의 `useCustom` hook이 반환하는 데이터 구조가 직접 타입으로 매핑되지 않음
**근거**:
- 현재 코드: `summaryData?.data as AnalyticsSummary`
- Refine v4의 `useCustom`는 일반적으로 `{ data: { data: T } }` 형태로 래핑됨
- Backend는 직접 Pydantic 모델을 반환 (`AnalyticsSummaryOut`)

### H2: 불필요한 중첩 접근
**가설**: 현재 코드에서 `.data` 접근이 한 번 더 필요할 수 있음
**근거**:
- Backend analytics API는 직접 schema 반환:
  - `/admin/analytics/summary` → `AnalyticsSummaryOut`
  - `/admin/analytics/topics` → `list[TopicStatsOut]`
  - `/admin/analytics/questions/trend` → `list[QuestionTrendOut]`
  - `/admin/analytics/feedback/distribution` → `FeedbackDistributionOut`

## Evidence

### Backend API 응답 형식 (from analytics.py)
```python
@router.get("/summary", response_model=AnalyticsSummaryOut)
async def get_analytics_summary(...) -> AnalyticsSummaryOut:
    return AnalyticsSummaryOut(
        total_questions=total_questions,
        total_feedback=total_feedback,
        active_sessions=active_sessions,
        average_feedback_score=float(avg_feedback),
    )
```

### 현재 Frontend 파싱 (analytics.tsx:97-100)
```typescript
const summary = summaryData?.data as AnalyticsSummary | undefined;
const topics = (topicsData?.data as TopicStats[]) || [];
const trend = (trendData?.data as QuestionTrend[]) || [];
const feedback = feedbackData?.data as FeedbackDistribution | undefined;
```

### Console.log 출력 위치
- analytics.tsx:95-98에 각 응답 데이터 구조 확인용 로그 존재

## Assumptions & Open Questions

### Assumptions
1. Backend API는 정상 작동 (FastAPI response_model 기반)
2. Refine dataProvider는 올바르게 설정됨 (`@refinedev/simple-rest`)
3. JWT 인증은 정상 작동

### Open Questions
1. **실제 런타임 응답 구조**: console.log 출력으로 확인 필요
   - `summaryData` 구조가 `{ data: {...} }` 인지 `{ data: { data: {...} } }` 인지?
2. **dataProvider 변환**: `@refinedev/simple-rest`가 응답을 어떻게 변환하는지?
3. **배열 응답 처리**: `topicsData`, `trendData` 같은 배열 응답은 어떻게 래핑되는지?

## Risks
- **Low**: 데이터 구조 수정은 타입 캐스팅만 변경 (비파괴적)
- **Medium**: 실제 API 응답을 확인하지 않고 추측하면 런타임 에러 가능

## Sub-agent Findings

### Refine useCustom 반환 구조 분석
**타입 정의 확인** (`@refinedev/core@4.58.0`):
- `useCustom` 반환: `QueryObserverResult<CustomResponse<TData>, TError>`
- `CustomResponse<TData>`: `{ data: TData }`
- 따라서 `useCustom<T>()`의 결과에서 `.data`로 접근하면 `CustomResponse<T>` 타입
- 최종 데이터는 `.data.data` 형태가 아니라 `.data`로 접근 ✅

**simple-rest dataProvider 구현 확인**:
- `custom` 메서드: `axios 응답.data`를 추출 → `{ data: ... }` 반환
- 예: Backend가 `{"total_questions": 10}`을 반환하면
  - axios 응답: `response.data = {"total_questions": 10}`
  - dataProvider 반환: `{ data: {"total_questions": 10} }`
  - useCustom 결과: `summaryData.data = {"total_questions": 10}`

**현재 코드 평가**:
```typescript
const summary = summaryData?.data as AnalyticsSummary | undefined;
```
→ **타입 정의상 정확함** ✅

## Next
**Hard Gate**: 실제 API 응답 구조 확인 필요 (사용자 실행)
1. Backend 실행 (`docker compose up -d`)
2. Frontend 실행 (`cd frontend && npm run dev`)
3. 브라우저에서 `/analytics` 접속 → Console 로그 확인
4. 응답 구조가 예상과 다르면 **PLAN Step 3** 진행
5. 응답 구조가 일치하면 **타입 안전성 개선만** 진행
