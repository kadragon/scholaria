# Research: FastAPI Write API 전환

## Goal
Django Context 생성/수정/삭제 로직을 FastAPI로 전환 (파일 업로드, Celery 통합 포함)

## Scope
- POST /api/contexts (파일 업로드, 타입별 워크플로우)
- PUT/PATCH /api/contexts/{id}
- DELETE /api/contexts/{id}
- POST /api/contexts/{id}/qa (FAQ Q&A 추가)

## Related Files/Flows

### Django Write Logic
- **`rag/admin.py:106-158`**: ContextForm (파일 업로드 처리)
- **`rag/models.py:88-246`**: Context.process_pdf_upload(), process_markdown_update(), add_faq_qa_pair()
- **`rag/views.py`**: 읽기 전용, Write는 Django Admin에서만 처리
- **`rag/tasks.py`**: Celery 작업 (process_context_task, generate_embeddings_task)
- **`rag/ingestion/parsers.py`**: PDFParser, MarkdownParser
- **`rag/ingestion/chunkers.py`**: TextChunker
- **`rag/storage.py`**: MinIOStorage (현재 미사용, 파일 폐기 방식)

### FastAPI 기존 구조
- **`api/models/context.py`**: Context, ContextItem SQLAlchemy 모델
- **`api/schemas/context.py`**: ContextOut, ContextListOut (읽기 전용)
- **`api/routers/contexts.py`**: GET /api/contexts, GET /api/contexts/{id}

## Hypotheses

### H1: Django Admin 로직을 FastAPI 라우터로 직접 포팅 가능
- **근거**: Phase 3 (RAG)에서 sync_to_async로 Django ORM 호출 성공
- **검증**: ContextForm.save() → FastAPI endpoint 직접 변환

### H2: Celery 통합은 Django와 FastAPI가 공유 가능
- **근거**: Celery는 프레임워크 독립적 (Redis/RabbitMQ만 필요)
- **검증**: FastAPI에서 `rag.tasks.process_context_task.delay()` 호출

### H3: 파일 업로드는 UploadFile → 임시 파일 → 파싱 → 폐기
- **근거**: `rag/models.py:88-134` (process_pdf_upload 워크플로우)
- **검증**: `UploadFile.file` → `tempfile.NamedTemporaryFile` → PDFParser

## Evidence

### Django Context 생성 워크플로우 (admin.py:199-258)
```python
def save_model(self, request, obj, form, change):
    super().save_model(request, obj, form, change)
    uploaded_file = form.cleaned_data.get("uploaded_file")

    if uploaded_file and obj.context_type == "PDF":
        success = obj.process_pdf_upload(uploaded_file)
        # processing_status = "COMPLETED" or "FAILED"
```

### process_pdf_upload 내부 (models.py:88-134)
```python
def process_pdf_upload(self, uploaded_file) -> bool:
    # 1. 임시 파일 저장
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
        for chunk in uploaded_file.chunks():
            tmp_file.write(chunk)

    # 2. 파싱
    parser = PDFParser()
    text = parser.parse_file(temp_path)

    # 3. 청킹
    chunker = TextChunker()
    chunks = chunker.chunk_text(text)

    # 4. DB 저장 (ContextItem.objects.create)
    for idx, chunk in enumerate(chunks):
        ContextItem.objects.create(context=self, title=f"Chunk {idx+1}", content=chunk)

    # 5. 임시 파일 삭제
    Path(temp_path).unlink()

    # 6. 상태 업데이트
    self.processing_status = "COMPLETED"
    self.update_chunk_count()
```

### Celery 사용 (현재 Django)
- **tasks.py**: `process_context_task`, `generate_embeddings_task`
- **호출**: `process_context_task.delay(context_id)`
- **검증**: FastAPI에서도 동일한 Celery 태스크 재사용 가능

## Assumptions/Open Qs

### 가정
1. **동기 처리 vs Celery**: 파일 업로드는 동기, 임베딩 생성은 비동기 (Celery)
2. **트랜잭션**: SQLAlchemy AsyncSession은 Django ORM과 별개 트랜잭션
3. **파일 검증**: Django FileValidator → FastAPI에서 동일 로직 재사용

### 열린 질문
1. **Q: FastAPI에서 Celery 태스크 호출 시 Django ORM 의존성은?**
   - A: Celery 워커는 Django 환경에서 실행되므로, 태스크 내부는 Django ORM 사용 가능
2. **Q: 파일 업로드 크기 제한?**
   - A: FastAPI `UploadFile` 기본 제한 없음, Nginx/Uvicorn 설정 필요
3. **Q: 동시 업로드 시 Celery 큐 관리?**
   - A: Celery 워커 수로 제어 (현재 구성 유지)

## Sub-agent Findings
없음 (단일 에이전트로 충분)

## Risks

### High
- **트랜잭션 격리**: FastAPI (SQLAlchemy) ↔ Celery (Django ORM) 동시 업데이트 시 충돌 가능
  - **완화**: 상태 업데이트는 Celery에서만 처리

### Medium
- **파일 크기**: 대용량 PDF 업로드 시 메모리/시간 초과
  - **완화**: Nginx `client_max_body_size`, Uvicorn `--timeout-keep-alive`

### Low
- **타입별 워크플로우**: PDF/Markdown/FAQ 각각 다른 로직
  - **완화**: 별도 서비스 함수 분리

## Next
**PLAN.md** 작성 → 파일별 변경 계획, 테스트 케이스, 단계별 구현
