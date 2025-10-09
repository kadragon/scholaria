# PDF 업로드 진행 상황 표시 (완료)

## 목표
PDF 업로드 후 처리 상태를 실시간으로 표시

## 핵심 변경사항
- **파일**: `frontend/src/pages/contexts/create.tsx`
- **Polling 로직**: 1초 간격, 60초 타임아웃
- **상태별 UI**: PENDING → "PDF 파싱 중...", COMPLETED → 성공 토스트, FAILED → 실패 토스트
- **메모리 관리**: `useEffect` cleanup으로 interval 정리

## 테스트
- Manual test 필요 (브라우저 실제 업로드)

## 커밋
- 963d8af (Polling 로직 + UI 메시지)
