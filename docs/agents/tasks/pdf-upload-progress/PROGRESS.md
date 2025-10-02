# Progress: PDF 업로드 진행 상황 표시

## Summary
PDF 업로드 후 polling으로 처리 상태를 실시간 표시하는 기능 구현

## Goal & Approach
- PDF 제출 → `processing_status` polling → "파싱 중...", "완료", "실패" 표시
- 1초 간격 polling, 60초 타임아웃

## Completed Steps
1. `create.tsx`에 polling 로직 추가 완료
   - `pollContextStatus()` 함수로 1초 간격 polling
   - 60초 타임아웃 처리
   - `useEffect` cleanup으로 메모리 누수 방지
2. 상태별 UI 메시지 구현
   - PENDING → "PDF 파싱 중..."
   - COMPLETED → 성공 토스트 + 리스트 이동
   - FAILED → 실패 토스트
3. TypeScript 빌드 성공 (NodeJS.Timeout → number)

## Current Failures
(none)

## Decision Log
- Polling 방식 선택 (WebSocket/SSE 도입 없이 간단하게)
- 동기 처리 유지 (Celery 도입 이번 scope 아님)

## Bonus Fixes
- 청크 목록 내용 미리보기: `truncate` → `line-clamp-3` (다중 행 표시)
- 편집 Dialog 배경: `bg-white` 추가 (배경 사라짐 방지)
- Commit: 64b107a

## Next Step
Manual testing in browser (user can test after deployment)
