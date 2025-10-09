# RAG Admin Interface - Agent Knowledge Base

## Intent

Dynamic context type selection workflow with contextual help and workflow guidance for RAG admin interface.

## Constraints

- **TDD Required**: Red → Green → Refactor cycle
- **Type Safety**: mypy compliance
- **Dynamic Forms**: JavaScript-powered type-specific form switching
- **User Experience**: Clear workflow guidance for each context type

## Context

### Context Type Selection Workflow
1. **Dynamic Form Switching**: JavaScript automatically shows/hides relevant fields based on context_type selection
2. **Type-Specific Forms**: Each context type (PDF, Markdown, FAQ) has its own optimized form layout
3. **Contextual Help**: Real-time guidance and help text updates based on user selections

### Admin Interface Components
- **ContextForm**: Custom form with dynamic field validation and context-aware help text
- **Dynamic Fieldsets**: Server-side fieldset generation based on context type
- **JavaScript Integration**: Client-side form enhancement with `context_type_selection.js`
- **Custom Template**: Enhanced admin change form template with workflow guidance

## Changelog

### Context Type Selection Implementation
- Dynamic form switching based on context_type selection (15 tests passing)
- Type-specific creation forms with appropriate field visibility
- Contextual help and workflow guidance with visual status indicators
- JavaScript-powered real-time form updates and help text

### Technical Features
- ContextForm with dynamic field requirements (chunk_count made optional)
- JavaScript module for form enhancement with workflow step display
- CSS styling for status indicators (pending, processing, completed, failed)
- Custom admin template with context type guide and workflow steps

### User Experience Enhancements
- Context type guide explaining PDF, Markdown, and FAQ workflows
- Step-by-step workflow instructions that change based on selected type
- Processing status indicators with color-coded visual feedback
- Real-time field help text updates based on context and status

### Form Behavior
- PDF type: Shows file upload field with automatic parsing workflow
- Markdown type: Shows content editor with direct editing capabilities
- FAQ type: Shows Q&A management tools and workflow guidance
- Processing status: Dynamic help text and visual indicators
