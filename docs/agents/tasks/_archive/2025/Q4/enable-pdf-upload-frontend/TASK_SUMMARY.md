# Task Summary: Enable PDF Upload in Frontend

## Goal
프론트엔드 Context 생성 폼에서 비활성화된 PDF 파일 업로드 기능을 활성화합니다.

## Key Changes

### 1. `frontend/src/providers/dataProvider.ts`
- `create` 메서드 오버라이드: File 객체 포함 시 FormData로 변환하여 전송
- 기존 JSON 전송 로직 유지 (MARKDOWN/FAQ)

### 2. `frontend/src/pages/contexts/create.tsx`
- 파일 상태 관리: `file`, `fileError` state 추가
- 파일 검증: 100MB 제한, PDF 타입만 허용
- UI 개선: 파일 선택 활성화, 파일명/크기 표시, 에러 메시지

### 3. `frontend/README.md`
- TODO 항목 완료 표시

## Tests
수동 테스트 필요 (E2E 프레임워크 없음):
- PDF 파일 업로드 성공 케이스
- 파일 크기/타입 검증
- 백엔드 API 연동 확인

## Validation
- 백엔드 API 테스트 5개 통과 확인됨 (`test_contexts_write.py`)
- 프론트엔드 코드 lint/typecheck 필요

## Commits
작업 완료 후 커밋 예정
