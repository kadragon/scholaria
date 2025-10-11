---
id: AG-POLICY-SCHEMA-GUIDELINES-001
version: 1.0.0
scope: global
status: active
supersedes: []
depends: [AG-POLICY-DEV-GUARDRAILS-001]
last-updated: 2025-10-11
owner: team-admin
---
# Pydantic Schema Guidelines

## Authoring Rules
- Group schemas by domain within `backend/schemas/`; avoid cross-module imports that break layering.
- Enable `ConfigDict(from_attributes=True)` for ORM compatibility across all response schemas.
- Use `populate_by_name=True` when exposing camelCase aliases alongside snake_case internals.

## Serialization Helpers
- Prefer shared utilities from `backend.schemas.utils`, especially `to_local_iso()` for date-time formatting.
- Validate field constraints via `Field` definitions instead of ad-hoc validators whenever possible.

## Change Management
- Update dependent tests whenever schema aliases or required fields change.
- Document breaking schema updates inside the corresponding `.spec/` contract before implementation.
