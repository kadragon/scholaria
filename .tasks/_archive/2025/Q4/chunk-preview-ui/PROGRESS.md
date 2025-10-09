# Progress: Chunk Preview UI Enhancement

## Summary

Context 상세 페이지 및 청크 목록 API 구현 완료 - 관리자가 Context의 ContextItem(청크)를 미리보기 형태로 확인 가능

## Goal & Approach

**Goal**: Context 상세 페이지에서 청크 목록을 시각화
**Approach**:
- Backend: TDD로 `GET /contexts/{id}/items` 엔드포인트 추가
- Frontend: Refine show 페이지 + Table UI 구성

## Completed Steps

### Phase 1: Backend API (TDD) ✅
1. ✅ 테스트 작성: `test_get_context_items_not_found` (404)
2. ✅ 테스트 작성: `test_get_context_items_empty` (빈 목록)
3. ✅ 테스트 작성: `test_get_context_items_success` (정상 조회)
4. ✅ 테스트 작성: `test_get_context_items_pagination` (skip/limit)
5. ✅ 구현: `GET /contexts/{context_id}/items` 엔드포인트
   - Response: `list[ContextItemOut]`
   - Query params: `skip=0`, `limit=100`
   - Context 존재 여부 검증 (404)
   - Datetime 직렬화 (ISO format)
6. ✅ 검증: 8/8 테스트 통과, ruff/mypy 통과

### Phase 2: Frontend UI ✅
7. ✅ 라우팅 추가: `App.tsx`에 `/contexts/show/:id` 경로
8. ✅ 페이지 생성: `show.tsx`
   - Context 메타데이터 표시 (name, description, type, chunk_count, status)
   - ContextItem 목록 Table (id, title, content preview, created_at)
   - "Edit" / "Back to List" 버튼
   - 빈 상태 처리 ("No chunks available")
9. ✅ API 연동: `useOne` + custom fetch for items
10. ✅ List 페이지 수정: "View" 버튼 추가 (이미 존재)

## Current Failures

없음 - 모든 테스트 통과

## Validation Status

### Backend
- ✅ 4개 신규 테스트 통과
  - `test_get_context_items_not_found`: 404 처리
  - `test_get_context_items_empty`: 빈 목록 반환
  - `test_get_context_items_success`: 청크 목록 조회 + ISO datetime
  - `test_get_context_items_pagination`: skip/limit 동작
- ✅ ruff 검사 통과
- ✅ mypy 타입 검사 통과

### Frontend
- ✅ 라우팅 정의 (show 경로)
- ✅ UI 컴포넌트 구현 (show.tsx)
- ✅ List 페이지 "View" 버튼 연동
- ⚠️ 수동 테스트 필요 (dev 서버 미실행)

## Decision Log

1. **새 엔드포인트 vs 기존 확장**
   - 결정: 새 엔드포인트 `GET /contexts/{id}/items` 추가
   - 이유: 기존 API 호환성 유지, 명확한 책임 분리

2. **Pagination 기본값**
   - 결정: `skip=0`, `limit=100`
   - 이유: 대부분 Context는 100개 이하 청크, 필요시 확장 가능

3. **Content Preview 길이**
   - 결정: 100자 + "..." truncate
   - 이유: 테이블 가독성 유지, 전체 내용은 향후 모달/확장 기능

4. **Frontend 상태 관리**
   - 결정: `useEffect` + manual fetch (items)
   - 이유: Refine `useOne`은 단일 리소스만, items는 별도 엔드포인트

## Files Touched

### Backend
- `backend/routers/contexts.py` (+16 lines): `get_context_items` 엔드포인트 추가
- `backend/tests/test_contexts.py` (+92 lines): 4개 신규 테스트 추가

### Frontend
- `frontend/src/App.tsx` (+4 lines): show 라우팅 추가
- `frontend/src/pages/contexts/show.tsx` (+158 lines, 신규): Context 상세 페이지
- `frontend/src/pages/contexts/list.tsx` (+1 line): `show` navigation 추가

## Next Step

PROGRESS 문서 작성 완료 → 커밋 및 문서 업데이트
