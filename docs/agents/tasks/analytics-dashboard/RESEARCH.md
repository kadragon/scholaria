# Analytics Dashboard - Research

## Goal
분석 대시보드 구현 - 사용량 통계, 인기 질문, 피드백 추세 등을 시각화

## Scope
- 백엔드: 통계 집계 API (analytics router)
- 프론트엔드: 관리자 대시보드 UI (Refine + recharts/visx)
- 테스트: API 엔드포인트 및 집계 로직 검증

## Related Files/Flows

### 백엔드 (FastAPI)
- `backend/models/history.py` - `QuestionHistory` (question, answer, feedback_score, created_at, topic_id, session_id)
- `backend/models/context.py` - `Context`, `ContextItem` (context_type, chunk_count, created_at)
- `backend/models/topic.py` - `Topic` (name, question_histories relationship)
- `backend/routers/` - 라우터 디렉터리 (auth, contexts, history, rag, topics 참고)
- `backend/schemas/` - Pydantic 스키마 패턴

### 프론트엔드 (Refine)
- `frontend/src/pages/` - topics, contexts (list/create/edit/show 패턴)
- `frontend/src/providers/dataProvider.ts` - REST API 연결
- `frontend/src/providers/authProvider.ts` - JWT 인증

### 테스트
- `backend/tests/test_*.py` - 유닛 테스트 패턴 (SQLAlchemy fixtures, `conftest.py` 공용 fixture)

## Hypotheses

1. **API 설계**: `/admin/analytics` 엔드포인트로 집계 데이터 제공 (일/주/월 범위 지원)
2. **집계 대상**:
   - 질문 수 (시간대별, 토픽별)
   - 피드백 점수 분포 (긍정/부정 비율)
   - 인기 질문 (조회/즐겨찾기 기준)
   - 컨텍스트 사용 통계 (타입별, 청크 수)
   - 세션 활동 (순 사용자 수 추정)
3. **프론트엔드**: Recharts 또는 visx 차트 라이브러리 사용
4. **권한**: Admin 전용 엔드포인트 (JWT 토큰 검증)

## Evidence

- `QuestionHistory` 모델에 `feedback_score`, `created_at`, `topic_id`, `session_id` 필드 존재
- `Context` 모델에 `context_type`, `chunk_count` 필드 존재
- 기존 admin 라우터 패턴: `backend/routers/admin/` (bulk_operations, contexts, topics, users 참고)
- 프론트엔드 페이지 패턴: `frontend/src/pages/{resource}/list.tsx` 형식
- 피드백 시스템 완료 (`feedback_score` 필드 사용 중)

## Assumptions/Open Questions

1. **차트 라이브러리**: Recharts 사용 (shadcn/ui 호환성 고려)
2. **시간 범위**: 기본 7일, 필터 옵션으로 1일/30일/90일 제공
3. **캐싱**: 집계 쿼리는 Redis 캐시 적용 (선택적)
4. **실시간 vs 배치**: 초기 버전은 요청 시 집계, 추후 Celery 스케줄링으로 전환 가능
5. **프론트엔드 라우팅**: `/analytics` 경로로 새 페이지 추가

## Sub-agent Findings

(N/A - 직접 탐색)

## Risks

- **성능**: QuestionHistory 테이블이 커질 경우 집계 쿼리 성능 저하 (인덱스/캐싱으로 완화)
- **시간대**: UTC 저장 기준, 프론트엔드에서 로컬 시간 변환 필요
- **빈 데이터**: 초기 사용 시 차트에 데이터 없음 (placeholder UI 필요)

## Next

PLAN.md 작성 - API 스키마, 집계 로직, 프론트엔드 컴포넌트, 테스트 계획
