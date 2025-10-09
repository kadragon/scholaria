# Plan: Frontend Testing Plan

## Objective

Vitest + React Testing Library + MSW 기반 테스트 인프라를 도입하고, 핵심 유틸/훅/컴포넌트/페이지에 70% 커버리지를 확보합니다.

## Constraints

- **TDD 필수**: Red → Green → Refactor
- **커밋 분리**: [Structural] (인프라, 설정) / [Behavioral] (테스트 + 코드)
- **main 직접 커밋 금지**: PR 필수
- **CI 통과 필수**: 모든 테스트 Green + 린트/타입체크
- **스냅샷 금지**: 명시적 어서션만 사용

## Target Files & Changes

### Phase 0 — 테스트 인프라 도입

#### 신규 파일
- `frontend/vitest.config.ts` — Vitest 설정 (jsdom, coverage, setupFiles)
- `frontend/src/setupTests.ts` — MSW worker, Refine mock, global cleanup
- `frontend/src/__mocks__/msw/handlers.ts` — MSW 요청 핸들러
- `frontend/src/__mocks__/msw/server.ts` — MSW 서버 인스턴스
- `frontend/src/__mocks__/refine.ts` — Refine 훅 모킹

#### 수정 파일
- `frontend/package.json` — devDependencies 추가, scripts 추가
- `.github/workflows/*.yml` — 프런트엔드 테스트 잡 추가 (해당 파일이 있다면)

### Phase 1 — 유틸/훅 단위 테스트

#### 신규 파일
- `frontend/src/lib/__tests__/apiClient.test.ts` — 토큰 인터셉터, 401 리다이렉트
- `frontend/src/providers/__tests__/authProvider.test.ts` — 로그인/로그아웃/check/onError
- `frontend/src/pages/chat/hooks/__tests__/useChat.test.ts` — SSE 스트리밍, 에러 처리

### Phase 2 — 공용 컴포넌트 상호작용 테스트

#### 신규 파일
- `frontend/src/components/__tests__/InlineEditCell.test.tsx` — 키보드 이벤트, blur 저장
- `frontend/src/components/__tests__/CommandPalette.test.tsx` — 검색, 네비게이션
- `frontend/src/hooks/__tests__/use-toast.test.ts` — 토스트 호출 확인

### Phase 3 — 페이지 시나리오 테스트

#### 신규 파일
- `frontend/src/pages/__tests__/login.test.tsx` — 로그인 폼 제출, 에러 처리
- `frontend/src/pages/__tests__/setup.test.tsx` — 초기 설정 흐름
- `frontend/src/pages/topics/__tests__/list.test.tsx` — 필터링, 테이블 렌더링
- `frontend/src/pages/contexts/__tests__/list.test.tsx` — 타입별 필터, 일괄 삭제
- `frontend/src/pages/chat/__tests__/index.test.tsx` — 토픽 선택, 메시지 스트리밍

### Phase 4 — 커버리지/회귀 가드

#### 수정 파일
- `frontend/vitest.config.ts` — coverage threshold 70% 설정
- `.github/pull_request_template.md` (신규 or 수정) — 프런트엔드 테스트 체크 추가

## Test & Validation Cases

### Phase 0
- [ ] `npm run test` 실행 → Vitest 구동 확인
- [ ] `npm run test:watch` → watch 모드 확인
- [ ] `npm run test:coverage` → 커버리지 리포트 생성 (빈 상태)
- [ ] MSW 핸들러 로드 확인 (`setupTests.ts` import 에러 없음)

### Phase 1
- [ ] `apiClient.test.ts`: 토큰 헤더 첨부, 401 응답 시 localStorage 클리어 + location.href 변경
- [ ] `authProvider.test.ts`: 로그인 성공(토큰 저장), 실패(에러 반환), 로그아웃(토큰 제거), check(토큰 여부), onError(401/403 → logout)
- [ ] `useChat.test.ts`: SSE 스트림 파싱(`answer_chunk`, `citations`, `done`, `error`), 메시지 버퍼 초기화, 에러 핸들링

### Phase 2
- [ ] `InlineEditCell.test.tsx`: 더블클릭 → Input 렌더, Enter → onSave 호출, Escape → 취소, blur → onSave
- [ ] `CommandPalette.test.tsx`: 검색 입력, 항목 선택 → navigate 호출 확인
- [ ] `use-toast.test.ts`: toast() 호출 → 토스트 메시지 렌더

### Phase 3
- [ ] `login.test.tsx`: 폼 제출 → authProvider.login 호출, 실패 시 에러 메시지 표시
- [ ] `setup.test.tsx`: 단계별 폼 제출 → 데이터 저장 확인
- [ ] `topics/list.test.tsx`: Refine useTable 모킹 → 테이블 렌더, 필터링
- [ ] `contexts/list.test.tsx`: 타입 필터, 일괄 삭제 버튼 → API 호출 확인
- [ ] `chat/index.test.tsx`: 토픽 선택 → useChat 호출, 메시지 전송 → 스트리밍

