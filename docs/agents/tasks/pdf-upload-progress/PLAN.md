# Plan: PDF 업로드 진행 상황 표시

## Objective
PDF 업로드 후 polling으로 `processing_status`를 체크하여 "파싱 중...", "완료", "실패" 등 상태를 실시간 표시

## Constraints
- WebSocket/SSE 도입 금지 (간단함 유지)
- 기존 `processing_status` 필드 활용
- Celery 도입 없이 동기 처리 유지 (이번 scope)

## Target Files & Changes

### `frontend/src/pages/contexts/create.tsx`
1. PDF 제출 → context 생성 응답 받음 (status=PENDING)
2. `context_id`로 GET `/api/contexts/{id}` polling 시작 (1초 간격)
3. `processing_status` 값에 따라 메시지 표시:
   - `PENDING` → "PDF 파싱 중..."
   - `COMPLETED` → "완료" → list로 이동
   - `FAILED` → "실패" → 에러 토스트
4. 최대 60초 polling 후 타임아웃

### `backend/routers/contexts.py`
- 변경 없음 (이미 `processing_status` 설정 중)

## Test/Validation Cases
1. **Manual Test**: PDF 업로드 → 브라우저에서 "파싱 중..." 표시 확인
2. **Edge**: 큰 PDF (50MB+) → 타임아웃 처리 확인
3. **Error**: 잘못된 PDF → "실패" 메시지 확인

## Steps
1. [ ] `create.tsx`에 polling 로직 추가
2. [ ] 상태별 메시지 UI 구현
3. [ ] Manual test 수행
4. [ ] 타임아웃 처리 확인

## Rollback
- Git revert to previous commit

## Review Hotspots
- Polling interval (1초 적절한지)
- 타임아웃 60초 충분한지
- 메모리 누수 (interval cleanup)

## Status
- [x] Step 1: Polling 로직 추가
- [x] Step 2: UI 메시지 구현
- [ ] Step 3: Manual test
- [ ] Step 4: 타임아웃 확인
