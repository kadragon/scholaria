# Plan: Documentation Update & Project Cleanup

## Objective
FastAPI 전환 완료 반영 - 문서 업데이트 및 Django 레거시 정리

## Constraints
- 중요 정보 보존
- 배포 가이드 정확성 유지
- 개발자 온보딩 경험 개선

## Target Files & Changes

### 1. 프로젝트 정리
**제거 대상**:
- `media/` (빈 폴더, Django MEDIA_ROOT)
- `storage/` (빈 폴더, MinIO 제거 후)
- `uploads/` (Django FileField 테스트 파일 11개)
- `tmp/` (캐시 폴더)
- `test_write.db` (pytest 생성 DB)

**gitignore 추가**:
```
# Test artifacts
test_*.db
*.db
.coverage

# Django legacy (removed)
media/
storage/
uploads/
tmp/
```

### 2. README.md 업데이트
**제거**:
- L5: "⚠️ MIGRATION IN PROGRESS" 배너
- L28-46: Django 서버 실행 가이드
- L41-51: Django Admin, hybrid runtime 언급
- L84-98: Django 마이그레이션 명령어
- L100+: Django 언급 섹션

**추가/수정**:
- L5: "✅ FastAPI 전용 시스템" 명시
- 기술 스택 섹션: FastAPI + SQLAlchemy + Refine 강조
- 테스트 명령어: `uv run pytest backend/tests/`
- 서버 실행: `uvicorn backend.main:app --reload`
- 환경변수: JWT 설정 추가
- Admin 접근: `/admin` (Refine Panel)

### 3. docs/DEPLOYMENT.md 업데이트
**확인 후 수정**:
- Django wsgi → FastAPI uvicorn
- Nginx 설정 (이미 반영되었을 수 있음)
- 환경 변수 (JWT_SECRET_KEY, FASTAPI_ALLOWED_ORIGINS)
- Docker Compose 프로덕션 설정

### 4. docs/ARCHITECTURE_DECISIONS.md 추가
**새 섹션**:
- ADR: Django → FastAPI 전환 (동기, 결정, 결과)
- 기술 스택 변경 (Django ORM → SQLAlchemy, Django Admin → Refine)

## Test/Validation
1. README 명령어 실행 테스트
2. 삭제된 폴더 복원 불필요 확인
3. .gitignore 동작 확인

## Steps
- [x] Step 1: Research 완료
- [x] Step 2: Plan 완료
- [ ] Step 3: 폴더/파일 정리
- [ ] Step 4: .gitignore 업데이트
- [ ] Step 5: README.md 업데이트
- [ ] Step 6: DEPLOYMENT.md 검토 & 업데이트
- [ ] Step 7: ARCHITECTURE_DECISIONS.md 업데이트
- [ ] Step 8: 커밋

## Rollback
```bash
git checkout README.md docs/DEPLOYMENT.md docs/ARCHITECTURE_DECISIONS.md .gitignore
git clean -fd media/ storage/ uploads/ tmp/
```

## Review Hotspots
- **uploads/ 삭제**: 중요 파일 없음 확인 완료 (테스트 더미 파일만)
- **README 명령어**: 실행 가능 여부 검증
- **DEPLOYMENT.md**: 프로덕션 배포 정확성

## Status
- [x] Step 1: Research
- [x] Step 2: Plan
- [ ] Step 3: 폴더/파일 정리
- [ ] Step 4: .gitignore
- [ ] Step 5: README.md
- [ ] Step 6: DEPLOYMENT.md
- [ ] Step 7: ARCHITECTURE_DECISIONS.md
- [ ] Step 8: 커밋
