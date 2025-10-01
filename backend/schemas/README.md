# Pydantic Schema Patterns

This document outlines conventions and patterns used in Scholaria's Pydantic schemas.

## Directory Structure

```
backend/schemas/
├── __init__.py
├── admin.py          # Admin API schemas (Refine panel)
├── context.py        # Context/ContextItem schemas
├── history.py        # QuestionHistory schemas
├── rag.py            # RAG endpoint schemas (Question/Answer)
├── topic.py          # Topic schemas
└── utils.py          # Shared serialization utilities
```

## Core Patterns

### 1. ConfigDict with ORM Mapping

**Use `ConfigDict(from_attributes=True)` for all output schemas** that map from SQLAlchemy models.

```python
from pydantic import BaseModel, ConfigDict

class ContextOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    # ...
```

**When to use:**
- All `*Out` schemas (e.g., `TopicOut`, `ContextOut`, `QuestionHistoryOut`)
- Schemas returned from database queries

**Why:**
- Enables automatic conversion from ORM models to Pydantic models
- Replaces deprecated `class Config: orm_mode = True` (Pydantic v1)

### 2. Datetime Serialization

**Use `@field_serializer` + `to_local_iso()` for all datetime fields** in output schemas.

```python
from datetime import datetime
from pydantic import field_serializer
from backend.schemas.utils import to_local_iso

class ContextOut(BaseModel):
    created_at: datetime
    updated_at: datetime

    @field_serializer("created_at", "updated_at")
    def serialize_datetime(self, value: datetime) -> str:
        return to_local_iso(value)
```

**Implementation:**
- `to_local_iso()` converts naive datetimes to UTC, then formats as ISO 8601
- Returns timezone-aware ISO strings (e.g., `2025-01-15T10:30:00+00:00`)

**When to apply:**
- All `*Out` schemas with datetime fields
- Currently applied: `ContextOut`, `ContextItemOut`, `TopicOut`, `QuestionHistoryOut`
- **Not yet applied** (backlog): `AdminTopicOut`, `AdminContextOut`

### 3. Field Aliases

**Use `Field(alias=...)` + `populate_by_name=True`** when API field names differ from model attributes.

```python
from pydantic import BaseModel, ConfigDict, Field

class QuestionHistoryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: int
    topic: int = Field(alias="topic_id")  # Maps topic_id → topic
    question: str
```

**When to use:**
- API response needs different field name than database column
- Frontend expects camelCase but backend uses snake_case

**Currently used:**
- `QuestionHistoryOut.topic` (maps from `topic_id`)

### 4. Validation with Field Constraints

**Use `Field(...)` for input validation** on create/update schemas.

```python
from pydantic import BaseModel, Field

class AdminTopicCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    description: str = Field(default="")
    system_prompt: str = Field(min_length=1)
    context_ids: list[int] = Field(default_factory=list)
```

**Common patterns:**
- **Required strings:** `Field(min_length=1)` (prevents empty strings)
- **Optional with defaults:** `Field(default="")` or `Field(default_factory=list)`
- **Numeric constraints:** `Field(gt=0)` for positive integers
- **Descriptions:** `Field(description="...")` for API documentation

### 5. Base Schemas for Reusability

**Define `*Base` schemas** for shared fields across create/update/output schemas.

```python
class ContextBase(BaseModel):
    name: str
    description: str
    context_type: str

class ContextOut(ContextBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    created_at: datetime
    updated_at: datetime

class ContextCreate(BaseModel):
    name: str
    description: str
    context_type: str
```

**Why:**
- Reduces duplication
- Centralizes field definitions
- Makes updates easier

## Schema Types by Purpose

### Output Schemas (`*Out`)
- **Purpose:** API responses, database → JSON
- **Patterns:** `ConfigDict(from_attributes=True)`, `@field_serializer`, `Field(alias=...)`
- **Examples:** `TopicOut`, `ContextOut`, `QuestionHistoryOut`

### Create Schemas (`*Create`)
- **Purpose:** POST request bodies
- **Patterns:** `Field(...)` validation, required fields
- **Examples:** `AdminTopicCreate`, `ContextCreate`, `FAQQACreate`

### Update Schemas (`*Update`)
- **Purpose:** PUT/PATCH request bodies (partial updates)
- **Patterns:** All fields `Optional`, `Field(None, ...)` validation
- **Examples:** `AdminTopicUpdate`, `ContextUpdate`

### List Response Schemas
- **Purpose:** Paginated list endpoints (Refine format)
- **Pattern:** `data: list[*Out]` + `total: int`
- **Examples:** `TopicListResponse`, `ContextListResponse`

### Request/Response Pairs
- **Purpose:** Non-CRUD operations (bulk, RAG)
- **Examples:**
  - `QuestionRequest` / `AnswerResponse`
  - `BulkAssignContextRequest` / `BulkAssignContextResponse`

## Testing Patterns

All schemas should be tested for:
1. **Validation:** Invalid inputs raise ValidationError
2. **ORM mapping:** SQLAlchemy models serialize correctly
3. **Serialization:** Datetime/alias fields format as expected
4. **Edge cases:** Empty strings, null values, boundary conditions

Example:
```python
def test_context_out_from_orm(db_session):
    context = Context(name="Test", description="Desc", context_type="PDF")
    db_session.add(context)
    db_session.commit()

    schema = ContextOut.model_validate(context)
    assert schema.name == "Test"
    assert isinstance(schema.created_at, str)  # ISO format
```

## Checklist for New Schemas

- [ ] Use `ConfigDict(from_attributes=True)` for `*Out` schemas
- [ ] Add `@field_serializer` for datetime fields (use `to_local_iso()`)
- [ ] Apply `Field(...)` validation on `*Create`/`*Update` schemas
- [ ] Use `*Base` classes to reduce duplication
- [ ] Document with docstrings if non-obvious
- [ ] Write unit tests for validation and serialization

## Future Improvements

1. **Admin datetime serializers** (Breaking change):
   - Apply `@field_serializer` to `AdminTopicOut`, `AdminContextOut`
   - Requires frontend compatibility check
2. **Schema validation docs**:
   - Add examples for complex validation (custom validators, model validators)
3. **OpenAPI customization**:
   - Examples of `Field(json_schema_extra={...})` for API docs
