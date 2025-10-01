# FastAPI Write API 전환 계획 (Phase 4)

## Objective
Django Context 생성/수정/삭제 API → FastAPI로 전환

## Constraints
- TDD 원칙 (테스트 우선)
- 파일 업로드 워크플로우 보존 (PDF → 파싱 → 폐기)
- Celery 비동기 작업 유지
- 기존 테스트 통과 유지

## Target Files & Changes

### 1. Write Routers (`api/routers/`)
- **contexts.py 확장**:
  - POST /api/contexts (Context 생성)
  - PUT /api/contexts/{id} (Context 수정)
  - DELETE /api/contexts/{id} (Context 삭제)
  - POST /api/contexts/{id}/qa (FAQ Q&A 추가)

### 2. File Upload (`api/routers/contexts.py`)
- FastAPI `UploadFile` 처리
- 임시 파일 저장 → Celery 작업 트리거 → 파일 삭제
- 타입별 워크플로우:
  - PDF: 파일 업로드 → `ingest_pdf_document` task
  - Markdown: 텍스트 입력 → DB 저장
  - FAQ: Q&A 입력 → DB 저장

### 3. Celery Integration (`api/services/celery_service.py`)
- Celery task 호출 (Django와 동일한 워커 사용)
- Task status 조회
- Task 취소

### 4. Schemas (`api/schemas/context.py` 확장)
- ContextCreateRequest (타입별 필드)
- ContextUpdateRequest
- FAQItemCreate (Q&A 추가용)
- FileUploadResponse (처리 상태)

### 5. Tests (`api/tests/test_contexts_write.py`)
- Context 생성 (PDF, Markdown, FAQ)
- Context 수정 (original_content, 메타데이터)
- Context 삭제
- FAQ Q&A 추가
- 파일 업로드 워크플로우
- Celery 작업 트리거 확인

## Test/Validation Cases

### Unit Tests
- [ ] ContextCreateRequest 스키마 검증 (타입별)
- [ ] UploadFile 처리 (임시 저장, 삭제)
- [ ] Celery task 호출 (mock)

### Integration Tests
- [ ] POST /api/contexts (PDF 업로드) → 200
- [ ] POST /api/contexts (Markdown) → 200
- [ ] POST /api/contexts (FAQ) → 200
- [ ] PUT /api/contexts/{id} → 200
- [ ] DELETE /api/contexts/{id} → 204
- [ ] POST /api/contexts/{id}/qa → 200
- [ ] Django vs FastAPI 응답 동등성 (생성/수정)

### Edge Cases
- [ ] 잘못된 파일 타입 업로드 (400)
- [ ] 파일 크기 초과 (413)
- [ ] 존재하지 않는 Context 수정/삭제 (404)
- [ ] Celery 작업 실패 처리

## Steps

### Step 1: 테스트 작성 (Red)
- [ ] `api/tests/test_contexts_write.py` 생성
- [ ] POST /api/contexts 테스트 (PDF, Markdown, FAQ)
- [ ] PUT, DELETE 테스트

### Step 2: 스키마 확장 (Green)
- [ ] `api/schemas/context.py` 확장
- [ ] ContextCreateRequest (타입별)
- [ ] ContextUpdateRequest, FAQItemCreate

### Step 3: 파일 업로드 처리 (Green)
- [ ] UploadFile → 임시 파일 저장 로직
- [ ] 파일 검증 (타입, 크기)

### Step 4: Celery 통합 (Green)
- [ ] Django Celery 설정 재사용 확인
- [ ] FastAPI에서 Celery task 호출
- [ ] Task status 조회 API

### Step 5: Write 라우터 구현 (Green)
- [ ] POST /api/contexts (타입별 분기)
- [ ] PUT /api/contexts/{id}
- [ ] DELETE /api/contexts/{id}
- [ ] POST /api/contexts/{id}/qa

### Step 6: 검증 & 리팩터링 (Refactor)
- [ ] 모든 테스트 통과
- [ ] Django vs FastAPI 동등성 확인
- [ ] 코드 리뷰 (중복 제거, 명확성)

## Rollback
- FastAPI write 라우터 제거 → Django endpoint 계속 사용
- DB 변경 없음 (동일한 Django ORM 사용)
- Celery 워커는 양쪽 모두 지원

## Review Hotspots

### 주의 필요
1. **파일 업로드**: FastAPI `UploadFile` vs Django `request.FILES`
2. **Celery 작업**: FastAPI에서 Django task 호출 (프로젝트 설정)
3. **트랜잭션**: SQLAlchemy vs Django ORM 트랜잭션
4. **타입별 워크플로우**: PDF/Markdown/FAQ 분기 로직

### 성능
- 파일 업로드: 스트리밍 vs 메모리 로드
- Celery 비동기: 응답 즉시 반환

## Risks

### High
- **Celery 호환성**: FastAPI에서 Django Celery task 호출 실패 가능
- **파일 처리**: 임시 파일 경로, 권한, 정리 실패

### Medium
- **타입별 분기**: 복잡한 조건 로직 → 버그 가능성
- **트랜잭션 관리**: SQLAlchemy와 Django ORM 혼용 시 문제

### Low
- 스키마 검증 (Pydantic이 강력함)

## Status

- [ ] Step 1: 테스트 작성
- [ ] Step 2: 스키마 확장
- [ ] Step 3: 파일 업로드 처리
- [ ] Step 4: Celery 통합
- [ ] Step 5: Write 라우터 구현
- [ ] Step 6: 검증 & 리팩터링
