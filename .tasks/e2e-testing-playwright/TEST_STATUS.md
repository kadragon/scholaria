# E2E Test Status Report

**Last Updated**: 2025-10-11
**Test Run**: Local development environment
**Pass Rate**: 45% (15/33 tests)

---

## Quick Summary

| Category | Total | Passed | Failed | Skipped |
|----------|-------|--------|--------|---------|
| **Overall** | 33 | 15 | 16 | 2 |
| Setup | 1 | 1 | 0 | 0 |
| Auth | 6 | 3 | 3 | 0 |
| Topics | 6 | 2 | 4 | 0 |
| Contexts | 6 | 4 | 1 | 1 |
| Chat | 7 | 4 | 3 | 0 |
| Analytics | 6 | 1 | 4 | 1 |

---

## Root Causes Analysis

### 1. Table Row Selection (High Priority)
**Impact**: 4 tests
**Cause**: `locator("tr", { hasText: "text" })` matches multiple rows
**Solution**: Use more specific selectors with column index

### 2. Async Task Processing (High Priority)
**Impact**: 4 tests
**Cause**: Celery worker not processing embeddings fast enough
**Solution**: Verify Celery worker running, increase timeouts

### 3. Auth Navigation Timeout (Medium Priority)
**Impact**: 3 tests
**Cause**: `/admin/topics` redirect times out after login
**Solution**: Wait for specific elements instead of URL

### 4. Missing Test Data (Medium Priority)
**Impact**: 4 tests
**Cause**: Analytics requires chat history that doesn't exist
**Solution**: Extend auth.setup.ts to create sample chats

---

## Next Sprint Goals

- [ ] Achieve 70% pass rate (23/33 tests)
- [ ] Fix all table row selector issues
- [ ] Verify Celery worker integration
- [ ] Create comprehensive test data in setup
