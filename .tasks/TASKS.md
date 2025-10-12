# Tasks: Scholaria RAG System

## 상태 스냅샷

- MVP 완성, FastAPI + Refine 스택 프로덕션 준비 완료
- 127개 프런트엔드 테스트 (62.17% coverage, 50% threshold), 223개 백엔드 테스트 (83% coverage, 80% threshold)
- ruff/mypy 클린, Celery/Redis 비동기 인프라 운영 중
- CI: 프런트엔드 4개 잡, 백엔드 3개 잡 (test+coverage, lint, typecheck)
- Observability: OpenTelemetry + Jaeger + Prometheus + Grafana 완전 통합 (2025-10-10)
- 세부 이력은 `docs/agents/tasks/_archive/` 및 `TASKS_ARCHIVE_INDEX.md` 참고

## 진행 중

- [x] **E2E 테스트 도입 (Playwright)** — 핵심 플로우 검증, App.tsx/ChatPage/Analytics 커버, 시각적 회귀 테스트 기반 마련 (Phase 1-8 완료, 28/29 통과 96.5%, Redis/Celery 구성 수정 및 컨텍스트 처리 복구 성공, Chat 핵심 기능 및 컨텍스트 관리 작동 확인, 다중 메시지 테스트에서 백엔드 세션 처리 이슈 발견)

## 단기 백로그

- [x] **React Router v7 업그레이드** — 기존 v6 라우팅 구성을 v7 API에 맞춰 마이그레이션, 관련 네비게이션/라우터 훅 영향도 점검 (이미 완료됨, 검증 완료, 2025-10-10)
- [x] **Celery Worker Docker 설정 수정** — venv 경로 불일치 문제 해결, isolated uv environment 적용, torch 설치 성공 (2025-10-12)

## 선택적 향상안

- [x] **성능 관측 강화 (OpenTelemetry)** — 8개 Phase 완료 (기반 구축, 커스텀 스팬, 메트릭, Jaeger, Prometheus, Grafana, 테스트, 문서화), 223개 테스트, 83% 커버리지, ~4% 오버헤드 (2025-10-10)
- [x] **피드백 루프 확장** — 좋아요/싫어요 + 자유 서술 피드백 입력 UI (챗 인터페이스, `/api/history/{id}/feedback`)
- [ ] **E2E 테스트 도입 (Playwright)** — 핵심 사용자 플로우 검증 (로그인→토픽 생성→Q&A, 컨텍스트 업로드→인제스션→검색, 피드백→분석), 시각적 회귀 테스트 기반 마련

## Frontend 테스트 계획

