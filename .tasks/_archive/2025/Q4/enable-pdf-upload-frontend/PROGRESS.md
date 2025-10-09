# Progress: Enable PDF Upload in Frontend

## Summary
프론트엔드 Context 생성 폼에서 비활성화된 PDF 파일 업로드 기능을 활성화합니다.

## Goal & Approach
- **Goal**: PDF 파일 업로드 UI 활성화 + FormData 전송 구현
- **Approach**: dataProvider FormData 지원 추가 → create.tsx 파일 상태 관리 → 검증 로직

## Completed Steps
- ✅ Research: 백엔드 API 계약 분석 (multipart/form-data)
- ✅ Plan: 5단계 구현 계획 수립
- ✅ Step 1: dataProvider FormData 지원 추가 (File 객체 감지 → FormData 생성)
- ✅ Step 2: File state & validation 추가 (size ≤ 100MB, type = PDF)
- ✅ Step 3: handleSubmit FormData 로직 구현
- ✅ Step 4: UI 개선 (파일명/크기 표시, 에러 메시지)
- ✅ Step 5: README.md TODO 체크

## Current Step
완료 - 수동 테스트 대기

## Decision Log
1. **dataProvider 전략**: `@refinedev/simple-rest` 기본 동작 유지, `create` 메서드만 커스텀 오버라이드
2. **검증 계층**: 클라이언트 (UX, 100MB/PDF) + 서버 (보안, backend/routers/contexts.py)
3. **FormData 감지**: `Object.values(variables).some(v => v instanceof File)` 패턴 사용

## Changes Made

### frontend/src/providers/dataProvider.ts
- 기본 provider를 `baseProvider`로 래핑
- `create` 메서드 오버라이드: File 객체 감지 시 FormData 생성
- Content-Type 헤더는 axios가 자동 설정

### frontend/src/pages/contexts/create.tsx
- State 추가: `file`, `fileError`
- `handleFileChange`: 파일 크기/타입 검증 (100MB, application/pdf)
- `handleSubmit`: PDF 타입일 때 FormData 전송, 아니면 JSON
- UI: 파일명/크기 표시, 에러 메시지, disabled 제거

### frontend/README.md
- TODO 항목 체크: `[x] File upload for PDF contexts`

## Next Step
수동 테스트 수행 (백엔드 실행 필요)
