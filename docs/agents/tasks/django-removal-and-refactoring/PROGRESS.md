# Progress: Django 제거 및 프로젝트 구조 리팩토링

## Summary
Django 레거시를 FastAPI 중심 모노레포로 전환 중

## Goal & Approach
**Goal**: Django 코드 제거, 폴더 구조 정리 (backend/, frontend/)
**Approach**: 8단계 점진적 리팩토링 (Celery 이동 → Django 제거 → 폴더 재구성 → Docker 업데이트 → 문서 정리)

## Completed Steps
- [x] RESEARCH.md: Django 레거시 분석, 폴더 구조 설계
- [x] PLAN.md: 8단계 상세 계획, 테스트/검증 전략
- [x] Step 1: Celery → FastAPI 서비스
  - [x] `api/services/ingestion.py` 생성 (ingest_document, save_uploaded_file, generate_context_item_embedding)
  - [x] `api/routers/contexts.py` 업데이트 (_process_pdf_upload → ingestion service 사용)
  - [x] `api/routers/admin/bulk_operations.py` 업데이트 (Celery import 제거, 동기 처리)
  - [x] `alembic/env.py` QuestionHistory import 추가
  - [x] `api/tests/test_ingestion_service.py` (6/6 테스트 통과)

## Current Failures
- Django fixture → SQLAlchemy 세션 불일치 (test_contexts.py 3/16 실패)
  - Mitigation: Step 2에서 Django 제거 시 해결 예정 (FastAPI-only 테스트로 전환)

## Decision Log
| 날짜 | 결정 | 근거 |
|------|------|------|
| 2025-10-01 | Celery 유지 (Django 의존성 제거 버전) | 백그라운드 작업(임베딩 재생성)에 필요, FastAPI와 호환 가능 |
| 2025-10-01 | 폴더 구조: backend/, frontend/ | 모노레포 표준 컨벤션, Docker 빌드 컨텍스트 명확화 |

## Next Step
Step 1: Celery 작업을 FastAPI 서비스로 이동 (`api/services/ingestion.py` 생성)
