# Research: Celery Monitoring with Flower

## Goal
Add Flower monitoring dashboard for Celery workers

## Scope
- Add Flower service to Docker Compose
- Configure authentication
- Document access & usage

## Related Files/Flows
- `docker-compose.yml` (add flower service)
- `docker-compose.dev.yml` (dev overrides if needed)
- `backend/celery_app.py` (celery config)
- `backend/tasks/embeddings.py` (current tasks)

## Hypotheses

### H1: Flower as separate service
**Hypothesis**: Run Flower in dedicated container alongside celery-worker
**Evidence**:
- Flower official image: `mher/flower`
- Needs access to Redis broker
- Web UI on port 5555 (standard)

### H2: Authentication required
**Hypothesis**: Flower should have basic auth in production
**Evidence**:
- Flower supports `--basic_auth=user:password`
- Environment variable: `FLOWER_BASIC_AUTH`

### H3: Minimal configuration
**Hypothesis**: Default Flower settings sufficient for MVP
**Evidence**:
- Auto-discovers Celery app via broker URL
- No additional Celery config needed

## Evidence

### Current Celery Setup
- **Broker**: Redis (`redis://redis:6379/0`)
- **Backend**: Same Redis
- **Worker**: `celery-worker` service in docker-compose.yml
- **Tasks**: `backend.tasks.embeddings` (regenerate_embeddings_task)

### Flower Docker Image
```yaml
flower:
  image: mher/flower:2.0
  command: celery --broker=redis://redis:6379/0 flower
  ports:
    - "5555:5555"
  environment:
    - FLOWER_BASIC_AUTH=admin:${FLOWER_PASSWORD:-flower}
  depends_on:
    - redis
    - celery-worker
```

## Assumptions
1. Flower 2.0 is stable & compatible with Celery 5.x
2. No custom Flower configuration needed initially
3. Basic auth sufficient for security (not exposed publicly)

## Open Questions
1. Should Flower run in dev only or also prod?
   → **Answer**: Both (but with strong password in prod)
2. Persistent data needed?
   → **Answer**: No (stateless, queries Redis directly)
3. Nginx reverse proxy needed?
   → **Answer**: Optional (can add `/flower` route later)

## Risks
- **Low**: Adding read-only monitoring service
- **Medium**: Weak password → security risk
  - **Mitigation**: Require strong password via env var

## Next
Proceed to PLAN
