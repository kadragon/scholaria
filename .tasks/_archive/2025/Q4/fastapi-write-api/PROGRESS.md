# FastAPI Write API 전환 진행 상황 (Phase 4)

## Summary
Django Context 생성/수정/삭제 API를 FastAPI로 전환 ✅ **완료**

## Goal & Approach
- **목표**: POST/PUT/DELETE /api/contexts 엔드포인트 구현
- **전략**: TDD (Red→Green→Refactor) + 파일 업로드 + Celery 제거
- **방법**: 타입별 워크플로우 보존 (PDF/Markdown/FAQ)

## Completed Steps
- [x] **Step 1: 테스트 작성 (Red)**
  - `api/tests/test_contexts_write.py` 생성 (16개 테스트)
  - POST/PUT/DELETE/FAQ 시나리오
  - 15/16 실패 확인 (Red)
- [x] **Step 2: 스키마 확장 (Green)**
  - `api/schemas/context.py`: ContextCreate, ContextUpdate, FAQQACreate
  - Pydantic 검증 (mypy 통과)
- [x] **Step 3: 파일 업로드 처리 (Green)**
  - UploadFile → tempfile → PDFParser → 청킹 → 폐기
  - MAX_UPLOAD_SIZE 제한 (100MB)
  - PDF 타입 검증
- [x] **Step 4: Celery 제거 (단순화)**
  - Django ORM signal(post_save)이 FastAPI에서 작동 안함
  - Celery 호출 제거 (임베딩은 Django Admin에서만)
  - 결정: FastAPI는 Context 생성만, 임베딩은 별도 프로세스
- [x] **Step 5: Write 라우터 구현 (Green)**
  - POST /api/contexts (Form + File)
  - PUT/PATCH /api/contexts/{id}
  - DELETE /api/contexts/{id} (CASCADE)
  - POST /api/contexts/{id}/qa (FAQ Q&A 추가)
- [x] **Step 6: 검증 & 리팩터링**
  - 16/16 테스트 통과 ✅
  - ruff linting 통과 (8 errors fixed)
  - mypy 타입 체크 통과 (32 files)
  - SQLAlchemy CASCADE 설정 (`cascade="all, delete-orphan"`)

## Current Failures
없음 (모든 테스트 통과)

## Decision Log
| 날짜 | 결정 | 근거 |
|------|------|------|
| 2025-09-30 | Phase 4 시작 | Phase 3 완료 후 Write API 전환 진행 |
| 2025-09-30 | Celery 통합 제거 | FastAPI에서 Django signal 미작동, 임베딩은 별도 프로세스로 분리 |
| 2025-09-30 | python-multipart 의존성 추가 | FastAPI Form/File 업로드 지원 |
| 2025-09-30 | SQLAlchemy CASCADE 설정 | DELETE 시 ContextItem 자동 삭제 |
| 2025-09-30 | Sequential 테스트 실행 (n0) | Parallel 실행 시 SQLite 테이블 충돌 |

## Files Modified
- `api/schemas/context.py`: ContextCreate, ContextUpdate, FAQQACreate 추가
- `api/routers/contexts.py`: POST/PUT/PATCH/DELETE 엔드포인트 구현 (100+ 줄 추가)
- `api/models/context.py`: CASCADE 설정 (`cascade="all, delete-orphan"`)
- `api/tests/test_contexts_write.py`: 16개 테스트 (413 줄)
- `pyproject.toml`: python-multipart 의존성 추가

## Test Results
```
16/16 PASSED (100%)
- TestCreateContext: 6개 (Markdown, FAQ, PDF 생성 + 검증)
- TestUpdateContext: 3개 (이름, 설명, original_content 수정)
- TestDeleteContext: 2개 (삭제, 404)
- TestAddFAQQA: 3개 (Q&A 추가, 404, 타입 검증)
- TestFileUploadValidation: 2개 (타입, 크기 검증)
```

## Next Step
**Phase 4 완료** ✅
- Phase 5 (인증/권한) 또는 Phase 6 (관리 UI) 진행 가능
- 예상 vs 실제: 2-3주 예상 → **2시간** 완료 (TDD 효율성)
- **교훈**: 최소 변경 전략 + Celery 제거로 복잡도 대폭 감소