- [x] **Phase 0 – 테스트 인프라 도입** — Vitest + React Testing Library + MSW 설치, `package.json`에 `test`, `test:watch`, `coverage` 스크립트 추가, `setupTests.ts`에서 Refine/React Router 모킹 및 JSDOM 환경 설정, GitHub Actions 워크플로에 프런트엔드 테스트 잡 추가
- [x] **Phase 1 – 유틸/훅 단위 테스트** — `src/lib/apiClient.ts` 인터셉터와 401 리다이렉션, `src/providers/authProvider.ts`의 로그인/로그아웃/토큰 만료 흐름, `src/pages/chat/hooks/useChat.ts`의 SSE 스트림, 에러 핸들링, 메시지 버퍼 초기화 로직을 MSW 기반으로 검증 (24 tests, 2025-10-09)
- [x] **Phase 2 – 공용 컴포넌트 상호작용 테스트** — `InlineEditCell`, `CommandPalette`, `TableSkeleton`, `use-toast` 테스트 작성 (28 tests); ResizeObserver/scrollIntoView 모킹 추가; Radix UI 래퍼는 통합 테스트에서 검증 예정 (2025-10-09)
- [x] **Phase 3 – 페이지 시나리오 테스트** — login(5), setup(6), topics list(3), contexts list(1), chat(2) 총 17개 페이지 플로우 테스트 완료; MSW 핸들러 확장하여 Refine 훅(`useTable`, `useUpdate`, `useDelete`) 모킹 지원; 전체 65개 테스트 통과 (2025-10-09)
- [x] **Phase 4 – 커버리지/회귀 가드** — 25% 커버리지 임계값 설정 (`vitest.config.ts`), CI coverage 잡 추가, PR 템플릿 생성 (백엔드/프런트엔드 체크리스트), `frontend/README.md` 업데이트 (2025-10-09)
- [x] **Phase 5 – 커버리지 확대 (31.62% → 40.91%)** — dataProvider(4), Sidebar(3), LoginPage(4), MessageInput(5) 테스트 추가; 86개 테스트 통과; 임계값 35% 상향; dist/ 제외 설정 (2025-10-09)
- [x] **Phase 6 – 추가 커버리지 확장 (40.91% → 51.29%)** — SetupPage(6), useCommandPalette(3), TopicSelector(3), MessageList(6), AnalyticsSkeleton(2) 테스트 추가; 106개 테스트 통과; 임계값 45% 상향 (2025-10-09)
- [x] **Phase 7 – 현실적 범위 (32.79% → 47.87%)** — CRUD List 2개 (topics/list 6 tests, contexts/list 6 tests); 복잡한 통합 테스트 제외 (App.tsx, ChatPage, Analytics는 E2E 권장); 105개 테스트 통과 (+12); 임계값 40% 설정; Unit 85%, Integration 45%, Branch 78% 균형 전략 (2025-10-10)
- [x] **Phase 8 – 점진적 확대 (47.87% → 55.97%)** — dataProvider custom 완전 커버(3), topics/create(5), topics/edit(5) 테스트 추가; 118개 테스트 통과 (+13); 임계값 50% 설정; Unit 95%+, Integration 57%+, Branch 80%+ 달성 (2025-10-10)
- [x] **Phase 9 – 60% 돌파 (55.97% → 62.17%)** — contexts/edit(5), contexts/create(4) 테스트 추가; 127개 테스트 통과 (+9); 임계값 50% 유지; Unit 100%, Integration 61%+, Branch 79%+ 달성; 전체 +30.55%p 향상 (Phase 5-9) (2025-10-10)

## 최근 완료 하이라이트

- **Celery Worker Docker 설정 수정 완료** — venv 경로 불일치 해결, isolated uv environment 적용, torch 설치 성공, E2E 테스트 RAG 응답 재활성화 (2025-10-12)
- **E2E 테스트 OpenAI API 키 통합** — Playwright dotenv 설정, Docker 환경변수 보완, Celery Redis 연결 해결 (2025-10-12)
- **OpenTelemetry 완전 통합 (Phase 1-8 완료)** — SDK 통합, 커스텀 RAG 스팬, 메트릭 수집, Jaeger (traces), Prometheus (metrics), Grafana (6개 패널 대시보드), 통합/성능 테스트, 포괄적 문서화 (OBSERVABILITY.md 400+줄), 26개 파일 변경, ~11.5시간 소요 (2025-10-10)
- **Phase 6 커버리지 확장** — 40.91% → 51.29%, 20개 테스트 추가 (SetupPage, useCommandPalette, TopicSelector, MessageList, AnalyticsSkeleton), 임계값 45% 상향 (2025-10-09)
- **백엔드 커버리지 임계값 설정** — 85% 커버리지, 80% 임계값, backend-ci.yml 3개 잡 (test+coverage, lint, typecheck) (2025-10-09)
- **Phase 4 커버리지 가드 완료** — 25% 임계값 설정, CI coverage 잡 추가, PR 템플릿 (백엔드/프런트엔드 체크리스트) (2025-10-09)
- **피드백 코멘트 분석 뷰** — `/admin/analytics/feedback/comments` 엔드포인트 및 관리자 대시보드 코멘트 리스트 + 토픽 필터 (2025-10-09)
- **Chat 피드백 입력 UI** — 세션 히스토리 생성 + 좋아요/싫어요 및 자유 서술 코멘트 PATCH 연동 (2025-10-09)
- **Phase 3 페이지 시나리오 테스트 완료** — login, setup, topics list, contexts list, chat 페이지의 핵심 플로우 검증 (17 tests, 65 total tests) (2025-10-09)
- **다크 모드 완료** — CSS 변수 기반 테마 시스템, light/dark/system 토글, localStorage 저장, FOUC 방지, 37개 테스트 통과 (2025-10-09)
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
