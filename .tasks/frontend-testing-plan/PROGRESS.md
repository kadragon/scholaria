# Progress: Frontend Testing Plan

## Summary

프런트엔드 테스트 인프라 도입 — Vitest + RTL + MSW 기반으로 Phase 0(인프라) → Phase 1(유틸/훅) → Phase 2(컴포넌트) → Phase 3(페이지) → Phase 4(커버리지 70%) 순차 진행.

## Goal & Approach

- **Goal**: 핵심 로직에 70% 커버리지 확보, 회귀 방지
- **Approach**: TDD Red→Green→Refactor, [Structural]/[Behavioral] 커밋 분리

## Completed Steps

- ✅ Research 완료 (기존 구조, 의존성, 테스트 대상 분석)
- ✅ Plan 작성 (Phase 0–4 단계별 타깃 파일, 테스트 케이스, 검증 방법)
- ✅ Phase 0 완료 — 테스트 인프라 도입 (커밋 63f3aa1)
  - Vitest 2.1.9, RTL 16.3.0, MSW 2.11.4, jsdom 25.0.1 설치
  - vitest.config.ts 작성 (jsdom, coverage-v8, setupFiles)
  - setupTests.ts 작성 (MSW 서버 lifecycle)
  - MSW 핸들러 보일러플레이트 (auth, topics, contexts)
  - package.json scripts: test, test:watch, test:ui, test:coverage
- ✅ Phase 1 완료 — 유틸/훅 단위 테스트 (커밋 4be3fc9)
  - apiClient.test.ts: 토큰 인터셉터, 401 리다이렉트 (5 tests)
  - authProvider.test.ts: 로그인/로그아웃/check/getIdentity/onError (11 tests)
  - useChat.test.ts: SSE 스트리밍, 에러 처리, 메시지 버퍼 (8 tests)
  - **버그 수정**: useChat.ts axios → fetch (브라우저 SSE 지원)
  - **버그 수정**: useChat.ts error event 전파 (inner try-catch 분리)
  - 총 24개 테스트 통과

## Current Failures

없음

## Decision Log

1. **axios → fetch 전환**: axios의 `responseType: "stream"`은 Node.js 전용. 브라우저에서 SSE를 처리하려면 fetch + ReadableStream 필요 → TDD 과정에서 실제 코드 버그 발견 및 수정
2. **에러 이벤트 전파**: 기존 코드는 `event.type === "error"` 시 내부 try-catch에 잡혀 `onError` 콜백이 호출되지 않음 → JSON 파싱과 이벤트 처리 try-catch 분리

## Next Step

**Phase 2 — Step 11**: InlineEditCell.test.tsx 작성 (TDD: Red → Green → Refactor)
