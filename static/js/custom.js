// SouniQ Custom JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Initialize file upload drag & drop
    initFileUpload();
    
    // Initialize task progress polling
    initTaskPolling();
    
    // Initialize audio players
    initAudioPlayers();
    
    // Auto-hide alerts after 5 seconds
    setTimeout(function() {
        var alerts = document.querySelectorAll('.alert');
        alerts.forEach(function(alert) {
            var bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        });
    }, 5000);
});

// File upload with drag & drop
function initFileUpload() {
    const uploadAreas = document.querySelectorAll('.file-upload-area');
    
    uploadAreas.forEach(function(area) {
        // Skip if this area already has specific handlers (like in modal)
        if (area.hasAttribute('data-handled')) {
            return;
        }
        
        // Look for the file input - it might be in a hidden div next to the area
        let fileInput = area.querySelector('input[type="file"]');
        if (!fileInput) {
            // If not found inside, look for it as a sibling
            const nextDiv = area.nextElementSibling;
            if (nextDiv) {
                fileInput = nextDiv.querySelector('input[type="file"]');
            }
        }
        
        if (!fileInput) {
            console.log('No file input found for upload area');
            return;
        }
        
        console.log('Initializing file upload for:', fileInput.id);
        
        // Mark as handled to avoid duplicate handlers
        area.setAttribute('data-handled', 'true');
        
        // Drag & drop events
        area.addEventListener('dragover', function(e) {
            e.preventDefault();
            e.stopPropagation();
            area.classList.add('dragover');
        });
        
        area.addEventListener('dragleave', function(e) {
            e.preventDefault();
            e.stopPropagation();
            area.classList.remove('dragover');
        });
        
        area.addEventListener('drop', function(e) {
            e.preventDefault();
            e.stopPropagation();
            area.classList.remove('dragover');
            
            const files = e.dataTransfer.files;
            if (files.length > 0) {
                fileInput.files = files;
                // Trigger change event to activate validation and auto-fill
                fileInput.dispatchEvent(new Event('change', { bubbles: true }));
                updateFileInfo(fileInput, files[0]);
            }
        });
        
        // Click to select file - only if not in a modal
        if (!area.closest('.modal')) {
            area.addEventListener('click', function(e) {
                e.preventDefault();
                e.stopPropagation();
                console.log('Upload area clicked, triggering file input');
                fileInput.click();
            });
        }
        
        // File input change
        fileInput.addEventListener('change', function() {
            console.log('File input changed, files:', this.files.length);
            if (this.files.length > 0) {
                updateFileInfo(this, this.files[0]);
                area.classList.add('file-selected');
            } else {
                area.classList.remove('file-selected');
            }
        });
    });
}

// Update file information display
function updateFileInfo(input, file) {
    const uploadArea = input.closest('.file-upload-area') || 
                      input.parentElement.previousElementSibling;
    
    if (!uploadArea) {
        console.log('Upload area not found for file info update');
        return;
    }
    
    let fileInfo = uploadArea.querySelector('.file-info');
    if (!fileInfo) {
        fileInfo = document.createElement('div');
        fileInfo.className = 'file-info mt-3 p-2 bg-light rounded';
        uploadArea.appendChild(fileInfo);
    }
    
    const fileSize = (file.size / (1024 * 1024)).toFixed(2);
    const fileIcon = getFileIcon(file.type || file.name);
    
    fileInfo.innerHTML = `
        <div class="d-flex align-items-center justify-content-center text-success">
            <i class="${fileIcon} text-primary me-2"></i>
            <span class="fw-medium me-2">${file.name}</span>
            <span class="text-muted">(${fileSize} MB)</span>
        </div>
        <small class="text-muted d-block mt-1">Archivo seleccionado correctamente</small>
    `;
}

function getFileIcon(typeOrName) {
    if (typeOrName.includes('audio') || typeOrName.match(/\.(mp3|wav|flac|aac|m4a)$/i)) {
        return 'fas fa-file-audio';
    }
    return 'fas fa-file';
}

// Task progress polling
function initTaskPolling() {
    const taskElements = document.querySelectorAll('[data-task-id]');
    
    taskElements.forEach(function(element) {
        const taskId = element.dataset.taskId;
        if (taskId) {
            pollTaskStatus(taskId, element);
        }
    });
}

function pollTaskStatus(taskId, element) {
    const pollInterval = setInterval(function() {
        fetch(`/music/api/task/${taskId}/status/`)
            .then(response => response.json())
            .then(data => {
                updateTaskProgress(element, data);
                
                if (data.status === 'completed') {
                    clearInterval(pollInterval);
                    
                    // Reload page after 2 seconds if task completed successfully
                    setTimeout(function() {
                        location.reload();
                    }, 2000);
                } else if (data.status === 'failed') {
                    clearInterval(pollInterval);
                    
                    // Show error and reload after 3 seconds to show error state
                    setTimeout(function() {
                        location.reload();
                    }, 3000);
                }
            })
            .catch(error => {
                console.error('Error polling task status:', error);
                clearInterval(pollInterval);
                
                // Reload to show any error state
                setTimeout(function() {
                    location.reload();
                }, 3000);
            });
    }, 3000); // Poll every 3 seconds
}

