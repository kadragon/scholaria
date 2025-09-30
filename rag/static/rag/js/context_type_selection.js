/**
 * Dynamic form switching for Context Type Selection
 * Shows/hides fields based on selected context type
 */

document.addEventListener('DOMContentLoaded', function() {
    const contextTypeField = document.querySelector('#id_context_type');
    if (!contextTypeField) return;

    // Initialize form state
    contextTypeChanged();

    // Listen for context type changes
    contextTypeField.addEventListener('change', contextTypeChanged);

    // Listen for processing status changes
    const processingStatusField = document.querySelector('#id_processing_status');
    if (processingStatusField) {
        processingStatusField.addEventListener('change', updateProcessingStatusHelp);
        updateProcessingStatusHelp(); // Initialize
    }

    function contextTypeChanged() {
        const contextType = contextTypeField.value;

        // Get all fieldsets
        const fileUploadFieldset = getFieldsetByTitle('File Upload');
        const markdownContentFieldset = getFieldsetByTitle('Markdown Content');
        const qaManagementFieldset = getFieldsetByTitle('Q&A Management');
        const contentFieldset = getFieldsetByTitle('Content');

        // Hide all type-specific fieldsets initially
        hideFieldset(fileUploadFieldset);
        hideFieldset(markdownContentFieldset);
        hideFieldset(qaManagementFieldset);
        hideFieldset(contentFieldset);

        // Show appropriate fieldsets based on context type
        switch(contextType) {
            case 'PDF':
                showFieldset(fileUploadFieldset);
                showFieldset(contentFieldset);
                updateFieldsetDescription(fileUploadFieldset,
                    'Upload a PDF file to automatically parse and create chunks.');
                break;

            case 'MARKDOWN':
                showFieldset(markdownContentFieldset);
                updateFieldsetDescription(markdownContentFieldset,
                    'Edit markdown content directly. Changes will automatically re-chunk the content when saved.');
                break;

            case 'FAQ':
                showFieldset(qaManagementFieldset);
                updateFieldsetDescription(qaManagementFieldset,
                    'Use the "Add Q&A Pair" action below to add question-answer pairs to this FAQ context.');
                break;

            default:
                // For new objects or unknown types, show PDF upload option
                showFieldset(fileUploadFieldset);
                updateFieldsetDescription(fileUploadFieldset,
                    'For PDF contexts, upload a file to automatically parse and create chunks.');
                break;
        }

        // Update help text for uploaded_file field based on context type
        updateUploadedFileHelp(contextType);

        // Update workflow steps display
        updateWorkflowSteps(contextType);
    }

    function getFieldsetByTitle(title) {
        const fieldsets = document.querySelectorAll('fieldset');
        for (let fieldset of fieldsets) {
            const legend = fieldset.querySelector('h2');
            if (legend && legend.textContent.trim() === title) {
                return fieldset;
            }
        }
        return null;
    }

    function showFieldset(fieldset) {
        if (fieldset) {
            fieldset.style.display = 'block';
        }
    }

    function hideFieldset(fieldset) {
        if (fieldset) {
            fieldset.style.display = 'none';
        }
    }

    function updateFieldsetDescription(fieldset, description) {
        if (!fieldset) return;

        const helpText = fieldset.querySelector('.description, .help');
        if (helpText) {
            helpText.textContent = description;
        }
    }

    function updateUploadedFileHelp(contextType) {
        const uploadedFileHelp = document.querySelector('#id_uploaded_file').parentNode.querySelector('.help');
        if (!uploadedFileHelp) return;

        let helpText = '';
        switch(contextType) {
            case 'PDF':
                helpText = 'Upload a PDF file to automatically parse and create chunks. File will be processed and discarded - not stored permanently.';
                break;
            case 'MARKDOWN':
                helpText = 'File upload not supported for Markdown contexts. Edit content directly in the Markdown Content field.';
                break;
            case 'FAQ':
                helpText = 'File upload not supported for FAQ contexts. Use the Q&A management tools instead.';
                break;
            default:
                helpText = 'Upload a PDF file to automatically parse and create chunks.';
                break;
        }

        uploadedFileHelp.textContent = helpText;
    }

    function updateWorkflowSteps(contextType) {
        // Hide all workflow types
        const workflowTypes = document.querySelectorAll('.workflow-type');
        workflowTypes.forEach(workflow => {
            workflow.style.display = 'none';
        });

        // Show appropriate workflow
        let workflowId = '';
        switch(contextType) {
            case 'PDF':
                workflowId = 'pdf-workflow';
                break;
            case 'MARKDOWN':
                workflowId = 'markdown-workflow';
                break;
            case 'FAQ':
                workflowId = 'faq-workflow';
                break;
            default:
                workflowId = 'pdf-workflow'; // Default to PDF workflow
                break;
        }

        const targetWorkflow = document.getElementById(workflowId);
        if (targetWorkflow) {
            targetWorkflow.style.display = 'block';
        }
    }

    function updateProcessingStatusHelp() {
        const processingStatusField = document.querySelector('#id_processing_status');
        if (!processingStatusField) return;

        const status = processingStatusField.value;
        const statusContainer = processingStatusField.parentNode;

        // Remove existing status indicator
        const existingIndicator = statusContainer.querySelector('.status-indicator');
        if (existingIndicator) {
            existingIndicator.remove();
        }

        // Add new status indicator
        const statusIndicator = document.createElement('span');
        statusIndicator.className = `status-indicator ${status.toLowerCase()}`;
        statusIndicator.textContent = status;

        // Insert after the field
        processingStatusField.parentNode.insertBefore(statusIndicator, processingStatusField.nextSibling);

        // Update help text based on status
        updateProcessingStatusHelpText(status);
    }

    function updateProcessingStatusHelpText(status) {
        const helpText = document.querySelector('#id_processing_status').parentNode.querySelector('.help');
        if (!helpText) return;

        let statusHelpText = '';
        switch(status) {
            case 'PENDING':
                statusHelpText = 'Content is ready to be processed. Save to begin processing.';
                break;
            case 'PROCESSING':
                statusHelpText = 'Content is currently being parsed and chunked. Please wait.';
                break;
            case 'COMPLETED':
                statusHelpText = 'Content has been successfully processed and chunked.';
                break;
            case 'FAILED':
                statusHelpText = 'Processing failed. Check the content and try again.';
                break;
            default:
                statusHelpText = 'Current processing status of the context.';
                break;
        }

        helpText.textContent = statusHelpText;
    }
});
