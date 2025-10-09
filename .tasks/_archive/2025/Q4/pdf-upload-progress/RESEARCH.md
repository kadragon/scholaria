# Research: PDF 업로드 진행 상황 표시

## Goal
PDF 업로드 시 "생성중..."만 표시되는 문제를 해결하고, 파싱/청킹 진행 상황을 사용자에게 보여준다.

## Scope
- `frontend/src/pages/contexts/create.tsx` - 업로드 UI
- `backend/routers/contexts.py` - `create_context`, `_process_pdf_upload`
- `backend/models/context.py` - `processing_status` 필드

## Related Files & Flows

### Frontend
- `frontend/src/pages/contexts/create.tsx:180` - "생성 중..." 표시
- Form submit → POST `/api/contexts` → 응답 대기 (sync)

### Backend
- `backend/routers/contexts.py:58` - `create_context()`
  - DB에 Context 생성 (`processing_status="PENDING"`)
  - `_process_pdf_upload()` 호출 (동기 실행)
  - 완료 후 `processing_status="COMPLETED"` or `"FAILED"`
- `backend/routers/contexts.py:117` - `_process_pdf_upload()`
  - PDF 파싱 → 청킹 → DB 저장
  - 동기 블로킹 처리

### Model
- `backend/models/context.py` - `Context.processing_status` 필드 (PENDING/COMPLETED/FAILED)

## Hypotheses
1. **WebSocket/SSE 없이 polling으로 상태 체크** - 가장 간단한 방법
2. **Celery task로 비동기 처리** - 더 정교하지만 복잡도 증가
3. **Streaming response** - FastAPI StreamingResponse 사용

## Evidence
- 현재 Celery는 임베딩 재생성에만 사용 중 (`backend/tasks/embeddings.py`)
- `processing_status` 필드가 이미 존재하여 polling 가능
- 사용자는 "파싱 중...", "청킹 중..." 등 세부 단계를 보고 싶어함

## Assumptions
- PDF 처리는 수 초~수십 초 소요 (100MB 이하)
- Polling interval 1~2초로 충분
- 처리 실패 시 에러 메시지 표시 필요

## Open Questions
- 세부 진행률(%) 표시 vs 단계별 텍스트?
- Celery task로 전환할지, 동기 유지할지?

## Risks
- Polling 오버헤드 (미미함)
- 동기 처리 시 타임아웃 가능성 (큰 PDF)

## Next
Plan으로 이동 - **Polling 방식** 선택 (가장 빠르고 간단)
