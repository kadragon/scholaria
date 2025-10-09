# Plan: shadcn/ui 통합 + Contexts 리소스 구현

## Objective
admin-frontend에 shadcn/ui를 설정하고, Contexts 리소스 CRUD UI를 구현하여 타입별 컨텍스트 관리 가능하게 함

## Constraints
- 기존 Refine + React Router 구조 유지
- Topics 페이지는 shadcn 적용으로 리팩토링
- Backend Admin API 먼저 완성 후 Frontend 작업
- TDD 원칙 준수 (Backend 테스트)

## Target Files & Changes

### Backend (Admin API 구현)
1. **`api/routers/admin/contexts.py`**
   - `list_contexts()`: Context 목록 + pagination (Refine 형식)
   - `get_context()`: 단일 Context 조회
   - `create_context()`: Context 생성 (파일 업로드 지원)
   - `update_context()`: Context 수정
   - `delete_context()`: Context 삭제

2. **`api/tests/admin/test_admin_contexts.py`** (NEW)
   - Admin API 전용 테스트 (기존 `/api/contexts` 테스트와 분리)
   - Refine pagination 형식 검증

### Frontend (shadcn/ui 통합)
3. **Tailwind + shadcn 설정**
   - `admin-frontend/tailwind.config.ts` (NEW)
   - `admin-frontend/postcss.config.js` (NEW)
   - `admin-frontend/src/index.css` (UPDATE): Tailwind directives 추가
   - `admin-frontend/tsconfig.json` (UPDATE): `@/*` path alias
   - `admin-frontend/vite.config.ts` (UPDATE): path alias resolver

4. **shadcn 컴포넌트 설치**
   - `components.json` (NEW): shadcn 설정 파일
   - `src/components/ui/` (NEW): table, button, input, card, dialog, tabs, form

5. **Contexts 페이지 구현**
   - `admin-frontend/src/pages/contexts/list.tsx` (NEW): Contexts 목록 (data-table)
   - `admin-frontend/src/pages/contexts/create.tsx` (NEW): 타입별 생성 폼 (Tabs)
   - `admin-frontend/src/pages/contexts/edit.tsx` (NEW): 수정 폼

6. **Topics 페이지 리팩토링**
   - `admin-frontend/src/pages/topics/list.tsx` (UPDATE): shadcn table 적용
   - `admin-frontend/src/pages/topics/create.tsx` (UPDATE): shadcn form 적용
   - `admin-frontend/src/pages/topics/edit.tsx` (UPDATE): shadcn form 적용

7. **App 설정**
   - `admin-frontend/src/App.tsx` (UPDATE): contexts 리소스 추가

## Test/Validation Cases

### Backend Tests
- [ ] `test_list_contexts_pagination`: Refine 형식 응답 검증
- [ ] `test_get_context_by_id`: 단일 조회
- [ ] `test_create_pdf_context`: PDF 타입 생성
- [ ] `test_create_markdown_context`: Markdown 타입 생성
- [ ] `test_create_faq_context`: FAQ 타입 생성
- [ ] `test_update_context`: 수정
- [ ] `test_delete_context`: 삭제
- [ ] `test_unauthorized_access`: 인증 실패 시 401

### Frontend Validation
- [ ] `npm run typecheck`: TypeScript 오류 없음
- [ ] `npm run lint`: ESLint 통과
- [ ] `npm run build`: 빌드 성공
- [ ] 수동 테스트: Contexts CRUD 동작 확인 (localhost:5173)

## Steps

### [Behavioral] Step 1: Backend Admin API 구현 (TDD)
1.1. `api/tests/admin/test_admin_contexts.py` 생성 (failing tests)
1.2. `api/routers/admin/contexts.py` 구현 (pass tests)
1.3. `api/routers/admin/__init__.py`에 contexts router 등록
1.4. 테스트 실행: `pytest api/tests/admin/test_admin_contexts.py -v`

### [Structural] Step 2: shadcn/ui 설정
2.1. Tailwind 설치: `cd admin-frontend && npm install -D tailwindcss postcss autoprefixer`
2.2. Tailwind 초기화: `npx tailwindcss init -p`
2.3. `tailwind.config.ts` 설정 (content paths)
2.4. `src/index.css`에 Tailwind directives 추가
2.5. `tsconfig.json`에 path alias 추가
2.6. `vite.config.ts`에 alias resolver 추가
2.7. shadcn 초기화: `npx shadcn@latest init`

### [Structural] Step 3: shadcn 컴포넌트 설치
3.1. `npx shadcn@latest add table button input card dialog tabs form label textarea select`
3.2. 설치 확인: `ls src/components/ui/`

### [Behavioral] Step 4: Contexts 리소스 구현
4.1. `src/pages/contexts/list.tsx` 생성 (data-table)
4.2. `src/pages/contexts/create.tsx` 생성 (타입별 Tabs)
4.3. `src/pages/contexts/edit.tsx` 생성
4.4. `src/App.tsx`에 contexts 리소스 등록

### [Behavioral] Step 5: Topics 페이지 리팩토링
5.1. `src/pages/topics/list.tsx` → shadcn table 적용
5.2. `src/pages/topics/create.tsx` → shadcn form 적용
5.3. `src/pages/topics/edit.tsx` → shadcn form 적용

### [Behavioral] Step 6: 통합 검증
6.1. Backend 테스트: `pytest api/tests/admin/test_admin_contexts.py -v`
6.2. Frontend 빌드: `cd admin-frontend && npm run typecheck && npm run build`
6.3. 수동 테스트: `npm run dev` → Contexts CRUD 동작 확인

## Status
- [x] Step 1: Backend Admin API 구현 ✅
- [x] Step 2: shadcn/ui 설정 ✅
- [x] Step 3: shadcn 컴포넌트 설치 ✅
- [x] Step 4: Contexts 리소스 구현 ✅
- [x] Step 5: Topics 페이지 리팩토링 ✅
- [x] Step 6: 통합 검증 ✅

**모든 단계 완료. 배포 준비 완료.**

## Rollback
- Backend: `git revert <commit>` (Alembic 마이그레이션 없음)
- Frontend: `npm uninstall tailwindcss ...` + `git checkout -- .`
- 최악의 경우: 전체 롤백 `git reset --hard HEAD~N`

## Review Hotspots
- `api/routers/admin/contexts.py`: Refine pagination 형식 정확성
- `src/pages/contexts/create.tsx`: 타입별 폼 전환 로직
- `tailwind.config.ts`: content paths 설정 (빌드 시 CSS 누락 방지)