### Phase 4
- [ ] `vitest.config.ts`에 `coverage.lines: 70, coverage.branches: 70` 설정
- [ ] `npm run test:coverage` 실행 → 70% 미만 시 실패 확인
- [ ] PR 템플릿에 "- [ ] 프런트엔드 테스트 통과 (`npm run test`)" 항목 추가

## Steps

### Phase 0 (인프라)
1. **[Structural]** Vitest/RTL/MSW 의존성 설치, `package.json` scripts 추가
2. **[Structural]** `vitest.config.ts` 작성 (jsdom, coverage, setupFiles)
3. **[Structural]** `setupTests.ts` 작성 (MSW worker, Refine mock, cleanup)
4. **[Structural]** MSW 핸들러/서버 보일러플레이트 작성
5. **[Structural]** GitHub Actions 워크플로 수정 (프런트엔드 테스트 잡 추가)
6. 검증: `npm run test` 실행 → 0 tests (정상)

### Phase 1 (유틸/훅)
7. **[Behavioral]** `apiClient.test.ts` 작성 (TDD: Red → Green → Refactor)
8. **[Behavioral]** `authProvider.test.ts` 작성 (TDD)
9. **[Behavioral]** `useChat.test.ts` 작성 (TDD, MSW SSE 모킹)
10. 검증: Phase 1 테스트 모두 통과

### Phase 2 (컴포넌트)
11. **[Behavioral]** `InlineEditCell.test.tsx` 작성 (TDD)
12. **[Behavioral]** `CommandPalette.test.tsx` 작성 (TDD, React Router 모킹)
13. **[Behavioral]** `use-toast.test.ts` 작성 (TDD)
14. 검증: Phase 2 테스트 모두 통과

### Phase 3 (페이지)
15. **[Behavioral]** `login.test.tsx` 작성 (TDD, Refine 훅 모킹)
16. **[Behavioral]** `setup.test.tsx` 작성 (TDD)
17. **[Behavioral]** `topics/list.test.tsx` 작성 (TDD)
18. **[Behavioral]** `contexts/list.test.tsx` 작성 (TDD)
19. **[Behavioral]** `chat/index.test.tsx` 작성 (TDD)
20. 검증: Phase 3 테스트 모두 통과

### Phase 4 (커버리지)
21. **[Structural]** `vitest.config.ts`에 coverage threshold 70% 설정
22. **[Structural]** PR 템플릿 추가/수정
23. 검증: `npm run test:coverage` → 70% 달성 확인, 미달 시 추가 테스트 작성
24. CI 통과 확인

## Rollback

- Phase 0 실패 시: 의존성 제거, `vitest.config.ts` 삭제 → 기존 상태 복원
- Phase 1–3 실패 시: 해당 테스트 파일 삭제, 커밋 되돌리기
- Phase 4 실패 시: coverage threshold 낮추기 또는 제거

## Review Hotspots

1. **MSW SSE 모킹**: `useChat.test.ts`에서 ReadableStream 재현 로직 — SSE 파싱 정확성 확인
2. **Refine 훅 모킹**: `login.test.tsx`, `topics/list.test.tsx` — 최소 모킹으로 페이지 렌더 가능한지 확인
3. **Coverage threshold**: 70% 달성 가능 여부 — 실제 커버리지에 따라 조정 필요
4. **CI 통합**: GitHub Actions 워크플로 수정 — 기존 백엔드 테스트와 병렬 실행 확인

## Status

- [x] Phase 0 — Step 1: Vitest/RTL/MSW 의존성 설치
- [x] Phase 0 — Step 2: vitest.config.ts 작성
- [x] Phase 0 — Step 3: setupTests.ts 작성
- [x] Phase 0 — Step 4: MSW 핸들러/서버 보일러플레이트
- [x] Phase 0 — Step 5: GitHub Actions 워크플로 수정 (생략 — 워크플로 부재)
- [x] Phase 0 — Step 6: 검증 (npm run test)
- [x] Phase 1 — Step 7: apiClient.test.ts
- [x] Phase 1 — Step 8: authProvider.test.ts
- [x] Phase 1 — Step 9: useChat.test.ts
- [x] Phase 1 — Step 10: 검증 (24 tests passing)
- [ ] Phase 2 — Step 11: InlineEditCell.test.tsx
- [ ] Phase 2 — Step 12: CommandPalette.test.tsx
- [ ] Phase 2 — Step 13: use-toast.test.ts
- [ ] Phase 2 — Step 14: 검증
- [ ] Phase 3 — Step 15: login.test.tsx
- [ ] Phase 3 — Step 16: setup.test.tsx
- [ ] Phase 3 — Step 17: topics/list.test.tsx
- [ ] Phase 3 — Step 18: contexts/list.test.tsx
- [ ] Phase 3 — Step 19: chat/index.test.tsx
- [ ] Phase 3 — Step 20: 검증
- [ ] Phase 4 — Step 21: coverage threshold 70% 설정
- [ ] Phase 4 — Step 22: PR 템플릿 추가/수정
- [ ] Phase 4 — Step 23: 검증 (npm run test:coverage)
- [ ] Phase 4 — Step 24: CI 통과 확인
