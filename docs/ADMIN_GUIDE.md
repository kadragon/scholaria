# Admin User Guide

This guide provides comprehensive instructions for administrators to manage the **Scholaria RAG System** through the Django admin interface. Learn how to create topics, manage content, upload documents, and perform bulk operations efficiently.

## Getting Started

Prepare your admin account and familiarize yourself with the interface before making changes.

## Login

1. **Access the Admin Interface**:
   - Navigate to `https://your-domain.com/admin/` (or `http://localhost:8000/admin/` for development)
   - You will see the Django admin login page

2. **Enter Credentials**:
   - **Username**: Your administrator username
   - **Password**: Your secure administrator password
   - Click **Log in**

3. **Admin Dashboard**:
   - After successful login, you'll see the main admin dashboard
   - The interface shows three main sections: **Topics**, **Contexts**, and **Context Items**

## Admin Interface Overview

The Scholaria admin interface is organized into three main areas:

- **RAG** section containing:
  - **Topics**: Academic subjects and their system prompts
  - **Contexts**: Document containers (PDF, Markdown, FAQ)
  - **Context Items**: Individual content pieces with file attachments

## Navigation

- **Home**: Click "Scholaria Administration" to return to the main dashboard
- **View Site**: Click to see the public Q&A interface
- **Logout**: Click your username in the top-right corner

## Topic Management

Topics represent academic subjects or categories that users can ask questions about. Each topic has a system prompt that guides the AI's responses.

### Creating a New Topic

1. **Navigate to Topics**:
   - From the admin dashboard, click **Topics** under the RAG section
   - Click the **Add Topic** button

2. **Fill Topic Information**:
   - **Name**: Enter a descriptive topic name (e.g., "Machine Learning", "Biology 101")
   - **Description**: Provide a detailed description of the topic's scope
   - **System Prompt**: Write instructions for the AI about how to respond for this topic

3. **Example System Prompt**:
   ```
   You are a helpful AI assistant specializing in Machine Learning.
   Provide accurate, educational responses suitable for undergraduate students.
   Include relevant examples and cite sources when possible.
   ```

4. **Associate Contexts** (Optional):
   - In the **Relationships** section, select relevant contexts
   - Hold Ctrl/Cmd to select multiple contexts
   - Click **Save** to create the topic

### Editing Topics

1. **Find the Topic**:
   - Go to the Topics list page
   - Use the **search bar** to find topics by name or description
   - Click on the topic name to edit topic details

2. **Update Information**:
   - Modify the name, description, or system prompt as needed
   - Add or remove context associations
   - Click **Save** to update

### Topic List Features

- **Search**: Use the search box to find topics by name or description
- **Filtering**: Filter by creation date using the sidebar filters
- **Sorting**: Click column headers to sort by name, creation date, etc.

## Context Management

Contexts are containers that organize related documents. Each context has a specific type (PDF, Markdown, or FAQ) that determines how content is processed.

### Creating a New Context

1. **Navigate to Contexts**:
   - From the admin dashboard, click **Contexts**
   - Click the **Add Context** button

2. **Fill Context Information**:
   - **Name**: Enter a descriptive context name (e.g., "Linear Algebra Textbook")
   - **Description**: Describe what documents this context will contain
   - **Context Type**: Choose from:
     - **PDF**: For PDF documents and academic papers
     - **MARKDOWN**: For Markdown files and formatted text
     - **FAQ**: For question-answer pairs

3. **Best Practices**:
   - Use descriptive names that indicate the content type and subject
   - Group related documents in the same context
   - Choose the appropriate context type for optimal processing

### Context Types Explained

- **PDF Context**:
  - Designed for academic papers, textbooks, and reports
  - Automatically extracts text and maintains document structure
  - Best for formal educational content

- **MARKDOWN Context**:
  - Perfect for formatted text, notes, and documentation
  - Preserves markdown formatting and structure
  - Ideal for structured educational materials

- **FAQ Context**:
  - Optimized for question-answer format
  - Great for common questions and explanations
  - Helps provide direct answers to student queries

### Editing Contexts

1. **Find the Context**:
   - Use search or filtering to locate the context
   - Click the context name to edit

2. **Modify Details**:
   - Update name, description, or type as needed
   - **Note**: Changing context type may affect how existing content is processed

## Context Item Management

Context Items are individual pieces of content within contexts. They can contain text content and/or uploaded files.

### Creating Context Items

### Method 1: Manual Content Entry

1. **Navigate to Context Items**:
   - Click **Context Items** from the admin dashboard
   - Click **Add Context Item**

2. **Fill Basic Information**:
   - **Title**: Descriptive title for the content
   - **Context**: Select the appropriate context from the dropdown
   - **Content**: Enter or paste the text content directly

3. **Add Metadata** (Optional):
   - Expand the **Metadata** section
   - Add JSON metadata for additional information:
   ```json
   {
     "source": "Textbook Chapter 5",
     "author": "Dr. Smith",
     "difficulty": "intermediate"
   }
   ```

