# Task Summary: Pydantic v2 Modernization

**Slug**: `pydantic-v2-modernization`
**Dates**: 2025-10-01
**Status**: 🔄 In Progress

## Goal
`class Config` → `model_config = ConfigDict()` 전환하여 Pydantic v2 권장 패턴 적용

## Key Changes
- **Files**: `backend/routers/auth.py`, `backend/schemas/admin.py` (2곳)
- **Change**: deprecated `class Config` → `model_config = ConfigDict()`
- **Impact**: Pydantic v3 대비 경고 제거, 현대적 패턴 적용

## Tests
- 86/86 테스트 통과
- 경고 감소: 60 → 57 (-3)
- ruff, mypy 검증 완료

## Commit SHA
11132b4
