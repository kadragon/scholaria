# Templates/RAG Agent Knowledge Base

## Intent

Web-based user interface for topic selection and Q&A interaction in the Scholaria RAG system.

## Constraints

- **TDD Implementation**: All UI components developed using Red → Green → Refactor methodology
- **Responsive Design**: Must work on mobile and desktop devices
- **Django Templates**: Use Django's template system with proper URL namespacing
- **Type Safety**: All views must pass mypy strict type checking
- **API Integration**: Frontend JavaScript integrates with existing REST API endpoints

## Context

### URL Structure

```
# Web Interface (rag_web namespace)
/                          -> Topic selection page
/qa/                       -> Redirects to topic selection
/qa/<topic_id>/           -> Q&A interface for specific topic

# API Endpoints (rag namespace)
/api/topics/              -> Topic list API
/api/ask/                 -> Question answering API
```

### Template Organization

- `templates/base.html` - Base template with responsive CSS and common styling
- `templates/rag/topic_selection.html` - Topic selection grid with cards
- `templates/rag/qa_interface.html` - Q&A interface with real-time API integration

### Views Architecture

- `TopicSelectionView` - Displays available topics in responsive cards
- `QAInterfaceView` - Handles topic-specific Q&A with JavaScript integration
- `QAInterfaceRedirectView` - Redirects to topic selection when no topic specified

### JavaScript Integration

- Fetch API for asynchronous communication
- CSRF token handling for Django compatibility
- Error handling with user-friendly messages
- Loading states and form validation

## Changelog

### 2025-09-19: Topic Selection Interface Implementation

- ✅ **TDD Methodology**: Wrote 5 failing tests first, then implemented to make them pass
- ✅ **Responsive Templates**: Created mobile-first responsive design with CSS Grid and Flexbox
- ✅ **URL Separation**: Separated web URLs from API URLs to avoid namespace conflicts
- ✅ **Type Safety**: All views fully typed with mypy compliance
- ✅ **JavaScript Integration**: Real-time Q&A with proper error handling and CSRF protection
- ✅ **Test Coverage**: Comprehensive test suite covering all user interactions and edge cases

### Technical Decisions

- **Separate URL Files**: Created `rag/web_urls.py` to avoid namespace collision with API URLs
- **Template Inheritance**: Used Django template inheritance for maintainable styling
- **Inline CSS**: Kept styles in templates for self-contained components (suitable for MVP)
- **Progressive Enhancement**: Interface works without JavaScript for basic functionality
- **Error Boundary**: Graceful degradation when external services unavailable

### Testing Strategy

- **Template Rendering**: Tests verify correct content appears in responses
- **URL Resolution**: Tests ensure proper URL namespace separation
- **Error Cases**: Tests cover 404 errors and empty states
- **Navigation Flow**: Tests verify redirect behavior and user journey

All 5 web interface tests passing with proper integration to existing RAG pipeline.
