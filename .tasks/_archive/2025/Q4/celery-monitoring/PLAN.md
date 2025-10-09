# Plan: Celery Monitoring with Flower

## Objective
Add Flower web dashboard for monitoring Celery workers, tasks, and queues

## Constraints
- Use official `mher/flower` Docker image
- Basic authentication required
- No modifications to existing Celery configuration

## Target Files & Changes

### 1. `docker-compose.yml`
**Add Flower service** (after celery-worker):
```yaml
flower:
  image: mher/flower:2.0
  command: celery --broker=redis://redis:6379/0 flower --port=5555
  ports:
    - "5555:5555"
  environment:
    - FLOWER_BASIC_AUTH=${FLOWER_USER:-admin}:${FLOWER_PASSWORD:-flower}
  depends_on:
    - redis
    - celery-worker
```

### 2. `.env.example`
**Add Flower credentials**:
```
# Flower (Celery monitoring)
FLOWER_USER=admin
FLOWER_PASSWORD=change_this_in_production
```

### 3. `docker-compose.dev.yml`
**No changes** (dev uses same Flower config)

### 4. `README.md`
**Add Flower section** (after Celery section):
```markdown
### Celery Monitoring (Flower)
Access Flower dashboard at http://localhost:5555
- Username: `admin` (default, set via FLOWER_USER)
- Password: `flower` (default, set via FLOWER_PASSWORD)
```

### 5. `docs/DEPLOYMENT.md`
**Add production notes**:
```markdown
## Flower Security
Set strong credentials in production:
FLOWER_USER=admin
FLOWER_PASSWORD=<strong-random-password>
```

## Test/Validation Cases

### Manual Tests
1. **Start services**: `docker compose up -d`
2. **Access Flower**: http://localhost:5555
3. **Verify auth**: Enter username/password
4. **Check workers**: Workers tab shows 1 active worker
5. **Trigger task**: Upload PDF → see task in Tasks tab
6. **Check metrics**: Monitor tab shows task stats

### Edge Cases
1. **Wrong credentials**: Should show 401 error
2. **Worker down**: Flower shows 0 workers
3. **No tasks**: Empty task list (not an error)

## Steps
1. [ ] Add `flower` service to docker-compose.yml
2. [ ] Update `.env.example` with FLOWER credentials
3. [ ] Update README.md with access instructions
4. [ ] Update docs/DEPLOYMENT.md with security notes
5. [ ] Test locally: `docker compose up -d` → verify Flower access
6. [ ] Trigger test task (PDF upload) → verify task appears in Flower
7. [ ] Commit changes

## Rollback
- Remove `flower` service from docker-compose.yml
- Remove env vars from .env.example

## Review Hotspots
- **Security**: FLOWER_PASSWORD must be strong in production
- **Port conflict**: 5555 may conflict (unlikely)
- **Resource usage**: Flower is lightweight (~50MB RAM)

## Status
- [x] Step 1: Add flower service
- [x] Step 2: Update .env.example
- [x] Step 3: Update README.md
- [x] Step 4: Update DEPLOYMENT.md
- [ ] Step 5: Manual test
- [ ] Step 6: Trigger task test
- [ ] Step 7: Commit
