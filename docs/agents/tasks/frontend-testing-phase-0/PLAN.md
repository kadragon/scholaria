# Plan: Frontend Testing Phase 0 Completion

## Objective
GitHub Actions 워크플로 추가하여 Phase 0 요구사항 완료

## Constraints
- **TDD 불필요**: GitHub Actions YAML은 선언적 설정 파일 (Structural 변경)
- **기존 스크립트 활용**: `npm run test`, `npm run typecheck`, `npm run lint`
- **최소 필수 잡**: test, typecheck, lint
- **Backend 통합 고려**: 기존 백엔드 CI가 없으므로 frontend 전용 워크플로 생성

## Target Files & Changes

### New Files
1. **`.github/workflows/frontend-ci.yml`**
   - Trigger: `push` (main), `pull_request`
   - Jobs:
     - `test`: Node.js 설치 → npm install → npm run test
     - `typecheck`: npm run typecheck
     - `lint`: npm run lint
   - Working directory: `frontend/`
   - Node version: 20.x (LTS)

### Modified Files
1. **`docs/agents/TASKS.md`**
   - Phase 0 항목 체크박스 업데이트 `- [x]`
   - "최근 완료 하이라이트"에 추가

## Test & Validation Cases

### Validation
1. ✅ 로컬에서 `npm run test` 실행 → 37 tests passing
2. ✅ 로컬에서 `npm run typecheck` 실행 → no errors
3. ✅ 로컬에서 `npm run lint` 실행 → no warnings
4. 🔄 GitHub Actions 워크플로 파일 생성 후 push
5. 🔄 GitHub에서 워크플로 실행 확인 (Actions 탭)

### Manual Check
- GitHub Actions UI에서 모든 잡 Green 확인
- PR 체크리스트에 frontend CI 상태 표시 확인

## Steps

### Phase 1: GitHub Actions 워크플로 생성
- [ ] Step 1: `.github/workflows/frontend-ci.yml` 작성
- [ ] Step 2: 로컬에서 YAML 문법 검증 (yamllint 또는 온라인 도구)
- [ ] Step 3: TASKS.md 업데이트 (Phase 0 완료 표시)

### Phase 2: 커밋 & 검증
- [ ] Step 4: 브랜치 생성 (`feat/frontend-testing-phase-0`)
- [ ] Step 5: 커밋 ([Structural] GitHub Actions frontend CI 추가)
- [ ] Step 6: main에 직접 푸시 (또는 PR 생성하여 검증)
- [ ] Step 7: GitHub Actions 실행 결과 확인

## Rollback Plan
- 워크플로 파일 삭제 또는 비활성화
- TASKS.md 체크박스 되돌리기

## Review Hotspots
1. **Working Directory**: `frontend/` 명시 필수
2. **Node Version**: package.json engines 필드와 일치 여부
3. **Cache Strategy**: npm cache 활용으로 빌드 속도 개선 가능
4. **Fail-Fast**: 한 잡 실패 시 다른 잡도 중단할지 여부

## Status
- [x] Step 1: GitHub Actions 워크플로 작성
- [ ] Step 2: YAML 문법 검증
- [ ] Step 3: TASKS.md 업데이트
- [ ] Step 4: 브랜치 생성
- [ ] Step 5: 커밋
- [ ] Step 6: Push 및 워크플로 실행
- [ ] Step 7: 검증 완료
