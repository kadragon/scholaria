# Task Summary: Schema Pattern Documentation

**Slug:** `schema-pattern-docs`
**Created:** 2025-10-01
**Status:** ✅ Complete

## Goal

Pydantic schema 사용 패턴 문서화 및 개발자 가이드 작성

## Key Changes

### Files Created
- `backend/schemas/README.md` - 전체 스키마 패턴 가이드

### Documentation Added
1. **ConfigDict + ORM 매핑**: `from_attributes=True` 사용 규칙
2. **Datetime 직렬화**: `@field_serializer` + `to_local_iso()` 패턴
3. **Field 검증**: `Field(...)` 제약 조건 사용법
4. **Alias 패턴**: `populate_by_name=True` + `Field(alias=...)`
5. **Base 스키마**: 공통 필드 재사용 전략
6. **스키마 타입별 목적**: Output/Create/Update/List/Request-Response
7. **테스트 패턴**: Validation, ORM mapping, Serialization 검증
8. **체크리스트**: 새 스키마 작성 시 확인 항목

### AGENTS.md Update
- `/docs/agents/AGENTS.md`에 Pydantic 스키마 패턴 섹션 추가
- 주요 규칙 요약 및 `backend/schemas/README.md` 참조 링크

## Tests

문서 작성만 해당 - 코드 변경 없음

## Commits

None (documentation only)
