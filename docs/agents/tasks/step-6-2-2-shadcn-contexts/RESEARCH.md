# Research: shadcn/ui 통합 + Contexts 리소스 구현

## Goal
admin-frontend에 shadcn/ui를 통합하고, Contexts 리소스를 위한 테이블/폼 UI를 구현

## Scope
- shadcn/ui + Tailwind CSS 설치 및 설정
- Contexts 리소스 CRUD 페이지 구현 (list/create/edit)
- 타입별 컨텍스트 생성 폼 (PDF/Markdown/FAQ)
- 기존 Topics UI 개선 (shadcn 컴포넌트 적용)

## Related Files/Flows

### 현재 Admin Frontend 구조
- `admin-frontend/package.json`: Refine 설치 완료 (core, react-router-v6, simple-rest)
- `admin-frontend/src/App.tsx`: Topics 리소스만 등록, Layout 컴포넌트 있음
- `admin-frontend/src/pages/topics/list.tsx`: 기본 HTML table 사용 (inline styles)
- `admin-frontend/src/providers/dataProvider.ts`: adminDataProvider (REST API)
- `admin-frontend/src/providers/authProvider.ts`: JWT 인증
- **NO** Tailwind/shadcn: `npm list`에서 확인, config 파일 없음

### Backend Contexts API
- `api/routers/admin/contexts.py`:
  - GET /admin/contexts (list, pagination support)
  - **TODO**: 아직 구현 안됨 (빈 응답)
- `api/schemas/context.py`:
  - ContextOut, ContextCreate, ContextUpdate, FAQQACreate
  - context_type: PDF|Markdown|FAQ
  - original_content, chunk_count, processing_status

### 필요한 shadcn/ui 컴포넌트
- **Table**: data-table (Contexts/Topics 리스트)
- **Form**: input, textarea, select, label (생성/편집)
- **Button**: 액션 버튼
- **Card**: 레이아웃
- **Dialog**: 삭제 확인, FAQ Q&A 추가 모달
- **Tabs**: 타입별 폼 전환 (PDF/Markdown/FAQ)

## Hypotheses
1. shadcn/ui는 Tailwind CSS 기반 → `tailwindcss`, `postcss`, `autoprefixer` 설치 필요
2. `npx shadcn@latest init`으로 초기 설정 가능
3. Refine과 충돌 없이 shadcn 컴포넌트 사용 가능 (단순 UI 라이브러리)
4. Contexts Admin API는 현재 빈 껍데기 → 먼저 구현 필요

## Evidence
- `admin-frontend/package.json`: shadcn 관련 패키지 없음 (검증 완료)
- `admin-frontend/vite.config.ts`: Tailwind 플러그인 없음
- `admin-frontend/tsconfig.json`: path alias 설정 없음 (shadcn은 `@/` alias 필요)
- Backend: `api/routers/admin/contexts.py:14` → `return {"data": [], "total": 0}` (TODO 주석)

## Assumptions/Open Questions
- **Q1**: Contexts Admin API를 먼저 완성할지, UI와 병렬로 진행할지?
  - **A**: Phase 4 완료 시 Write API는 `/api/contexts`에 이미 구현됨 (POST/PUT/DELETE)
  - Admin API (`/admin/contexts`)는 Refine 전용 pagination 포맷 필요 → 먼저 구현
- **Q2**: shadcn/ui 초기 설정 시 TypeScript path alias 변경 필요?
  - **A**: Yes, `tsconfig.json`에 `"@/*": ["./src/*"]` 추가
- **Q3**: 기존 Topics 페이지도 shadcn으로 리팩토링?
  - **A**: Yes, 일관성 위해 함께 변경

## Sub-agent Findings
N/A

## Risks
1. **Tailwind 설정 충돌**: Vite 플러그인 추가 시 기존 CSS 영향
2. **TypeScript path alias**: tsconfig 변경 시 빌드 재설정 필요
3. **API 미구현**: Contexts Admin API가 빈 상태 → UI 테스트 불가

## Next
PLAN.md 작성 → 단계별 구현 계획
