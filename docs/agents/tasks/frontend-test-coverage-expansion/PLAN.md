# Plan: Frontend Test Coverage Expansion

## Objective
프런트엔드 테스트 커버리지를 31.62%에서 40~50%로 상향. 핵심 providers → 공용 컴포넌트 → 페이지 순으로 TDD 진행.

## Constraints
- **TDD 필수**: Red → Green → Refactor
- **현재 임계값 25%** 유지, Phase 5 완료 후 35% 상향
- **통합 테스트 중심**: Refine 훅(`useLogin`, `useLogout`, `useTable` 등) 모의 필수
- **기존 MSW 핸들러 재사용**: `/handlers` 확장

## Target Files & Changes

### Step 1: dataProvider 단위 테스트
- **파일**: `src/providers/dataProvider.ts`
- **현재**: 0% → **목표**: 90%+
- **변경**: `src/providers/__tests__/dataProvider.test.ts` 생성
- **테스트 케이스**:
  1. Request 인터셉터 — 토큰 Authorization 헤더 추가 검증
  2. Response 인터셉터 — 401 시 토큰 제거 & 리다이렉션
  3. `getList` 변환 로직 — `{ data: [], total: N }` 구조 처리
  4. `getList` 변환 로직 — 배열 직접 반환 처리

### Step 2: Sidebar 컴포넌트 테스트
- **파일**: `src/components/Sidebar.tsx`
- **현재**: 0% → **목표**: 80%+
- **변경**: `src/components/__tests__/Sidebar.test.tsx` 생성
- **테스트 케이스**:
  1. 메뉴 항목 렌더링 (토픽, 컨텍스트, 분석)
  2. 활성 경로 스타일 적용 (`/admin/topics` 진입 시)
  3. 로그아웃 버튼 클릭 → `useLogout` 호출 검증

### Step 3: LoginPage 통합 테스트
- **파일**: `src/pages/login.tsx`
- **현재**: 0% → **목표**: 75%+
- **변경**: `src/pages/__tests__/login.test.tsx` 생성
- **테스트 케이스**:
  1. 초기 렌더링 — 이메일/비밀번호 입력 필드 표시
  2. Setup 체크 — `needs_setup: true` 시 `/admin/setup` 리다이렉션
  3. 로그인 성공 — `useLogin` 호출 & 토스트 미표시
  4. 로그인 실패 — 에러 토스트 표시

### Step 4: MessageInput 컴포넌트 테스트
- **파일**: `src/pages/chat/components/MessageInput.tsx`
- **현재**: 0% → **목표**: 85%+
- **변경**: `src/pages/chat/components/__tests__/MessageInput.test.tsx` 생성
- **테스트 케이스**:
  1. 텍스트 입력 & 전송 버튼 활성화
  2. Enter 키 전송 (Shift+Enter는 개행)
  3. 전송 후 입력란 초기화
  4. `isStreaming` 시 전송 버튼 비활성화

### Step 5: 커버리지 검증 & 임계값 상향
- **변경**: `frontend/vitest.config.ts`
- **테스트**: `npm run test:coverage` 실행
- **검증**: 전체 커버리지 40% 이상 달성 확인
- **임계값**: `lines: 35, functions: 35, branches: 35, statements: 35`로 상향

## Test/Validation Cases
- 각 Step 완료 시 `npm run test:coverage` 실행
- 신규 테스트 개별 실행 (`npm run test -- <file-name>`)
- 린트/타입체크 통과 (`npm run lint && npm run typecheck`)

## Steps
1. [ ] Step 1: dataProvider 단위 테스트 (4 tests)
2. [ ] Step 2: Sidebar 컴포넌트 테스트 (3 tests)
3. [ ] Step 3: LoginPage 통합 테스트 (4 tests)
4. [ ] Step 4: MessageInput 컴포넌트 테스트 (4 tests)
5. [ ] Step 5: 커버리지 검증 & 임계값 35% 상향
6. [ ] TASKS.md 업데이트 (Phase 5 완료 기록)

## Rollback
- 각 Step은 독립된 테스트 파일 추가. 실패 시 해당 파일만 삭제.
- 임계값 상향 실패 시 `vitest.config.ts` 원복.

## Review Hotspots
- **dataProvider**: MSW 핸들러가 Refine 요청 형식 (`_start`, `_end`, `_sort`) 처리하는지 확인
- **LoginPage**: `checkSetupStatus` useEffect 의존성 경고 없는지 검토
- **MessageInput**: 키보드 이벤트 (`Enter`, `Shift+Enter`) 모의 정확도 확인

