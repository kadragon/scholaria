# Plan: Analytics Data Parsing Fix

## Objective
Frontend analytics.tsx의 useCustom 응답 파싱을 검증하고, 필요 시 수정하여 올바른 데이터 렌더링 보장

## Constraints
- **현재 코드 구조 유지**: `useCustom` hook 사용법은 변경하지 않음
- **타입 안전성**: TypeScript 타입 추론 보장
- **Runtime 검증**: 실제 API 응답 구조 확인 필요

## Target Files & Changes

### 1. `frontend/src/pages/analytics.tsx`
**현재 상태 확인**:
- 라인 97-100: 데이터 파싱 로직
  ```typescript
  const summary = summaryData?.data as AnalyticsSummary | undefined;
  const topics = (topicsData?.data as TopicStats[]) || [];
  const trend = (trendData?.data as QuestionTrend[]) || [];
  const feedback = feedbackData?.data as FeedbackDistribution | undefined;
  ```

**예상 수정** (실제 응답 구조에 따라 조정):
- **케이스 1**: 현재 코드가 정확함 → 변경 불필요
- **케이스 2**: 중첩 구조 → `.data.data` 접근 필요
- **케이스 3**: 타입 단언 제거 → 타입 가드 추가

**변경 전략**:
1. Console.log 확인 (라인 95-98)
2. 실제 응답 구조에 맞춰 파싱 로직 조정
3. 타입 단언 대신 옵셔널 체이닝 강화

## Test/Validation Cases

### Unit Tests (필요 시)
- [ ] **Mock useCustom 응답 테스트**
  - Mock 데이터로 각 endpoint별 파싱 검증
  - `summaryData`, `topicsData`, `trendData`, `feedbackData` 각각

### Integration Tests
- [ ] **실제 API 응답 검증**
  - Docker 환경에서 backend 실행
  - Frontend 개발 서버 실행
  - 브라우저 개발자도구 → Network 탭에서 응답 확인
  - Console 로그로 파싱된 데이터 구조 검증

### Manual Validation
1. `docker compose up -d` (backend + DB 실행)
2. `cd frontend && npm run dev` (frontend 실행)
3. 브라우저에서 `/analytics` 접속
4. 개발자도구 → Console 탭 → 응답 구조 확인
5. 차트가 올바르게 렌더링되는지 확인

## Steps

### Step 1: 실제 API 응답 구조 확인
- [ ] Backend 실행 (`docker compose up -d`)
- [ ] Frontend 실행 (`npm run dev`)
- [ ] 브라우저에서 console.log 확인
- [ ] Network 탭에서 각 endpoint 응답 확인

### Step 2: Research 업데이트
- [ ] `RESEARCH.md`에 실제 응답 구조 기록
- [ ] 가설 검증 결과 추가

### Step 3: 파싱 로직 수정 (필요 시)
- [ ] `analytics.tsx` 97-100 라인 수정
- [ ] 타입 안전성 개선 (옵셔널 체이닝)
- [ ] Console.log 제거 또는 조건부 처리

### Step 4: 검증
- [ ] 페이지 새로고침 → 데이터 정상 렌더링 확인
- [ ] 차트 4종 (요약, 추세, 토픽, 피드백) 모두 동작 확인
- [ ] TypeScript 컴파일 에러 없음 확인

### Step 5: Cleanup
- [ ] Console.log 제거
- [ ] 불필요한 타입 단언 정리

## Rollback
- Git stash 또는 commit 직전 상태로 복원
- 변경사항이 최소화되므로 rollback 리스크 낮음

## Review Hotspots
- **analytics.tsx:97-100**: 파싱 로직 핵심 부분
- **Response 타입**: Refine `CustomResponse<T>` 구조 이해 필수

## Status
- [ ] Step 1: 실제 API 응답 구조 확인 — **BLOCKED** (사용자 실행 필요)
- [ ] Step 2: Research 업데이트
- [ ] Step 3: 파싱 로직 수정
- [ ] Step 4: 검증
- [ ] Step 5: Cleanup

## Notes
- **Refine useCustom 반환 타입**: `QueryObserverResult<CustomResponse<TData>, TError>`
- **CustomResponse 구조**: `{ data: TData }`
- **현재 코드 평가**: 타입 정의 상으로는 올바름 (`summaryData?.data`)
- **실제 검증 필요**: Runtime에서 dataProvider가 어떻게 응답을 변환하는지 확인
