# Task Summary: Topic Slug Feature

## Goal
Add URL-friendly slug to Topic model (e.g., "코러스" → "korus").

## Key Changes
- **Model:** Added `slug` field (String(50), unique, indexed) to `Topic` model
- **Auto-generation:** SQLAlchemy event auto-generates slugs from topic name
- **Romanization:** Uses `korean-romanizer` for Korean→Latin conversion
- **API:** New endpoint `GET /api/topics/slug/{slug}`
- **Migration:** `0002_add_topic_slug.py` with backfill logic
- **Backward compat:** ID-based routes still work

## Tests
- 13 new tests: slug generation, uniqueness, retrieval
- All 40 topic/slug tests passing
- Lint (ruff) and type checks (mypy) clean

## Commit
`9fdf043` - [Behavioral] Add topic slug feature for URL-friendly links

## Dependencies
- Added `korean-romanizer>=0.28.0` to `pyproject.toml`
