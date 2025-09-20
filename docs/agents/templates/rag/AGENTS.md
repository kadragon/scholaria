# Templates/RAG Agent Knowledge Base

## Intent

Web UI for topic selection and Q&A interaction.

## Constraints

- **TDD Implementation**: Red → Green → Refactor methodology
- **Responsive Design**: Mobile and desktop support
- **Type Safety**: mypy strict compliance
- **API Integration**: JavaScript with existing REST endpoints

## Context

### URL Structure
- `/` - Topic selection, `/qa/<topic_id>/` - Q&A interface
- API: `/api/topics/`, `/api/ask/`

### Components
- Base template with responsive CSS
- Topic selection grid with cards
- Q&A interface with real-time API integration
- CSRF handling, error messages, loading states

## Changelog

### Web Interface Implementation
- TDD with 5 tests: topic selection and Q&A interface
- Responsive design with CSS Grid/Flexbox
- URL namespace separation (web vs API)
- JavaScript integration with CSRF protection
- Progressive enhancement and error handling
