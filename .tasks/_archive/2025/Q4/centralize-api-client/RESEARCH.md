# Research: Centralize API Client with Axios Interceptor

## Goal
localStorage.getItem("token") 중복 제거 및 중앙집중식 인증 헤더 관리로 유지보수성 향상.

## Scope
- `frontend/src/*` 내 모든 API 요청 (토큰 직접 참조 10+ 곳)
- Axios 인스턴스 생성 및 인터셉터 설정
- authProvider와의 통합

## Related Files & Flows

### 현재 토큰 직접 참조 (10+ 곳)
- `frontend/src/providers/authProvider.ts` (2곳: check, getIdentity)
- `frontend/src/providers/dataProvider.ts` (1곳: 인터셉터 이미 존재)
- `frontend/src/pages/contexts/list.tsx` (2곳)
- `frontend/src/pages/contexts/create.tsx` (2곳)
- `frontend/src/pages/contexts/show.tsx` (4곳)
- `frontend/src/pages/chat/hooks/useChat.ts` (1곳: SSE)
- `frontend/src/pages/topics/list.tsx` (1곳)

### 이미 구현된 부분
- `dataProvider.ts`: **이미 Axios 인터셉터 사용** (admin API용)
- axios 패키지: 이미 설치됨 (^1.12.2)

### 핵심 패턴
1. **Admin 영역**: `dataProvider.ts` → axios 인터셉터로 자동 주입
2. **Public 영역**: fetch() 직접 사용 → 토큰 수동 주입

## Hypotheses

**H1**: dataProvider의 axios 인터셉터 패턴을 재사용 가능
**증거**: 동일 패턴으로 admin API 이미 동작 중

**H2**: authProvider의 fetch() → axios 전환 필요
**증거**: check/getIdentity에서 토큰 직접 가져옴

**H3**: Public API용 별도 axios 인스턴스 필요
**근거**: admin(`/api/admin`) vs public(`/api`) base URL 분리

**H4**: SSE(EventSource) 엔드포인트는 예외 처리 필요
**증거**: `useChat.ts`에서 EventSource 사용 (axios 불가)

## Evidence

### 현재 admin API 인터셉터 (이미 동작 중)
```typescript
// frontend/src/providers/dataProvider.ts
const axiosInstance = axios.create();
axiosInstance.interceptors.request.use((config) => {
  const token = localStorage.getItem("token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});
```

### Public API fetch 패턴 (변경 대상)
```typescript
// frontend/src/pages/contexts/list.tsx:169
const response = await fetch(url, {
  headers: {
    Authorization: `Bearer ${localStorage.getItem("token")}`,
  },
});
```

## Assumptions / Open Questions

**가정**:
- SSE(`/api/rag/stream`)는 EventSource만 지원 → 헤더 주입은 URL 쿼리로 대체 필요
- authProvider의 fetch → axios 전환은 기존 동작 유지 가능

**열린 질문**:
- [ ] EventSource는 Authorization 헤더 지원하지 않음 → 쿼리 파라미터로 토큰 전달? (보안 우려)
- [ ] 또는 SSE 전용 토큰 교환 메커니즘 필요?

## Risks

**중대**: SSE 토큰 주입 패턴 결정 필요 (헤더 불가, 쿼리는 로그에 노출 위험)
**보통**: authProvider 변경으로 인한 로그인/로그아웃 흐름 회귀
**낮음**: 기존 admin API는 이미 동작 중 (변경 최소화)

## Next

1. **Plan 작성**:
   - `lib/apiClient.ts` 생성 (public API용 axios 인스턴스)
   - authProvider fetch → axios 전환
   - SSE 토큰 주입 전략 결정 (쿼리 vs 별도 인증 엔드포인트)
2. **TDD 시작**: 인터셉터 동작 테스트 → 각 페이지 리팩터링