function updateTaskProgress(element, data) {
    const progressBar = element.querySelector('.progress-bar');
    const statusText = element.querySelector('.task-status');
    const progressText = element.querySelector('.task-progress');
    const detailedStatus = element.querySelector('.detailed-status');
    const errorMessage = element.querySelector('.error-message');
    
    if (progressBar) {
        progressBar.style.width = data.progress + '%';
        progressBar.setAttribute('aria-valuenow', data.progress);
        
        // Cambiar color de la barra según el estado
        if (data.status === 'failed') {
            progressBar.className = 'progress-bar bg-danger';
        } else if (data.status === 'completed') {
            progressBar.className = 'progress-bar bg-success';
        } else if (data.status === 'in_progress') {
            progressBar.className = 'progress-bar bg-warning';
        } else {
            progressBar.className = 'progress-bar bg-secondary';
        }
    }
    
    if (statusText) {
        statusText.textContent = getStatusText(data.status);
        statusText.className = `badge status-badge ${getStatusClass(data.status)}`;
    }
    
    if (progressText) {
        progressText.textContent = `${data.progress}%`;
    }
    
    // Mostrar mensaje de error si hay uno
    if (errorMessage && data.error_message) {
        errorMessage.textContent = data.error_message;
        errorMessage.style.display = 'block';
    } else if (errorMessage) {
        errorMessage.style.display = 'none';
    }
    
    // Mostrar estado detallado de Hugging Face si está disponible
    if (detailedStatus && data.detailed_status) {
        detailedStatus.textContent = data.detailed_status;
        detailedStatus.style.display = 'block';
    } else if (detailedStatus) {
        detailedStatus.style.display = 'none';
    }
    
    // Update element class
    element.className = element.className.replace(/\b(pending|in_progress|completed|failed)\b/g, '');
    element.classList.add(data.status);
}

function getStatusText(status) {
    const statusTexts = {
        'pending': 'Pendiente',
        'in_progress': 'Procesando',
        'completed': 'Completado',
        'failed': 'Error'
    };
    return statusTexts[status] || status;
}

function getStatusClass(status) {
    const statusClasses = {
        'pending': 'bg-secondary',
        'in_progress': 'bg-warning',
        'completed': 'bg-success',
        'failed': 'bg-danger'
    };
    return statusClasses[status] || 'bg-secondary';
}

// Audio player enhancements
function initAudioPlayers() {
    const audioPlayers = document.querySelectorAll('audio');
    
    audioPlayers.forEach(function(audio) {
        // Add custom controls if needed
        audio.addEventListener('loadstart', function() {
            const container = audio.closest('.audio-player');
            if (container) {
                container.classList.add('loading');
            }
        });
        
        audio.addEventListener('canplay', function() {
            const container = audio.closest('.audio-player');
            if (container) {
                container.classList.remove('loading');
            }
        });
        
        audio.addEventListener('error', function() {
            const container = audio.closest('.audio-player');
            if (container) {
                container.classList.remove('loading');
                container.innerHTML = '<div class="text-danger"><i class="fas fa-exclamation-triangle"></i> Error cargando audio</div>';
            }
        });
    });
}

// Confirmation dialogs
function confirmAction(message, callback) {
    if (confirm(message)) {
        callback();
    }
}

// Form validation helpers
function validateAudioFile(input) {
    const file = input.files[0];
    if (!file) return true;
    
    const allowedTypes = ['audio/mpeg', 'audio/wav', 'audio/flac', 'audio/aac', 'audio/m4a'];
    const maxSize = 50 * 1024 * 1024; // 50MB
    
    if (!allowedTypes.includes(file.type) && !file.name.match(/\.(mp3|wav|flac|aac|m4a)$/i)) {
        alert('Por favor, selecciona un archivo de audio válido (MP3, WAV, FLAC, AAC, M4A)');
        input.value = '';
        return false;
    }
    
    if (file.size > maxSize) {
        alert('El archivo no puede superar los 50MB');
        input.value = '';
        return false;
    }
    
    return true;
}

// Utility functions
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

function formatDuration(seconds) {
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = Math.floor(seconds % 60);
    return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
}

// Copy to clipboard function
function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(function() {
        // Show temporary success message
        const toast = document.createElement('div');
        toast.className = 'alert alert-success position-fixed top-0 end-0 m-3';
        toast.style.zIndex = '9999';
        toast.innerHTML = '<i class="fas fa-check me-2"></i>Copiado al portapapeles';
        document.body.appendChild(toast);
        
        setTimeout(function() {
            toast.remove();
        }, 3000);
    });
}

// Download file function
function downloadFile(url, filename) {
    const link = document.createElement('a');
    link.href = url;
    link.download = filename || '';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}

// Theme toggle (optional)
function toggleTheme() {
    document.body.classList.toggle('dark-theme');
    localStorage.setItem('theme', document.body.classList.contains('dark-theme') ? 'dark' : 'light');
}

// Load saved theme
if (localStorage.getItem('theme') === 'dark') {
    document.body.classList.add('dark-theme');
}
