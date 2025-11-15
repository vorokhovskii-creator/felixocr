document.addEventListener('DOMContentLoaded', function() {
    const uploadArea = document.getElementById('uploadArea');
    const fileInput = document.getElementById('fileInput');
    const fileButton = document.getElementById('fileButton');
    const previewContainer = document.getElementById('previewContainer');
    const previewImage = document.getElementById('previewImage');
    const processButton = document.getElementById('processButton');
    const removeImageButton = document.getElementById('removeImageButton');
    const resultsContainer = document.getElementById('resultsContainer');
    const resultsList = document.getElementById('resultsList');
    const errorContainer = document.getElementById('errorContainer');
    const errorMessage = document.getElementById('errorMessage');
    const buttonText = document.getElementById('buttonText');
    const loadingSpinner = document.getElementById('loadingSpinner');

    let selectedFile = null;

    // File selection
    fileButton.addEventListener('click', () => fileInput.click());

    fileInput.addEventListener('change', (e) => {
        const file = e.target.files[0];
        if (file) {
            handleFile(file);
        }
    });

    // Drag and drop
    uploadArea.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadArea.classList.add('drag-over');
    });

    uploadArea.addEventListener('dragleave', () => {
        uploadArea.classList.remove('drag-over');
    });

    uploadArea.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadArea.classList.remove('drag-over');
        
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            const file = files[0];
            if (isValidFile(file)) {
                handleFile(file);
            } else {
                showError('Invalid file type. Please select PNG, JPG, JPEG, or WEBP.');
            }
        }
    });

    function isValidFile(file) {
        const validTypes = ['image/png', 'image/jpeg', 'image/webp'];
        return validTypes.includes(file.type) || /\.(png|jpg|jpeg|webp)$/i.test(file.name);
    }

    function handleFile(file) {
        selectedFile = file;
        const reader = new FileReader();
        
        reader.onload = (e) => {
            previewImage.src = e.target.result;
            uploadArea.style.display = 'none';
            previewContainer.style.display = 'block';
            processButton.style.display = 'flex';
            errorContainer.style.display = 'none';
        };
        
        reader.readAsDataURL(file);
    }

    removeImageButton.addEventListener('click', () => {
        selectedFile = null;
        fileInput.value = '';
        uploadArea.style.display = 'block';
        previewContainer.style.display = 'none';
        processButton.style.display = 'none';
        resultsContainer.style.display = 'none';
        errorContainer.style.display = 'none';
    });

    processButton.addEventListener('click', async () => {
        if (!selectedFile) {
            showError('Please select a file first.');
            return;
        }

        await processImage();
    });

    async function processImage() {
        const formData = new FormData();
        formData.append('file', selectedFile);

        processButton.disabled = true;
        buttonText.style.display = 'none';
        loadingSpinner.style.display = 'inline-block';
        errorContainer.style.display = 'none';

        try {
            const response = await fetch('/api/process', {
                method: 'POST',
                body: formData
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || 'Failed to process image');
            }

            displayResults(data.data);
        } catch (error) {
            showError(error.message);
        } finally {
            processButton.disabled = false;
            buttonText.style.display = 'inline';
            loadingSpinner.style.display = 'none';
        }
    }

    function displayResults(data) {
        resultsList.innerHTML = '';
        
        if (data.numbers && data.numbers.length > 0) {
            data.numbers.forEach((item, index) => {
                const resultItem = document.createElement('div');
                resultItem.className = 'result-item';
                
                const rawRow = document.createElement('div');
                rawRow.className = 'result-row';
                rawRow.innerHTML = `
                    <div>
                        <div class="result-label">RAW</div>
                        <div class="result-value">${escapeHtml(item.raw)}</div>
                    </div>
                `;
                
                const normalizedRow = document.createElement('div');
                normalizedRow.className = 'result-row';
                const copyButton = document.createElement('button');
                copyButton.className = 'copy-button';
                copyButton.textContent = 'Copy';
                copyButton.addEventListener('click', () => copyToClipboard(item.normalized, copyButton));
                
                normalizedRow.innerHTML = `
                    <div>
                        <div class="result-label">NORMALIZED</div>
                        <div class="result-value">${escapeHtml(item.normalized)}</div>
                    </div>
                `;
                normalizedRow.appendChild(copyButton);
                
                resultItem.appendChild(rawRow);
                resultItem.appendChild(normalizedRow);
                resultsList.appendChild(resultItem);
            });
        } else {
            resultsList.innerHTML = '<p>No numbers found in the image.</p>';
        }

        resultsContainer.style.display = 'block';
    }

    function copyToClipboard(text, button) {
        navigator.clipboard.writeText(text).then(() => {
            const originalText = button.textContent;
            button.textContent = 'Copied!';
            button.classList.add('copied');
            
            setTimeout(() => {
                button.textContent = originalText;
                button.classList.remove('copied');
            }, 2000);
        }).catch(() => {
            showError('Failed to copy to clipboard');
        });
    }

    function showError(message) {
        errorMessage.textContent = message;
        errorContainer.style.display = 'block';
    }

    function escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
});
