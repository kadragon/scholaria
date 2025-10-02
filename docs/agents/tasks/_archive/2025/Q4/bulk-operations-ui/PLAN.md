# Plan: Bulk Operations UI

## Objective
Refine Admin Panel의 Topics/Contexts 목록에 bulk operations UI 추가

## Constraints
- TDD: 각 기능에 대한 테스트 먼저 작성 (단, UI 테스트는 E2E 도구 없으므로 수동 테스트)
- 기존 shadcn/ui 컴포넌트 재사용
- Refine 패턴 준수

## Target Files & Changes
- `admin-frontend/src/pages/contexts/list.tsx`: checkbox 선택 + bulk actions 버튼
- `admin-frontend/src/pages/topics/list.tsx`: checkbox 선택 + bulk update system prompt
- `admin-frontend/src/components/ui/`: Toast 컴포넌트 추가 (필요 시)
- `admin-frontend/src/providers/dataProvider.ts`: bulk operations API 호출 추가

## Test / Validation Cases
- UI 테스트는 수동 검증 (브라우저에서 확인)
- API 호출 검증: Network 탭에서 올바른 요청 확인
- 성공/에러 시나리오 테스트

## Steps
- [ ] Step 1: shadcn/ui Checkbox, Toast 컴포넌트 추가
- [ ] Step 2: Contexts 목록에 선택 기능 추가 (checkbox)
- [ ] Step 3: "Assign to Topic" bulk action 구현
- [ ] Step 4: "Regenerate Embeddings" bulk action 구현
- [ ] Step 5: Topics 목록에 "Update System Prompt" bulk action 구현
- [ ] Step 6: 수동 테스트 및 검증

## Rollback Strategy
- Git revert로 변경사항 롤백
- 개별 컴포넌트 단위로 커밋하여 부분 롤백 가능

## Review Hotspots
- Refine useTable과 checkbox 통합 방식
- API 에러 처리 및 사용자 피드백
- UX: 선택된 항목 수 표시, 전체 선택/해제

## Status
- [x] Step 1: UI 컴포넌트 추가 (Checkbox, Toast)
- [x] Step 2: Contexts 선택 기능
- [x] Step 3: Assign to Topic
- [x] Step 4: Regenerate Embeddings
- [x] Step 5: Update System Prompt
- [x] Step 6: 타입 체크 및 린트 통과 (수동 UI 테스트는 사용자가 수행)
