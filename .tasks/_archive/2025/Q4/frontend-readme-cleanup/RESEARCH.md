# Research: Frontend README Cleanup

## Goal
`frontend/README.md`의 TODO 목록을 최신 상태로 반영하고 완료 항목을 체크 또는 제거.

## Scope
- `frontend/README.md` 파일 단독
- TODO 섹션(line 74-81) 검증 및 업데이트
- 실제 구현 상태와 대조 후 정확성 확보

## Related Files
- `/Users/kadragon/Dev/scholaria/frontend/README.md`
- `/Users/kadragon/Dev/scholaria/frontend/src/pages/contexts/*` (CRUD 구현)
- `/Users/kadragon/Dev/scholaria/frontend/src/components/ui/*` (shadcn/ui 컴포넌트)
- `/Users/kadragon/Dev/scholaria/frontend/package.json` (의존성 확인)

## Evidence

### TODO 항목 검증

1. **shadcn/ui integration** (line 75)
   - 상태: **완료 ✅**
   - 근거:
     - `package.json`에 Radix UI 의존성 다수 존재 (`@radix-ui/react-*`)
     - `src/components/ui/` 디렉터리에 24개 shadcn 컴포넌트 존재
     - `button.tsx`, `dialog.tsx`, `table.tsx`, `form.tsx` 등 활발히 사용 중

2. **Contexts CRUD with type-specific forms** (line 76)
   - 상태: **완료 ✅**
   - 근거:
     - `src/pages/contexts/list.tsx`, `create.tsx`, `edit.tsx`, `show.tsx` 존재
     - `list.tsx` 내 `contextTypeOptions`(PDF/FAQ/MARKDOWN) 정의 확인
     - 타입별 아이콘(FileText, FileQuestion, FileCode) 사용
     - `statusOptions` 및 필터링 구현

3. **File upload for PDF contexts** (line 77)
   - 상태: **완료 ✅**
   - 근거:
     - Git log: `963d8af` "Add PDF upload progress polling to context creation"
     - Git log: `86e9387` "Fix deployment issues and implement PDF upload feature"

4. **Bulk operations UI** (line 78)
   - 상태: **완료 ✅**
   - 근거:
     - `list.tsx`에서 `Checkbox` 컴포넌트 import (line 14)
     - `DataTableToolbar` 사용 (line 31) → 일괄 작업 툴바

5. **Processing status polling** (line 79)
   - 상태: **완료 ✅**
   - 근거:
     - `list.tsx`에서 `statusOptions` 정의 (PENDING/PROCESSING/COMPLETED/FAILED)
     - Git log: `963d8af` "Add PDF upload **progress polling**"

6. **Users management** (line 80)
   - 상태: **미확인** (추가 조사 필요)
   - 현재 `src/pages/` 내 users 관련 디렉터리 없음

## Assumptions / Open Questions
- Users management는 미구현으로 간주 (TODO 유지)
- 완료 항목 5개는 체크 또는 제거 결정 필요
- "Known Issues" 섹션도 검증 필요할 수 있으나 우선순위 낮음

## Risks
- 낮음. 문서 정리 작업으로 런타임 영향 없음.
- 오해의 소지 있는 TODO 목록은 사용자 혼란 유발 가능.

## Next
- Plan 단계로 진행: 완료 항목 체크/제거 방식 결정, Users management 항목 처리 방안 수립.
