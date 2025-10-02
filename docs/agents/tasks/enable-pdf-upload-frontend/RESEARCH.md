# Research: Enable PDF Upload in Frontend

## Goal
Activate PDF file upload functionality in frontend Context creation form.

## Scope
- `frontend/src/pages/contexts/create.tsx` - Enable file input, add upload logic
- Update `frontend/README.md` TODO list

## Related Files
- **Backend API**: `backend/routers/contexts.py:62-114` - `/contexts` POST endpoint (multipart/form-data)
- **Frontend Form**: `frontend/src/pages/contexts/create.tsx:93-100` - Currently disabled PDF input
- **Data Provider**: `frontend/src/providers/dataProvider.ts` - REST client (needs FormData support check)

## Current State Analysis

### Backend (✅ Fully implemented)
```python
# backend/routers/contexts.py:62-82
@router.post("/contexts", ...)
def create_context(
    name: str = Form(...),
    description: str = Form(...),
    context_type: str = Form(...),
    original_content: str | None = Form(None),
    file: UploadFile | None = File(None),  # ← PDF upload ready
    db: Session = Depends(get_db),
) -> Context:
    if context_type == "PDF" and not file:
        raise HTTPException(400, "File upload required for PDF")
    if context_type == "PDF" and file.content_type != "application/pdf":
        raise HTTPException(400, "Only PDF files supported")
    # ... _process_pdf_upload() handles parsing/chunking
```

**Validation:**
- Max size: 100MB (`MAX_UPLOAD_SIZE`)
- Content-Type: `application/pdf`
- Processing: Docling parser → PDF chunker → embeddings

### Frontend (❌ Disabled)
```tsx
// frontend/src/pages/contexts/create.tsx:96-98
<Input id="pdf" type="file" accept=".pdf" disabled />
<p className="text-sm text-muted-foreground mt-2">
  PDF 업로드는 다음 단계에서 구현될 예정입니다.
</p>
```

**Missing logic:**
1. File state management (`useState<File | null>`)
2. FormData construction (multipart/form-data)
3. File size/type validation
4. Upload progress/error handling

### Data Provider Check
```typescript
// frontend/src/providers/dataProvider.ts
```
Need to verify if `create()` supports FormData or requires custom implementation.

## Hypotheses
1. **H1**: Refine's default data provider handles FormData automatically
2. **H2**: Need custom `create` override for file uploads
3. **H3**: Backend API contract matches FormData field names (`name`, `description`, `context_type`, `file`)

## Evidence
- Backend expects `multipart/form-data` (FastAPI `File()` + `Form()`)
- Frontend uses Refine's `useCreate()` hook
- No existing file upload examples in codebase

## Open Questions
1. Does `dataProvider.create()` auto-detect FormData?
2. Should we add upload progress indicator?
3. Client-side file size validation before upload?

## Risks
- **Low**: Backend API stable, 5 passing tests for PDF upload
- **Medium**: FormData compatibility with Refine data provider (needs verification)

## Next Steps
1. Read `dataProvider.ts` to check FormData support
2. Plan implementation strategy (state + FormData construction)
3. Add file validation logic (size/type)
4. Update form to enable file input
