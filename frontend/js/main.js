async function processFile() {
    const fileInput = document.getElementById('fileInput');
    const statusDiv = document.getElementById('status');
    
    if (!fileInput.files.length) {
        showStatus('Please select a file first', 'error');
        return;
    }

    const file = fileInput.files[0];
    
    // Check if file has .rpt extension
    if (!file.name.toLowerCase().endsWith('.rpt')) {
        showStatus('Please select a .rpt file', 'error');
        return;
    }

    const formData = new FormData();
    formData.append('file', file);

    showStatus('Processing...', '');

    try {
        const response = await fetch('http://localhost:5000/process-file', {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        // Get the filename from the Content-Disposition header if available
        const contentDisposition = response.headers.get('Content-Disposition');
        let filename = 'processed_file';
        if (contentDisposition) {
            const match = contentDisposition.match(/filename="(.+)"/);
            if (match) {
                filename = match[1];
            }
        }

        // Create a blob from the response
        const blob = await response.blob();
        
        // Create a download link
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);

        showStatus('File processed successfully!', 'success');
    } catch (error) {
        showStatus(`Error: ${error.message}`, 'error');
    }
}

function showStatus(message, type) {
    const statusDiv = document.getElementById('status');
    statusDiv.innerHTML = `<p class="${type}">${message}</p>`;
}