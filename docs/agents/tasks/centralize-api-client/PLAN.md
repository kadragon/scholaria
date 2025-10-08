# Plan: Centralize API Client with Axios Interceptor

## Objective
localStorage.getItem("token") 직접 참조 10+ 곳을 중앙집중식 axios 인스턴스로 통합하여 유지보수성 향상.

## Constraints
- **기존 동작 유지**: 로그인/로그아웃/API 요청 동작 불변
- **점진적 전환**: dataProvider는 이미 axios 사용 중 → public API만 전환
- **SSE 예외**: fetch() 스트리밍은 axios로 전환 가능 (axios는 ReadableStream 지원)
- **TDD**: 각 파일 변경 전 테스트 작성

## Target Files & Changes

### 1. 새 파일: `frontend/src/lib/apiClient.ts`
**생성**: Public API용 axios 인스턴스 및 인터셉터
```typescript
// Public API 베이스 URL
const publicApi = axios.create({ baseURL: '/api' });
// 요청 인터셉터: 토큰 자동 주입
// 응답 인터셉터: 401 → 로그아웃
```

### 2. 수정: `frontend/src/providers/authProvider.ts` (2곳)
**변경 전**: fetch() + `localStorage.getItem("token")`
**변경 후**: `apiClient.get('/auth/me')`
- [ ] `check()` → axios로 전환
- [ ] `getIdentity()` → axios로 전환

### 3. 수정: `frontend/src/pages/contexts/list.tsx` (2곳)
**변경 전**: fetch() + 수동 헤더
**변경 후**: `apiClient.put()`, `apiClient.delete()`
- [ ] handleToggleActive
- [ ] handleDelete

### 4. 수정: `frontend/src/pages/contexts/create.tsx` (2곳)
**변경 전**: fetch() + 수동 헤더
**변경 후**: `apiClient.get()`, `apiClient.post()`
- [ ] FAQ Q&A 쌍 생성

### 5. 수정: `frontend/src/pages/contexts/show.tsx` (4곳)
**변경 전**: fetch() + 수동 헤더
**변경 후**: `apiClient.post()`, `apiClient.put()`, `apiClient.delete()`
- [ ] handleAddQuestion
- [ ] handleUpdateItem
- [ ] handleDeleteItem
- [ ] handleReorderItems

### 6. 수정: `frontend/src/pages/chat/hooks/useChat.ts` (1곳)
**변경 전**: fetch() 스트리밍 + 수동 헤더
**변경 후**: `apiClient.post()` with `responseType: 'stream'`
- [ ] sendMessage SSE 요청

### 7. 수정: `frontend/src/pages/topics/list.tsx` (1곳)
**변경 전**: fetch() + 수동 헤더
**변경 후**: `apiClient.put()`
- [ ] handleToggleActive

## Test & Validation Cases

### 단위 테스트 (Jest/Vitest 필요 시 추가)
- [ ] **apiClient 인터셉터**: 토큰 자동 주입 확인
- [ ] **401 응답**: 자동 로그아웃 트리거 확인
- [ ] **토큰 없음**: 헤더 누락 확인

### 통합 테스트 (수동 검증)
- [ ] **로그인**: 토큰 저장 → 이후 요청에 자동 첨부
- [ ] **API 요청**: contexts/topics CRUD 동작
- [ ] **SSE 스트리밍**: 질문 → 답변 스트리밍 정상 동작
- [ ] **만료 토큰**: 401 → 로그인 페이지 리다이렉트

## Steps

### Step 1: apiClient 생성
- [ ] `frontend/src/lib/apiClient.ts` 생성
- [ ] 요청 인터셉터: 토큰 자동 주입
- [ ] 응답 인터셉터: 401 → localStorage.removeItem("token") + redirect

### Step 2: authProvider 전환
- [ ] `check()` 메서드 axios 전환
- [ ] `getIdentity()` 메서드 axios 전환

### Step 3: contexts/list.tsx 전환
- [ ] handleToggleActive
- [ ] handleDelete

### Step 4: contexts/create.tsx 전환
- [ ] FAQ Q&A 생성 로직

### Step 5: contexts/show.tsx 전환
- [ ] 4개 핸들러 전환

### Step 6: chat/useChat.ts 전환
- [ ] SSE 스트리밍 axios 전환

### Step 7: topics/list.tsx 전환
- [ ] handleToggleActive

### Step 8: 검증 및 커밋
- [ ] `pnpm typecheck` 통과
- [ ] `pnpm lint` 통과
- [ ] 수동 테스트 완료
- [ ] 커밋: `[Structural] refactor(frontend): centralize API client with axios interceptor [centralize-api-client]`

## Rollback
모든 변경은 단일 커밋 → `git revert <commit-sha>` 또는 `git reset --hard HEAD~1`

## Review Hotspots
- **SSE 스트리밍**: axios의 ReadableStream 처리 확인 필요
- **401 인터셉터**: 무한 루프 방지 (로그인 페이지에서 401 시 재귀 방지)
- **dataProvider 충돌**: 기존 admin axios 인스턴스와 분리 확인

## Status
- [ ] Step 1: apiClient 생성
- [ ] Step 2: authProvider 전환
- [ ] Step 3: contexts/list.tsx 전환
- [ ] Step 4: contexts/create.tsx 전환
- [ ] Step 5: contexts/show.tsx 전환
- [ ] Step 6: chat/useChat.ts 전환
- [ ] Step 7: topics/list.tsx 전환
- [ ] Step 8: 검증 및 커밋
