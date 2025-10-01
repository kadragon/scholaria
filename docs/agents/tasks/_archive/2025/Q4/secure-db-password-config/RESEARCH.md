# Goal
Ensure database password handling avoids hard-coded defaults that trigger secret scanners while keeping local development workflows intact.

# Scope
- `backend/config.py`
- Associated tests under `backend/tests`
- Relevant environment documentation references (if updates needed)

# Related Files/Flows
- FastAPI settings via `Settings` (Pydantic BaseSettings)
- Database URL construction in `Settings.database_config`
- Docker Compose env defaults (`docker-compose.dev.yml`, `docker-compose.prod.yml`)

# Hypotheses
- Hard-coded fallback `DB_PASSWORD="postgres"` violates secret scanning policies.
- Removing the default may break local dev unless URL builder handles missing password.
- Tests currently do not cover password omission behavior.

# Evidence
- `backend/config.py` line 25 defines `DB_PASSWORD: str = Field(default="postgres")`.
- GitGuardian flagged this literal as a credential in source control.
- `backend/tests/test_config.py` lacks assertions around password defaults or URL formatting.

# Assumptions/Open Qs
- Acceptable to require explicit password env var in production (existing documentation already encourages setting it).
- Local development can fall back to Docker-provided env (`POSTGRES_PASSWORD`) without code default.

# Sub-agent Findings
- None.

# Risks
- Removing default might produce invalid URLs (`: @`) if not handled.
- Tests or runtime relying on `settings.DB_PASSWORD` may expect non-empty string.

# Next
- Draft plan to change `DB_PASSWORD` default to empty/optional and adjust URL builder accordingly.
- Define tests covering missing password and explicit password encoding.
