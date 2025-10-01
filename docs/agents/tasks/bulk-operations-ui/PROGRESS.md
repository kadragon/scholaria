# Progress: Bulk Operations UI

## Summary
Refine Admin Panel에 bulk operations UI 구현 완료

## Goal & Approach
Topics/Contexts 목록에 checkbox 선택 + bulk actions (assign to topic, regenerate embeddings, update system prompt) 추가

## Completed Steps
- Step 1: shadcn/ui Checkbox, Toast 컴포넌트 추가
- Step 2-4: Contexts 목록 구현
  - Checkbox 선택 기능 (개별 + 전체 선택)
  - "Assign to Topic" bulk action (Dialog + API 호출)
  - "Regenerate Embeddings" bulk action (API 호출 + toast notification)
- Step 5: Topics 목록 구현
  - Checkbox 선택 기능
  - "Update System Prompt" bulk action (Dialog + Tabs for KR/EN)
- Step 6: 타입 체크 및 린트 통과

## Current Failures / Blockers
없음 (수동 UI 테스트 대기 중)

## Decision Log
- Toast 컴포넌트를 App.tsx Layout에 추가하여 전역 사용
- API 호출 시 localStorage에서 직접 token 가져오기 (Refine useCustomMutation 대신 fetch 사용)
- Tabs 컴포넌트를 사용하여 한/영 시스템 프롬프트 입력 구분 (UX 개선)

## Next Step
수동 테스트 (브라우저에서 확인) 후 커밋