### Context Item Features

- **Title**: Searchable title for easy identification
- **Content**: Full text content (auto-populated from uploads)
- **File Path**: MinIO storage path (automatically set)
- **Metadata**: Flexible JSON field for additional information
- **Timestamps**: Creation and modification dates

## File Upload

Use file uploads (Method 2) to ingest large documents or reference material while maintaining security controls.

1. **Choose File Upload**:
   - In the **File Upload** section, click **Choose File**
   - Select a PDF, Markdown (.md), or text file

2. **Automatic Processing**:
   - The system will automatically:
     - Validate the file for security
     - Extract content from the file
     - Store the file in MinIO object storage
     - Populate the content field

3. **File Requirements**:
   - **Maximum size**: 10MB per file
   - **Supported formats**: PDF, Markdown (.md, .markdown), Plain text (.txt)
   - **Security**: Files are automatically scanned for malicious content

### File Upload Security

The system implements comprehensive file validation:

- **File Type Validation**: Secure validation of file types, including magic byte verification for binary formats like PDF
- **Size Limits**: Maximum 10MB per file
- **Malicious Content Detection**: Automatic scanning for threats
- **Filename Sanitization**: Removes unsafe characters and paths

## Bulk Operations

The admin interface provides powerful bulk operations to manage multiple items efficiently.

### Topic Bulk Operations

#### Assign Context to Topics

1. **Select Topics**:
   - Go to the Topics list
   - Check the boxes next to topics you want to update
   - Select **Assign context to selected topics** from the Actions dropdown
   - Click **Go**

2. **Choose Context**:
   - Select the context to assign from the dropdown
   - Click **Assign Context**
   - All selected topics will be associated with the chosen context

#### Bulk Update System Prompt

1. **Select Topics**:
   - Choose multiple topics using checkboxes
   - Select **Update system prompt for selected topics**
   - Click **Go**

2. **Enter New Prompt**:
   - Type the new system prompt in the text area
   - Click **Update System Prompt**
   - All selected topics will receive the new prompt

### Context Bulk Operations

#### Update Context Type

1. **Select Contexts**:
   - Choose contexts to update using checkboxes
   - Select **Update context type for selected contexts**
   - Click **Go**

2. **Choose New Type**:
   - Select PDF, MARKDOWN, or FAQ from the dropdown
   - Click **Update Context Type**
   - **Warning**: This may affect content processing

### Context Item Bulk Operations

#### Regenerate Embeddings

1. **Select Items**:
   - Choose context items using checkboxes
   - Select **Regenerate embeddings for selected items**
   - Click **Go**

2. **Confirm Action**:
   - Review the selected items
   - Click **Regenerate Embeddings**
   - The system will process embeddings in the background

#### Move Items to Different Context

1. **Select Items**:
   - Choose items to move using checkboxes
   - Select **Move selected items to another context**
   - Click **Go**

2. **Choose Destination**:
   - Select the target context from the dropdown
   - Click **Move Items**
   - All selected items will be moved to the new context (move to context operation)

## Best Practices

### Content Organization

1. **Topic Structure**:
   - Create specific topics rather than broad categories
   - Use clear, descriptive names
   - Write detailed system prompts that guide AI responses

2. **Context Organization**:
   - Group related documents in the same context
   - Use consistent naming conventions
   - Choose the correct context type for your content

3. **Content Quality**:
   - Ensure uploaded documents are clear and well-formatted
   - Review auto-extracted content for accuracy
   - Add meaningful metadata to improve searchability

### System Prompt Guidelines

Write effective system prompts by:

1. **Being Specific**: Define the subject area and expertise level
2. **Setting Tone**: Specify if responses should be formal, casual, technical, etc.
3. **Providing Context**: Mention the target audience (students, professionals, etc.)
4. **Including Instructions**: Specify citation requirements, example preferences, etc.

Example:
```
You are an expert biology tutor helping undergraduate students.
Provide clear, accurate explanations with relevant examples.
When discussing complex processes, break them into simple steps.
Always cite sources when referencing specific research or data.
```

### File Management

1. **Organize Before Upload**:
   - Review documents for quality and relevance
   - Ensure files are properly formatted
   - Remove sensitive or irrelevant information

2. **Use Descriptive Titles**:
   - Create titles that clearly describe the content
   - Include subject area and content type
   - Make titles searchable

3. **Leverage Metadata**:
   - Add relevant tags and categories
   - Include difficulty levels
   - Specify target audience information

### Performance Optimization

1. **Efficient Bulk Operations**:
   - Use bulk actions for large-scale changes
   - Process similar items together
   - Monitor system performance during large operations

2. **Content Management**:
   - Regularly review and update outdated content
   - Remove duplicate or irrelevant items
   - Keep contexts organized and focused

## Workflow Examples

### Example 1: Setting up a New Course

1. **Create the Topic**:
   - Name: "Introduction to Psychology"
   - Description: "Foundational concepts in psychology for first-year students"
   - System Prompt: "You are a psychology instructor. Provide clear explanations suitable for introductory students. Use examples from everyday life when possible."

