# Admin Templates Agent Knowledge Base

## Intent

Django 관리자에서 컨텍스트 관련 배치 액션 UI를 제공하는 템플릿을 관리한다.

## Constraints

- 모든 폼은 Django Admin 액션 프로토콜(`action`, `_selected_action`)을 준수한다.
- CSRF 토큰을 포함하고, 관리자 기본 템플릿(`admin/base_site.html`)을 확장한다.
- FAQ 전용 템플릿은 컨텍스트/아이템 정보를 명확히 표기해 실수 삭제를 방지한다.

## Context

- `templates/admin/add_qa_pair.html`: FAQ QnA 추가용 폼.
- `templates/admin/remove_qa_pair.html`: FAQ QnA 삭제용 폼, 선택한 컨텍스트의 항목만 드롭다운에 노출한다.
- `templates/admin/rag/context/change_form.html`: FAQ 컨텍스트 변경 화면에서 QnA를 바로 삭제할 수 있는 모듈과 버튼을 제공한다.

## Changelog

- FAQ QnA 삭제 폼(`remove_qa_pair.html`)과 change form 확장 템플릿을 추가해 관리자에서 개별 QnA 삭제를 지원한다.
