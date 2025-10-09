# Research: Frontend Test Coverage Expansion

## Goal
프런트엔드 테스트 커버리지를 31.62%에서 상향 조정. 핵심 비즈니스 로직과 사용자 플로우 우선 커버.

## Scope
- 현재: 70개 테스트, 31.62% 커버리지 (25% 임계값)
- 타깃: 40~50% 커버리지 달성 (핵심 페이지 & providers)

## Related Files

### 0% Coverage (우선순위 상)
1. **Pages (비즈니스 로직)**
   - `src/pages/login.tsx` — 인증 진입점
   - `src/pages/setup.tsx` — 초기 설정
   - `src/pages/analytics.tsx` — 대시보드 (복잡)
   - `src/pages/topics/list.tsx` — 토픽 관리
   - `src/pages/contexts/list.tsx` — 컨텍스트 관리
   - `src/pages/chat/index.tsx` — 채팅 메인

2. **Components (재사용성)**
   - `src/components/Sidebar.tsx` — 네비게이션
   - `src/pages/chat/components/MessageInput.tsx` — 메시지 입력
   - `src/pages/chat/components/MessageList.tsx` — 메시지 렌더링
   - `src/pages/chat/components/TopicSelector.tsx` — 토픽 선택

3. **Providers**
   - `src/providers/dataProvider.ts` — Refine CRUD 어댑터

### Partial Coverage (우선순위 중)
- `src/lib/apiConfig.ts` (76.92%) — 환경 설정
- `src/hooks/use-toast.ts` (80.46%) — 엣지 케이스
- `src/pages/chat/components/FeedbackControls.tsx` (89.21%) — 엣지 케이스

### UI Components (우선순위 하)
- `src/components/ui/*` 대부분 0% — Radix UI 래퍼, 통합 테스트에서 검증 예정

## Hypotheses
1. **Pages 통합 테스트** 작성 시 커버리지 급상승 (현재 0% → 70%+ 예상)
2. **dataProvider** 테스트로 CRUD 안정성 확보
3. **MessageInput/MessageList** 테스트로 채팅 핵심 플로우 검증
4. UI 컴포넌트는 페이지 테스트에서 간접 검증되므로 직접 테스트는 후순위

## Evidence
- 기존 Phase 1~3에서 **hooks → components → pages** 순 진행
- Page 테스트 17개 추가 시 65개 → 82개 테스트, 커버리지 29.63% → 31.62% 소폭 상승
- **Pages가 0%**인 이유: 기존 페이지 테스트는 **통합 시나리오** 중심, 페이지 자체 렌더링은 미포함

## Assumptions/Open Questions
- **Q:** analytics.tsx (399 LOC) 테스트 범위?
  - **A:** 주요 차트 렌더링 & API 응답 처리만 검증, recharts 내부는 모의
- **Q:** 커버리지 임계값 상향 시점?
  - **A:** Phase 5 완료 후 40% 달성 시 임계값 35%로 상향

## Risks
- **act() 경고** — useChat 테스트에서 React 상태 업데이트 경고 발생. 우선순위 낮음 (기능 정상 동작).
- **JSDOM navigation** — authProvider 테스트에서 경고. 무해하나 향후 vi.mock('jsdom') 고려.

## Next
PLAN.md 작성 — Phase 5 단계별 테스트 추가 계획 수립.