2. **Create Contexts**:
   - "Psychology Textbook Chapters" (PDF context)
   - "Course Lecture Notes" (MARKDOWN context)
   - "Common Psychology Questions" (FAQ context)

3. **Upload Content**:
   - Upload PDF chapters to the textbook context
   - Add lecture notes as markdown files
   - Create FAQ items for common student questions

4. **Associate with Topic**:
   - Edit the topic to link all three contexts
   - Test with sample questions

### Example 2: Bulk Content Migration

1. **Prepare Content**:
   - Review all existing materials
   - Organize files by subject and type
   - Create contexts for each major topic area

2. **Bulk Upload**:
   - Upload similar files to appropriate contexts
   - Use descriptive titles and consistent metadata
   - Process files in batches to avoid system overload

3. **Quality Check**:
   - Review auto-extracted content for accuracy
   - Update titles and metadata as needed
   - Test AI responses with sample questions

4. **Bulk Association**:
   - Use bulk operations to assign contexts to topics
   - Update system prompts for consistency
   - Regenerate embeddings if needed

## Troubleshooting

### Common Issues

#### File Upload Problems

**Problem**: File upload fails with validation error
**Solution**:
- Check file size (must be under 10MB)
- Verify file format (PDF, Markdown, or text only)
- Ensure filename doesn't contain special characters
- Try uploading a smaller file to test

**Problem**: Content extraction fails
**Solution**:
- Verify the file isn't corrupted
- Check if the PDF is text-based (not scanned images)
- Try extracting content manually and entering it directly

#### Search and Display Issues

**Problem**: Topics or contexts don't appear in lists
**Solution**:
- Check the search filters and clear them if needed
- Verify you have the correct permissions
- Refresh the page and try again

**Problem**: Content doesn't appear in Q&A results
**Solution**:
- Ensure the context is properly associated with the topic
- Check if embeddings need to be regenerated
- Verify the content is properly extracted and saved

#### Bulk Operation Errors

**Problem**: Bulk operations fail with error messages
**Solution**:
- Check that all selected items are valid
- Verify you have permission to perform the operation
- Try the operation on a smaller batch of items

**Problem**: Embeddings regeneration takes too long
**Solution**:
- This is normal for large batches - operations run in background
- Check system logs for progress
- Contact system administrator if the process seems stuck

### Error Messages

**"File validation failed"**: The uploaded file doesn't meet security requirements. Check file type, size, and content.

**"Context not found"**: The selected context may have been deleted. Refresh the page and try again.

**"Permission denied"**: You don't have the necessary permissions for this operation. Contact your system administrator.

**"Embedding generation failed"**: There may be an issue with the OpenAI API connection. Check system configuration.

### Getting Help

1. **Check System Logs**: Ask your system administrator to review Django logs for detailed error information
2. **Test with Simple Content**: Try creating a simple context item with manual text content to isolate file-related issues
3. **Contact Support**: Provide specific error messages and steps to reproduce the problem
4. **Documentation**: Refer to the deployment guide for system configuration issues

## Security Considerations

### Access Control

1. **Password Security**:
   - Use strong, unique passwords for admin accounts
   - Change passwords regularly
   - Never share admin credentials

2. **User Permissions**:
   - Only grant admin access to trusted personnel
   - Review user access regularly
   - Remove access for former staff members

3. **Content Security**:
   - Review uploaded files for sensitive information
   - Ensure compliance with data protection regulations
   - Monitor content for inappropriate material

### File Upload Security

The system automatically:
- Validates file types and sizes
- Scans for malicious content
- Sanitizes filenames
- Stores files securely in MinIO

### Best Practices

1. **Regular Updates**: Keep the system updated with security patches
2. **Backup Strategy**: Maintain regular backups of content and configurations
3. **Monitor Access**: Review admin access logs regularly
4. **Content Review**: Periodically audit uploaded content for relevance and appropriateness

## Advanced Features

### Metadata Usage

Use JSON metadata to enhance content organization:

```json
{
  "subject": "Machine Learning",
  "difficulty": "advanced",
  "prerequisites": ["linear_algebra", "statistics"],
  "keywords": ["neural networks", "deep learning"],
  "last_reviewed": "2024-01-15"
}
```

### System Prompt Optimization

Effective system prompts improve AI response quality:

- **Be Specific**: Define the exact role and expertise level
- **Set Boundaries**: Specify what topics to focus on or avoid
- **Provide Examples**: Include sample question-answer pairs
- **Define Style**: Specify formal vs. casual, technical vs. accessible

### Integration with External Systems

- **Content Management**: The admin interface can be integrated with external content management systems
- **User Management**: LDAP/Active Directory integration available for enterprise deployments
- **API Access**: RESTful API available for programmatic content management

This guide provides comprehensive coverage of the Scholaria admin interface. For technical issues or advanced configuration, consult the deployment guide or contact your system administrator.
