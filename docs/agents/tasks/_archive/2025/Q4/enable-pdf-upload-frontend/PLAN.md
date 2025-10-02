# Plan: Enable PDF Upload in Frontend

## Objective
Activate PDF file upload in Context creation form with proper validation and FormData handling.

## Constraints
- Backend expects `multipart/form-data` with fields: `name`, `description`, `context_type`, `original_content`, `file`
- Max file size: 100MB
- Accept only `application/pdf`
- Use Refine's `useCreate` hook (no custom data provider override needed initially)

## Target Files & Changes

### 1. `frontend/src/pages/contexts/create.tsx`
**Changes:**
- Add `file` state: `useState<File | null>(null)`
- Enable file input (remove `disabled`)
- Add file change handler with validation (size ≤ 100MB, type = PDF)
- Modify `handleSubmit` to construct FormData when `contextType === "PDF" && file`
- Replace message: "PDF 업로드는 다음 단계에서 구현될 예정입니다" → remove or show file name
- Add error state for file validation

### 2. `frontend/src/providers/dataProvider.ts`
**Analysis:** Uses `@refinedev/simple-rest` default provider.
**Decision:** Override `create` method for `contexts` resource to handle FormData.

**Changes:**
- Wrap default provider with custom `create` override
- Detect if `values` contains `File` object → use FormData
- Otherwise, use default JSON behavior

### 3. `frontend/README.md`
**Changes:**
- Mark `[ ] File upload for PDF contexts` as `[x]` (line 77)

## Test/Validation Cases

### Manual Testing (no E2E framework)
1. **Valid PDF upload**
   - Select PDF file < 100MB
   - Fill name/description
   - Submit → verify backend receives multipart request
   - Check Context created with `processing_status: "COMPLETED"`

2. **File size validation**
   - Select file > 100MB → show error, prevent submit

3. **File type validation**
   - Select non-PDF file (e.g., `.txt`) → show error, prevent submit

4. **PDF tab without file**
   - Submit without selecting file → backend returns 400 error, show error message

5. **Markdown/FAQ tabs**
   - Verify non-PDF contexts still work (JSON body)

## Implementation Steps

### Step 1: Update dataProvider for FormData support
- [x] Read current `dataProvider.ts`
- [ ] Override `create` method to detect File objects
- [ ] Construct FormData with all form fields
- [ ] Test with valid PDF upload

### Step 2: Add file state & validation to create.tsx
- [ ] Add `const [file, setFile] = useState<File | null>(null)`
- [ ] Add `const [fileError, setFileError] = useState<string>("")`
- [ ] Create `handleFileChange` with size/type validation
- [ ] Enable file input, bind to state

### Step 3: Modify handleSubmit for FormData
- [ ] Check if `contextType === "PDF"` → construct FormData
- [ ] Append all fields: name, description, context_type, file
- [ ] Pass FormData to `create({ values: formData })`
- [ ] Keep JSON body for MARKDOWN/FAQ

### Step 4: UI polish
- [ ] Remove "구현될 예정입니다" message
- [ ] Show selected file name
- [ ] Display file validation errors
- [ ] Add loading state during upload

### Step 5: Update documentation
- [ ] Mark TODO as complete in `frontend/README.md`

## Rollback
- Revert `create.tsx` changes (re-disable input, restore message)
- Revert `dataProvider.ts` override
- Revert `README.md` checkbox

## Review Hotspots
- **FormData field names** must exactly match backend API contract
- **Content-Type header** should auto-set to `multipart/form-data` (axios handles this)
- **File validation** both client-side (UX) and server-side (security)

## Status
- [ ] Step 1: dataProvider FormData support
- [ ] Step 2: File state & validation
- [ ] Step 3: FormData construction
- [ ] Step 4: UI polish
- [ ] Step 5: Documentation update
