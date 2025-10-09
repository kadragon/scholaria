# Docs Folder - Agent Knowledge Base

## Intent
Scholaria 운영·개발 문서(가이드, 플레이북, 헬프)를 단일 소스로 유지한다.

## Constraints
- 테스트와 문서가 동기화되어야 한다. 핵심 가이드의 헤딩 이름은 테스트에서 상수로 사용되므로 변경 시 관련 테스트를 갱신한다.
- 문서는 실사용 시나리오 중심으로 작성하고 실행 가능한 명령을 포함한다.
- 신규 문서는 Markdown으로 작성하며 최상위 헤딩은 파일 목적과 일치해야 한다.

## Context
- 주요 문서:
  - `docs/CONTRIBUTING.md`: 브랜치 전략, TDD, 품질 게이트.
  - `docs/DEPLOYMENT.md`: 프로덕션 배포 절차(`docker-compose.prod.yml`, nginx, 환경 변수).
  - `docs/ADMIN_GUIDE.md`, `docs/USER_GUIDE.md`: 관리자/엔드유저 워크플로우.
  - `docs/TESTING_STRATEGY.md`: TDD 원칙, pytest/coverage 실행 플로우.
  - `docs/ARCHITECTURE_DECISIONS.md`: FastAPI 전환 등 핵심 결정.
  - `docs/BACKUP_STRATEGY.md`: 백업/복구 체크리스트.
- 최신 프로젝트 상태 요약은 `README.md`의 "Project Status" 섹션을 소스로 삼는다.
- 문서에서 `Docling`을 in-process 의존성으로 명시하고 외부 Unstructured API 언급을 제거한다.

## Changelog

### 2025-10-09
- `docs/tasks.md` 참조 제거(파일 삭제됨). 진행 상황은 `README.md`에서 추적.
- 배포 가이드에 Docling 의존성 및 `docker compose` 명령 사용이 반영되었는지 확인 완료.
