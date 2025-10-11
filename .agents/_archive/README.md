# Archive Policy

## Purpose
Store deprecated or retired agent knowledge documents.

## Structure
```
_archive/
  YYYY/
    Q1/
    Q2/
    Q3/
    Q4/
```

## Rules
1. Move files here when `status: deprecated` is set.
2. Update `supersedes` chain in replacement document.
3. Keep archived files read-only; do not edit.
4. Reference archived docs via full path when needed for historical context.

## Maintenance
- Review quarterly; purge items older than 2 years unless explicitly required for compliance or debugging.
