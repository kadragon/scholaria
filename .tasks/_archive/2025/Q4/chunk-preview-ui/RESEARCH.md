# Research: Chunk Preview UI Enhancement

## Goal

Context 상세 페이지에서 청크(ContextItem) 목록을 미리보기와 함께 시각화

## Scope

Frontend: Context 상세/편집 화면에 청크 목록 표시
Backend: ContextItem 조회 API 제공

## Related Files/Flows

### Frontend (현재 상태)
- `frontend/src/pages/contexts/list.tsx`: Context 목록 표시 (chunk_count만 표시)
- `frontend/src/pages/contexts/edit.tsx`: Context 편집 (MARKDOWN 타입만 content 편집 가능)
- **누락**: Context 상세 페이지 없음 (`show.tsx` 파일 없음)

### Backend (API)
- `backend/routers/contexts.py`:
  - `GET /contexts/{context_id}` → `ContextOut` (items 제외)
  - `POST /contexts/{context_id}/qa` → FAQ Q&A 추가
- `backend/schemas/context.py`:
  - `ContextOut`: items 포함 안 함
  - `ContextWithItemsOut`: items 포함 (사용되지 않음)
  - `ContextItemOut`: 개별 청크 스키마 (id, title, content, created_at 등)

### Data Models
- `Context` (1) : `ContextItem` (N) 관계
- `ContextItem` 필드: id, title, content, context_id, file_path, created_at, updated_at

## Hypotheses

1. **현재 상태**: Context 상세 페이지가 없어 청크를 볼 방법이 없음
2. **API 갭**: `GET /contexts/{id}` 엔드포인트가 items를 반환하지 않음 (스키마는 존재하나 미사용)
3. **개선 방향**:
   - 새 엔드포인트 추가: `GET /contexts/{id}/items` → `list[ContextItemOut]`
   - 또는 기존 엔드포인트 확장: `GET /contexts/{id}?include_items=true` → `ContextWithItemsOut`

## Evidence

### 1. Frontend 누락 기능
- Context list에서 "Edit" 버튼만 있고 "View" 버튼 없음
- Edit 페이지는 메타데이터만 편집 (청크 표시 안 함)

### 2. Backend Schema 불일치
- `ContextWithItemsOut` 스키마 정의됨 → 실제 라우터에서 사용 안 함
- `ContextItemOut` 스키마 존재 → FAQ Q&A 추가 시에만 반환

### 3. 유사 기능 존재
- `backend/routers/admin/contexts.py`에 Admin API가 있을 가능성 (확인 필요)

## Assumptions/Open Questions

1. **Q**: 청크를 inline으로 편집 가능하게 할 것인가?
   - **A**: 일단 read-only 미리보기만 구현 (편집은 Phase 2)

2. **Q**: 페이지네이션이 필요한가?
   - **A**: Context당 청크 수가 많을 수 있으므로 가상 스크롤 또는 페이지네이션 고려

3. **Q**: 기존 엔드포인트 수정 vs 새 엔드포인트?
   - **A**: 새 엔드포인트 추가 (`GET /contexts/{id}/items`) - 기존 API 호환성 유지

## Sub-agent Findings

N/A (수동 조사로 충분)

## Risks

1. **성능**: Context당 청크가 수백~수천 개일 경우 응답 크기 문제
   - **완화**: 페이지네이션 또는 limit/offset 파라미터
2. **Breaking Change**: 기존 API 수정 시 frontend 호환성
   - **완화**: 새 엔드포인트 추가로 회피

## Next Steps

1. Backend: `GET /contexts/{id}/items` 엔드포인트 추가 (TDD)
2. Frontend: Context 상세 페이지 (`show.tsx`) 생성
3. Frontend: 청크 목록 컴포넌트 구현 (Card 또는 Table)
4. Integration: 청크 미리보기 UI 연결
