# Core Tests - FAQ Workflow Agent Knowledge Base

## Intent

보강된 FAQ 워크플로우 테스트 시나리오를 유지하며 모델/어드민 흐름을 TDD로 검증한다.

## Constraints

- Django TestCase 기반으로 DB 격리를 보장한다.
- FAQ 관련 테스트는 `Context` 모델의 FAQ 전용 메서드를 직접 호출한다.
- 관리자 액션 테스트 시 로그인된 `Client`를 사용하고, 선택된 객체에 대한 POST 파라미터를 명시한다.

## Context

- `core/tests/test_faq_workflow.py`는 FAQ 컨텍스트 생성 → QnA 추가 → 관리자 UI 검증을 다룬다.
- `Context.remove_qa_pair` 메서드 및 `remove_qa_pair_action` 관리자 액션을 커버하는 신규 테스트가 포함된다.

## Changelog

- FAQ QnA 삭제 플로우 테스트(`remove_qa_pair` 메서드, 관리자 액션, change form 삭제 버튼)를 추가해 모델과 관리자 UI를 동시에 검증한다.
