# Research: Frontend Testing Plan

## Goal

Vitest + React Testing Library + MSW 기반 테스트 인프라를 도입하고 핵심 유틸/훅/컴포넌트/페이지에 70% 커버리지를 확보합니다.

## Scope

- **Phase 0**: 테스트 인프라 (Vitest, RTL, MSW, scripts, CI)
- **Phase 1**: 유틸/훅 단위 테스트 (`apiClient`, `authProvider`, `useChat`)
- **Phase 2**: 공용 컴포넌트 상호작용 테스트 (`InlineEditCell`, `CommandPalette`, UI 토글, 토스트)
- **Phase 3**: 페이지 시나리오 테스트 (login, setup, topics, contexts, chat)
- **Phase 4**: 커버리지 70% 기준 설정, 회귀 가드, PR 템플릿 추가

## Related Files & Flows

### 현재 상태
- **프론트엔드**: Vite + React + TypeScript + Refine + React Router v6
- **의존성**: `frontend/package.json` — Refine, Radix UI, axios, react-hook-form, zod, recharts 등 포함
- **설정**: `vite.config.ts` — React 플러그인, `@` alias, 백엔드 프록시(`/api` → `http://backend:8001`)
- **TypeScript**: `tsconfig.json` + `tsconfig.app.json` + `tsconfig.node.json`
- **테스트**: **없음** (scripts, setupTests, CI 모두 부재)

### 핵심 파일 (테스트 대상)
1. **apiClient.ts** (29 LOC)
   - axios 인스턴스 생성, 토큰 인터셉터, 401 → `/admin/login` 리다이렉트
   - 테스트: 토큰 헤더 첨부, 401 응답 시 localStorage 클리어 + 리다이렉트

2. **authProvider.ts** (81 LOC)
   - Refine `AuthProvider` 구현: login(fetch), logout, check, getIdentity, onError
   - 테스트: 로그인 성공/실패, 토큰 저장, 로그아웃 후 localStorage 클리어, 만료 토큰 체크

3. **useChat.ts** (168 LOC)
   - SSE 스트림 기반 메시지 송수신 (`/api/rag/stream`)
   - 상태: `messages`, `isStreaming`
   - 이벤트: `answer_chunk`, `citations`, `done`, `error`
   - 테스트: 스트리밍 성공, 에러 처리, 메시지 버퍼 초기화, citation 추가

4. **InlineEditCell.tsx** (70 LOC)
   - 더블클릭 → Input → Enter/Escape/blur 처리
   - 테스트: 편집 모드 진입, 키보드 이벤트(Enter 저장, Escape 취소), blur 저장

5. **CommandPalette.tsx** (80 LOC)
   - `cmdk` 기반 네비게이션
   - 테스트: 검색 입력, 항목 선택 → navigate 호출 확인

6. **페이지 컴포넌트** (총 ~800 LOC)
   - `login.tsx`, `setup.tsx`, `topics/*`, `contexts/*`, `chat/index.tsx`
   - Refine 훅: `useLogin`, `useNavigation`, `useTable`, `useForm`, `useDataProvider`
   - 테스트: Refine 훅 모킹 + 필터링/일괄 편집/파일 업로드/채팅 플로우

### UI 컴포넌트
- `ui/button.tsx`, `ui/input.tsx`, `ui/toast.tsx`, `ui/dialog.tsx` 등 22개 (Radix + shadcn/ui)
- 대부분 재사용 가능한 Radix primitive 래퍼 → **기본적으로 Radix 테스트 범위에 포함**, 프로젝트 특화 로직만 테스트

## Hypotheses

1. **Vitest + RTL**: Vite 네이티브 → 빌드 통합 간편, Jest보다 빠름
2. **MSW**: axios 요청을 서비스 워커 모킹 → apiClient, authProvider, useChat SSE 모킹 가능
3. **Refine 모킹**: `@refinedev/core` 훅을 jest.mock으로 대체 → 페이지 단위 테스트 가능
4. **CI 추가**: GitHub Actions에 `test:frontend` 잡 추가 → PR 체크 필수
5. **커버리지**: Phase 0–3 완료 시 70% 달성 가능 (핵심 로직 우선, UI primitive는 최소화)

## Evidence

- **Backend**: `backend/tests/` 에 134개 테스트 (pytest + FastAPI testclient)
- **Frontend**: **0개 테스트** — 빠른 이터레이션 우선했으나 회귀 리스크 증가
- **Vite ecosystem**: Vitest 공식 권장, jsdom 환경 기본 지원
- **MSW v2**: SSE/stream 모킹 지원 (`res.stream()` 유틸)

## Assumptions & Open Questions

### Assumptions
- Vite workspace에 Vitest 설치 시 기존 빌드 프로세스 영향 없음
- Refine 4.58.0 버전은 테스트 환경에서 최소 모킹으로 작동
- React Router v6는 `MemoryRouter` 래퍼로 페이지 테스트 가능
- SSE 스트림은 MSW `res.stream()` + ReadableStream 모킹으로 재현 가능

### Open Questions
- **jsdom vs happy-dom**: jsdom 기본, 성능 필요 시 happy-dom 전환?
- **스냅샷 테스트**: UI 컴포넌트 스냅샷 금지(TASKS.md 명시) → 명시적 어서션만
- **Coverage threshold**: 70% 라인·브랜치 → 실제 달성률에 따라 조정 필요?
- **MSW 3.x**: 최신 버전 사용 가능? (현재 MSW 2.x 안정)

## Sub-agent Findings

N/A

## Risks

1. **Refine 훅 모킹 복잡도**: `useTable`, `useForm` 등 내부 상태가 많아 완전한 모킹 어려울 수 있음 → 최소 모킹 전략 필요
2. **SSE 스트림 재현**: MSW의 SSE 지원이 제한적일 경우 mock fetch + ReadableStream 직접 구현 필요
3. **CI 시간 증가**: Vitest 추가 시 CI 빌드 시간 +1–2분 예상 → 병렬 실행으로 최소화
4. **의존성 버전 충돌**: Vitest + jsdom + @testing-library/react 버전 호환 확인 필요

## Next

1. **Plan** 단계로 전환
2. Phase 0 인프라 구축 계획 수립:
   - 의존성 설치 목록
   - `vitest.config.ts` 설정 (jsdom, coverage, setupFiles)
   - `frontend/src/setupTests.ts` 작성 (MSW worker, Refine mock, global cleanup)
   - `package.json` 스크립트: `test`, `test:watch`, `test:coverage`
   - GitHub Actions 워크플로 수정
3. Phase 1–4 단계별 타깃 파일, 테스트 케이스, 검증 방법 정의
