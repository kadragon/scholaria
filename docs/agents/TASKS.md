# Tasks: Scholaria RAG System

## 상태 스냅샷
- MVP 완성, FastAPI + Refine 스택 프로덕션 준비 완료
- 134개 테스트 통과, ruff/mypy 클린, Celery/Redis 비동기 인프라 운영 중
- 세부 이력은 `docs/agents/tasks/_archive/` 및 `TASKS_ARCHIVE_INDEX.md` 참고

## 진행 중
없음

## 단기 백로그
- [ ] **다크 모드** — UI 테마 토글 및 사용자 선호 저장
- [ ] **다국어 지원** — 핵심 UI 번역 및 Q&A 프롬프트 대응
- [ ] **SSO 통합** — 우선순위 공급자 결정 후 인증 흐름 통합

## 선택적 향상안
- [ ] **성능 관측 강화** — OpenTelemetry + 대시보드로 RAG 체인의 메트릭 가시화
- [ ] **피드백 루프 확장** — 좋아요/싫어요 외에 자유 서술 피드백 수집 UX 추가

## Frontend 테스트 계획
- [ ] **Phase 0 – 테스트 인프라 도입** — Vitest + React Testing Library + MSW 설치, `package.json`에 `test`, `test:watch`, `coverage` 스크립트 추가, `setupTests.ts`에서 Refine/React Router 모킹 및 JSDOM 환경 설정, GitHub Actions 워크플로에 프런트엔드 테스트 잡 추가
- [ ] **Phase 1 – 유틸/훅 단위 테스트** — `src/lib/apiClient.ts` 인터셉터와 401 리다이렉션, `src/providers/authProvider.ts`의 로그인/로그아웃/토큰 만료 흐름, `src/pages/chat/hooks/useChat.ts`의 SSE 스트림, 에러 핸들링, 메시지 버퍼 초기화 로직을 MSW 기반으로 검증
- [ ] **Phase 2 – 공용 컴포넌트 상호작용 테스트** — `src/components/InlineEditCell.tsx`, `src/components/CommandPalette.tsx`, `src/components/TableSkeleton.tsx`, `src/components/ui/*` 토글류 컴포넌트의 키보드·접근성 동작과 토스트(`src/hooks/use-toast.ts`) 호출 여부를 사용자 동작 중심으로 확인
- [ ] **Phase 3 – 페이지 시나리오 테스트** — `src/pages/login.tsx`, `src/pages/setup.tsx`, `src/pages/topics/*.tsx`, `src/pages/contexts/*.tsx`, `src/pages/chat/index.tsx`에 대해 Refine 훅과 라우팅을 모킹하여 필터링/일괄 편집/컨텍스트 업로드/채팅 스트리밍 등 핵심 플로우를 검증하고 주요 회귀 버그 사례를 재현하는 테스트 추가
- [ ] **Phase 4 – 커버리지/회귀 가드** — 70% 라인·브랜치 커버리지 기준 설정, 주요 회귀 케이스를 스냅샷 대신 명시적 어서션으로 전환, 실데이터 스키마 변경 감지를 위한 MSW 핸들러 공유, PR 템플릿에 프런트엔드 테스트 체크 추가

## 최근 완료 하이라이트
- **Golden Dataset 통합 테스트 완료** — Qdrant 벡터 검색 100% 정확도 달성, BGE 리랭킹 유지 확인 (2025-10-09)
- **Admin datetime 직렬화** — `AdminTopicOut`, `AdminContextOut`에 ISO 8601 timezone-aware 직렬화 추가 (2025-10-08)
- **운영 데이터 백업/복원 가이드** — 5가지 재해 복구 시나리오, 리허설 자동화 스크립트, 트러블슈팅 포함 (2025-10-08)
- **Frontend README 정리** — 실제 구현 상태 반영 (13개 기능 완료, 2개 TODO 유지) (2025-10-08)
- **성능 벤치마크 (초기)** — Mock 기반 응답 지연 & 동시성 테스트 3개, Golden Dataset 인프라 구축 (2025-10-08)
- FastAPI 전환, 인제스션 워크플로우, Refine 기반 Admin UI, 스트리밍 Q&A 인터페이스 제공 완료
- Celery + Redis 재도입으로 임베딩 재생성 및 캐시 공유 인프라 복원

## 운영 참고
- 품질 점검: `uv run ruff check . && uv run mypy . && uv run pytest`
- 개발 서버: `uv run uvicorn backend.main:app --reload`
- Docker(dev): `docker compose -f docker-compose.yml -f docker-compose.dev.yml up --build`
- 마이그레이션: `uv run alembic upgrade head`
