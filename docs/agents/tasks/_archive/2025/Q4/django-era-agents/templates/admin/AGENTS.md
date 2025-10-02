# Admin Templates Agent Knowledge Base

## Intent

Manage templates providing context-related batch action UI in Django admin.

## Constraints

- All forms comply with Django Admin action protocol (`action`, `_selected_action`)
- Include CSRF tokens and extend admin base template (`admin/base_site.html`)
- FAQ-specific templates clearly display context/item information to prevent accidental deletion

## Context

- `templates/admin/add_qa_pair.html`: Form for adding FAQ Q&A pairs
- `templates/admin/remove_qa_pair.html`: Form for deleting FAQ Q&A pairs, exposing only items from selected context in dropdown
- `templates/admin/rag/context/change_form.html`: Provides module and button for direct Q&A deletion from FAQ context change screen

## Changelog

- Added FAQ Q&A deletion form (`remove_qa_pair.html`) and change form extension template to support individual Q&A deletion in admin
