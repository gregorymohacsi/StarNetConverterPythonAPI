const API_URL = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
    ? 'http://localhost:5000/api/process-file'
    : '/api/process-file';

async function processFile() {
    const fileInput = document.getElementById('fileInput');
    const statusDiv = document.getElementById('status');
    
    if (!fileInput.files.length) {
        showStatus('Please select a file first', 'error');
        return;
    }

    const file = fileInput.files[0];
    
    if (!file.name.toLowerCase().endsWith('.rpt')) {
        showStatus('Please select a .rpt file', 'error');
        return;
    }

    const formData = new FormData();
    formData.append('file', file);

    showStatus('Processing...', '');

    try {
        const response = await fetch(API_URL, {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            const errorText = await response.text();
            throw new Error(`Server error: ${errorText}`);
        }

        // Check response headers
        console.log('Response headers:', [...response.headers.entries()]);
        
        const blob = await response.blob();
        console.log('Response blob size:', blob.size);
        
        if (blob.size === 0) {
            throw new Error('Received empty file from server');
        }

        // Create download link
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = getFilename(response) || 'processed_file.txt';
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);

        showStatus('File processed successfully!', 'success');
    } catch (error) {
        console.error('Processing error:', error);
        showStatus(`Error: ${error.message}`, 'error');
    }
}

function getFilename(response) {
    const disposition = response.headers.get('content-disposition');
    if (!disposition) return null;
    
    const matches = /filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/.exec(disposition);
    if (matches != null && matches[1]) {
        return matches[1].replace(/['"]/g, '');
    }
    return null;
}

function showStatus(message, type) {
    const statusDiv = document.getElementById('status');
    statusDiv.innerHTML = `<p class="${type}">${message}</p>`;
}