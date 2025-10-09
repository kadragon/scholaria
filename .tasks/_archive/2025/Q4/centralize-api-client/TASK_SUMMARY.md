# Task Summary: Centralize API Client

## 목표
localStorage.getItem("token") 중복 제거 및 axios 인터셉터 기반 중앙집중식 인증 관리.

## 핵심 변경
- **새 파일**: `frontend/src/lib/apiClient.ts` (axios 인스턴스 + 인터셉터)
- **제거**: `localStorage.getItem("token")` 직접 참조 10+ 곳
- **전환**: authProvider, contexts, topics, chat SSE → apiClient 사용
- **LOC**: -136줄 (중복 제거)

## 테스트
- `pnpm lint` ✅
- `pnpm typecheck` ✅
- 수동 검증 필요: 로그인/API 요청/SSE 스트리밍

## 커밋
- **SHA**: `8315f96`
- **브랜치**: `feat/centralize-api-client`
- **타입**: Structural (리팩터링)
