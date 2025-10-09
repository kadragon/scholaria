# Research: Documentation Update & Project Cleanup

## Goal
FastAPI 전환 완료 후 문서 업데이트 및 Django 레거시 파일/폴더 정리

## Scope
1. **문서 업데이트**: README, DEPLOYMENT, ARCHITECTURE를 FastAPI 기준으로 수정
2. **파일/폴더 정리**: Django 관련 불필요 파일 제거

## Related Files/Folders

### 문서 (업데이트 필요)
- `README.md`: 프로젝트 개요, 기술 스택, 시작 가이드
- `docs/DEPLOYMENT.md`: 배포 가이드
- `docs/ARCHITECTURE_DECISIONS.md`: 아키텍처 결정 기록

### 정리 대상 후보 (루트 레벨)
1. **test_write.db** (60KB): 테스트 DB, .gitignore 추가 필요
2. **media/** (빈 폴더): Django MEDIA_ROOT, 제거 가능
3. **storage/** (빈 폴더): MinIO 제거 후 미사용, 제거 가능
4. **uploads/** (13개 파일): Django FileField 업로드, 확인 후 제거
5. **tmp/** (임시 파일): 확인 후 정리
6. **.coverage**: 테스트 커버리지 캐시, .gitignore 추가
7. **__pycache__/**: Python 바이트코드 캐시

### 보존 대상
- **alembic/**: SQLAlchemy 마이그레이션 (필요)
- **backend/**: FastAPI 코드
- **frontend/**: Refine Admin Panel
- **nginx/**: 프로덕션 리버스 프록시
- **scripts/**: 배포 & 백업 스크립트
- **docs/**: 문서
- **.venv/**, **.git/**, 기타 도구 설정

## Hypotheses
1. **media/, storage/, uploads/**: Django 제거로 더 이상 불필요
2. **test_write.db, .coverage**: 로컬 개발 아티팩트, .gitignore 추가
3. **README.md**: Django 언급 제거, FastAPI 강조 필요
4. **DEPLOYMENT.md**: Django 배포 가이드 → FastAPI 배포 가이드

## Evidence
- `media/`, `storage/` 빈 폴더 (ls 결과)
- `uploads/` 13개 파일 존재 → 내용 확인 필요
- `test_write.db` 60KB → pytest 생성 파일
- README.md L1-50 Django 언급 가능성

## Assumptions
- 현재 프로젝트는 FastAPI 전용
- Django 관련 설정/파일은 모두 제거 가능
- 문서는 개발자 온보딩 & 배포에 중요

## Risks
- **uploads/ 삭제**: 중요 파일 포함 가능성 → 확인 필수
- **문서 과도 수정**: 기존 맥락 손실 → 중요 정보는 보존

## Next
Plan 단계 → 파일 확인 & 문서 수정 전략 수립
