# 프론트엔드 린트 및 타입 에러 수정

## 목표
프론트엔드 ESLint 에러 3개, 경고 1개, TypeScript 빌드 에러 9개 수정

## 현재 상태
- ESLint: 3개 에러, 1개 경고
- TypeScript 빌드 (tsc -b): 9개 에러
- TypeScript 타입 체크 (tsc --noEmit): 통과

## 이슈 분류

### 1. ESLint 에러 (3개)
**a. react-refresh/only-export-components (2개)**
- `src/components/ui/button.tsx:57:18`
- `src/components/ui/form.tsx:171:3`
- 원인: 컴포넌트 파일에서 컴포넌트 외에 상수/함수 export
- 해결: `/* eslint-disable react-refresh/only-export-components */` 주석 추가 (shadcn/ui 생성 파일)

**b. @typescript-eslint/no-unused-vars (1개)**
- `src/hooks/use-toast.ts:18:7` - `actionTypes` 변수
- 원인: 타입으로만 사용되는 변수
- 해결: `as const` 추가 또는 타입 정의로 변경

### 2. ESLint 경고 (1개)
**react-hooks/exhaustive-deps**
- `src/pages/contexts/show.tsx:151:6`
- 원인: useEffect 의존성 배열 누락
- 해결: `fetchItems`를 useCallback으로 래핑 또는 의존성 추가

### 3. TypeScript 빌드 에러 (9개)
**a. contexts/list.tsx (5개)**
- Line 58: `Set<BaseKey | undefined>` → `Set<number>` 불일치
- Line 156: `data.data.length` possibly undefined
- Line 207, 209: `BaseKey | undefined` → `number` 불일치
- Line 276: `topic.id` possibly undefined

**b. topics/list.tsx (4개)**
- Line 47: `Set<BaseKey | undefined>` → `Set<number>` 불일치
- Line 107: `data.data.length` possibly undefined
- Line 148, 150: `BaseKey | undefined` → `number` 불일치

## 단계별 실행 계획

### Step 1: ESLint 에러 수정 ✅
- [ ] `button.tsx`: eslint-disable 주석 추가
- [ ] `form.tsx`: eslint-disable 주석 추가
- [ ] `use-toast.ts`: actionTypes 타입 문제 수정
- [ ] `npm run lint` 실행하여 검증

### Step 2: TypeScript 에러 수정 - contexts/list.tsx ✅
- [ ] Line 58: selectedRowKeys 타입 가드 추가
- [ ] Line 156: optional chaining 또는 기본값 처리
- [ ] Line 207, 209: record.id 타입 가드 추가
- [ ] Line 276: topic.id 타입 가드 추가

### Step 3: TypeScript 에러 수정 - topics/list.tsx ✅
- [ ] Line 47: selectedRowKeys 타입 가드 추가
- [ ] Line 107: optional chaining 또는 기본값 처리
- [ ] Line 148, 150: record.id 타입 가드 추가

### Step 4: ESLint 경고 수정 ✅
- [ ] `contexts/show.tsx`: useCallback으로 fetchItems 래핑

### Step 5: 빌드 검증 ✅
- [ ] `npm run lint` - ESLint 통과 확인
- [ ] `npm run typecheck` - 타입 체크 통과 확인
- [ ] `npm run build` - 빌드 성공 확인

## 성공 기준
- ✅ ESLint: 0개 에러, 0개 경고
- ✅ TypeScript 타입 체크: 통과
- ✅ 빌드: 성공
- ✅ 기능 동작: 정상

## 예상 소요 시간
- Step 1: 10분
- Step 2: 15분
- Step 3: 10분
- Step 4: 5분
- Step 5: 5분
- **총합**: 약 45분
