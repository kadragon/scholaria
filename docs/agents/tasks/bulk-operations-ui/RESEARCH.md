# RESEARCH: Bulk Operations UI

## Goal
Refine Admin Panel에 bulk operations UI 추가 (컨텍스트 일괄 할당, 임베딩 재생성, 시스템 프롬프트 일괄 업데이트)

## Scope
- Topics 목록에서 여러 항목 선택 → 시스템 프롬프트 일괄 업데이트
- Contexts 목록에서 여러 항목 선택 → Topic에 일괄 할당, 임베딩 재생성
- Refine의 다중 선택 UI 패턴 활용
- shadcn/ui Dialog, Button 컴포넌트 재사용

## Related Files/Flows

### Backend API (이미 구현됨)
- `api/routers/admin/bulk_operations.py`:
  - POST /api/admin/bulk/assign-context-to-topic
  - POST /api/admin/bulk/regenerate-embeddings
  - POST /api/admin/bulk/update-system-prompt
- `api/schemas/admin.py`: Request/Response schemas

### Frontend 구조
- `admin-frontend/src/pages/topics/list.tsx` - Topics 목록
- `admin-frontend/src/pages/contexts/list.tsx` - Contexts 목록
- `admin-frontend/src/components/ui/` - shadcn/ui 컴포넌트

## Hypotheses

### H1: Refine의 useTable에서 다중 선택 지원
**가설**: Refine의 useTable hook이 row selection을 기본 제공
**검증**: @refinedev/core 문서 확인, useTable에 rowSelection 옵션 추가

### H2: Bulk actions는 별도 Dialog로 처리
**가설**: 선택된 항목에 대해 Dialog를 열어 bulk action 수행
**검증**: shadcn/ui Dialog + Form 조합으로 구현

### H3: API 호출은 Refine의 useCustomMutation
**가설**: Bulk operations는 Refine의 기본 CRUD가 아니므로 useCustomMutation 사용
**검증**: @refinedev/core의 useCustomMutation hook 활용

## Evidence

### Backend API 엔드포인트
1. **Bulk Assign Context to Topic**:
   - POST /api/admin/bulk/assign-context-to-topic
   - Body: `{ topic_id: number, context_ids: number[] }`
   - Response: `{ assigned_count: number, topic_id: number }`

2. **Bulk Regenerate Embeddings**:
   - POST /api/admin/bulk/regenerate-embeddings
   - Body: `{ context_ids: number[] }`
   - Response: `{ queued_count: number, task_ids: string[] }`

3. **Bulk Update System Prompt**:
   - POST /api/admin/bulk/update-system-prompt
   - Body: `{ topic_ids: number[], system_prompt: string }`
   - Response: `{ updated_count: number }`

### Refine 패턴
- Refine은 기본적으로 TanStack Table (React Table v8) 사용
- Row selection은 `enableRowSelection` prop으로 활성화
- 선택된 rows는 `table.getSelectedRowModel()` 로 접근

## Assumptions/Open Qs

### Assumptions
1. Contexts 목록에서 Topic 선택 시 모든 Topics 목록 필요 (GET /api/topics/)
2. Bulk actions는 비동기 처리 후 목록 refetch 필요
3. 사용자 피드백을 위한 Toast 또는 Alert 컴포넌트 필요

### Open Questions
1. **Q1**: Refine Admin Panel이 TanStack Table을 사용하는가?
   - 확인 필요: 현재 TopicList, ContextList 구현 확인

2. **Q2**: shadcn/ui에 Toast 컴포넌트가 있는가?
   - 필요 시 shadcn/ui Toast 추가

3. **Q3**: 임베딩 재생성은 비동기 작업 - 진행 상태 표시 필요한가?
   - Option A: 단순히 "작업이 큐에 추가되었습니다" 메시지
   - Option B: 실시간 진행 상태 표시 (Phase 2에서 구현)

## Risks

### Medium
1. **UX 복잡도**: 너무 많은 bulk actions으로 UI가 복잡해질 수 있음
2. **에러 처리**: Partial failure 시나리오 (일부 컨텍스트만 실패)

### Low
1. **성능**: 수백 개 항목 선택 시 UI 렌더링 성능
2. **권한**: 이미 require_admin으로 보호되어 있음

## Next

### 우선순위 조사
1. 현재 TopicList, ContextList 구현 확인 (Table 라이브러리 확인)
2. shadcn/ui Toast 컴포넌트 확인
3. Refine useCustomMutation 예제 확인

### 결정 필요
1. Bulk actions UI 위치 (테이블 상단 툴바 vs 선택 시 floating bar)
2. Toast vs Dialog로 성공/에러 메시지 표시
3. 단계별 구현 순서 (assign → regenerate → update)