## Status
- [x] Step 1: dataProvider 단위 테스트 — 4 tests added
- [x] Step 2: Sidebar 컴포넌트 테스트 — 3 tests added
- [x] Step 3: LoginPage 통합 테스트 — 4 tests added
- [x] Step 4: MessageInput 컴포넌트 테스트 — 5 tests added
- [x] Step 5: 커버리지 검증 & 임계값 상향 — 40.91% achieved, 35% threshold set
- [x] TASKS.md 업데이트 — Phase 5 완료 기록

## Phase 6 Steps (40.91% → 50%+)

### Step 6: SetupPage 통합 테스트
- **파일**: `src/pages/setup.tsx`
- **현재**: 0% → **목표**: 75%+
- **변경**: `src/pages/__tests__/setup.test.tsx` 생성
- **테스트 케이스**:
  1. 초기 렌더링 — 사용자명/이메일/비밀번호 입력 필드 표시
  2. Setup 체크 — `needs_setup: false` 시 `/login` 리다이렉션
  3. 비밀번호 불일치 검증 — 에러 메시지 표시
  4. 비밀번호 길이 검증 — 8자 미만 시 에러
  5. 계정 생성 성공 — POST `/api/setup/init` 호출 & 토스트 & `/login` 이동
  6. 계정 생성 실패 — 에러 메시지 표시

### Step 7: useCommandPalette 훅 테스트
- **파일**: `src/hooks/useCommandPalette.tsx`
- **현재**: 0% → **목표**: 90%+
- **변경**: `src/hooks/__tests__/useCommandPalette.test.tsx` 생성
- **테스트 케이스**:
  1. Cmd+K (Mac) / Ctrl+K (Windows) 키 이벤트로 팔레트 토글
  2. navigate 함수 호출 검증
  3. 초기 open 상태 false 검증

### Step 8: TopicSelector 컴포넌트 테스트
- **파일**: `src/pages/chat/components/TopicSelector.tsx`
- **현재**: 0% → **목표**: 80%+
- **변경**: `src/pages/chat/components/__tests__/TopicSelector.test.tsx` 생성
- **테스트 케이스**:
  1. 토픽 목록 렌더링 (useList 모의)
  2. 토픽 선택 시 onTopicSelect 콜백 호출
  3. 로딩 상태 표시

### Step 9: MessageList 컴포넌트 테스트
- **파일**: `src/pages/chat/components/MessageList.tsx`
- **현재**: 0% → **목표**: 70%+ (복잡한 Markdown 렌더링 포함)
- **변경**: `src/pages/chat/components/__tests__/MessageList.test.tsx` 생성
- **테스트 케이스**:
  1. 사용자/어시스턴트 메시지 렌더링
  2. Markdown 렌더링 (헤더, 리스트, 코드 블록)
  3. Citations 확장/축소 토글
  4. FeedbackControls 통합 (historyId 있을 때)
  5. 스트리밍 중 로딩 인디케이터 표시
  6. 자동 스크롤 (scrollIntoView 모의)

### Step 10: AnalyticsSkeleton 컴포넌트 테스트
- **파일**: `src/components/AnalyticsSkeleton.tsx`
- **현재**: 0% → **목표**: 80%+
- **변경**: `src/components/__tests__/AnalyticsSkeleton.test.tsx` 생성
- **테스트 케이스**:
  1. 스켈레톤 렌더링 검증 (Skeleton 컴포넌트 사용)
  2. 카드 레이아웃 구조 검증

### Step 11: 커버리지 검증 & 임계값 상향 검토
- **변경**: `frontend/vitest.config.ts`
- **테스트**: `npm run test:coverage` 실행
- **검증**: 전체 커버리지 51.29% 달성
- **임계값**: 45%로 상향 완료

## Phase 6 Status
- [x] Step 6: SetupPage 통합 테스트 — 6 tests added
- [x] Step 7: useCommandPalette 훅 테스트 — 3 tests added
- [x] Step 8: TopicSelector 컴포넌트 테스트 — 3 tests added
- [x] Step 9: MessageList 컴포넌트 테스트 — 6 tests added
- [x] Step 10: AnalyticsSkeleton 컴포넌트 테스트 — 2 tests added
- [x] Step 11: 커버리지 검증 & 임계값 45% 상향 — 51.29% achieved, 106 tests passing
- [x] TASKS.md 업데이트 — Phase 6 완료 기록
