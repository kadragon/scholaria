# Core Tests - FAQ Workflow Agent Knowledge Base

## Intent

Enhanced FAQ workflow test scenarios maintaining TDD validation for model/admin flows.

## Constraints

- Django TestCase-based ensuring database isolation
- FAQ-related tests directly call Context model FAQ-specific methods
- Admin action tests use authenticated Client with explicit POST parameters for selected objects

## Context

- `core/tests/test_faq_workflow.py` covers FAQ context creation → Q&A addition → admin UI validation
- Includes new tests covering `Context.remove_qa_pair` method and `remove_qa_pair_action` admin action

## Changelog

- Added FAQ Q&A deletion flow tests (`remove_qa_pair` method, admin action, change form delete button) to simultaneously validate model and admin UI
