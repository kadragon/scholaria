# Progress: Centralize API Client with Axios Interceptor

## Summary
localStorage.getItem("token") 중복 제거를 위한 중앙집중식 axios 인스턴스 구현 진행 중.

## Goal & Approach
- **목표**: 10+ 곳의 토큰 직접 참조를 axios 인터셉터로 통합
- **접근**:
  1. `lib/apiClient.ts` 생성 (public API용)
  2. 각 파일을 점진적으로 전환 (authProvider → pages)
  3. SSE 스트리밍도 axios로 전환 (ReadableStream 지원)

## Completed Steps
- ✅ Step 1: apiClient 생성 (`lib/apiClient.ts`)
- ✅ Step 2: authProvider 전환 (`getIdentity`)
- ✅ Step 3: contexts/list.tsx 전환 (벌크 작업 2곳)
- ✅ Step 4: contexts/create.tsx 전환 (생성/폴링 2곳)
- ✅ Step 5: contexts/show.tsx 전환 (CRUD 4곳)
- ✅ Step 6: chat/useChat.ts 전환 (SSE 스트리밍)
- ✅ Step 7: topics/list.tsx 전환 (시스템 프롬프트 업데이트)
- ✅ Step 8: 검증 및 커밋 (lint/typecheck 통과)

## Current Failures
_None_

## Decision Log
- **2025-10-08**: SSE 엔드포인트가 Authorization 헤더 지원 확인 → fetch() 대신 axios 스트리밍 사용 가능
- **2025-10-08**: dataProvider는 이미 axios 사용 중 → public API만 전환 대상

## Next Step
Step 1: `frontend/src/lib/apiClient.ts` 생성 및 인터셉터 구현
