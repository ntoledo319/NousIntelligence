/**
 * Voice Recording Functionality for NOUS Personal Assistant
 * Handles browser audio recording and speech-to-text conversion
 */

class VoiceRecorder {
    constructor(options = {}) {
        // Configuration with defaults
        this.config = {
            buttonId: options.buttonId || 'voiceBtn',
            outputElementId: options.outputElementId || null,
            formId: options.formId || null,
            inputFieldId: options.inputFieldId || null,
            autoSubmit: options.autoSubmit || false,
            recordingClass: options.recordingClass || 'recording',
            maxRecordingTime: options.maxRecordingTime || 30000, // 30 seconds max
            language: options.language || 'en-US'
        };
        
        // Initialize state
        this.isRecording = false;
        this.mediaRecorder = null;
        this.audioChunks = [];
        this.recordingTimeout = null;
        
        // Get DOM elements
        this.button = document.getElementById(this.config.buttonId);
        this.outputElement = this.config.outputElementId ? document.getElementById(this.config.outputElementId) : null;
        this.form = this.config.formId ? document.getElementById(this.config.formId) : null;
        this.inputField = this.config.inputFieldId ? document.getElementById(this.config.inputFieldId) : null;
        
        // Check if all required elements exist
        if (!this.button) {
            console.error('Voice recording button not found! Make sure the element ID is correct.');
            return;
        }
        
        // Check browser support
        if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
            console.warn('Browser does not support audio recording. Voice features will be disabled.');
            this.button.disabled = true;
            this.button.title = 'Voice recording not supported in this browser';
            this.button.classList.add('disabled');
            return;
        }
        
        // Set up speech recognition if available
        this.recognition = null;
        if ('webkitSpeechRecognition' in window) {
            this.recognition = new webkitSpeechRecognition();
            this.recognition.continuous = true;
            this.recognition.interimResults = true;
            this.recognition.lang = this.config.language;
            
            this.recognition.onresult = (event) => {
                const transcript = Array.from(event.results)
                    .map(result => result[0])
                    .map(result => result.transcript)
                    .join('');
                
                // Display the transcript
                if (this.inputField) {
                    this.inputField.value = transcript;
                }
                
                if (this.outputElement) {
                    this.outputElement.textContent = transcript;
                }
            };
            
            this.recognition.onerror = (event) => {
                console.error('Speech recognition error:', event.error);
                this.stopRecording();
            };
        } else {
            console.warn('Speech recognition not supported. Will record audio without transcription.');
        }
        
        // Set up event listeners
        this.button.addEventListener('click', this.toggleRecording.bind(this));
    }
    
    async toggleRecording() {
        if (this.isRecording) {
            this.stopRecording();
        } else {
            await this.startRecording();
        }
    }
    
    async startRecording() {
        try {
            // Request microphone access
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            
            // Reset audio chunks
            this.audioChunks = [];
            
            // Create media recorder
            this.mediaRecorder = new MediaRecorder(stream);
            
            // Set up event handlers
            this.mediaRecorder.ondataavailable = (event) => {
                this.audioChunks.push(event.data);
            };
            
            this.mediaRecorder.onstop = () => {
                // Combine audio chunks into a single blob
                const audioBlob = new Blob(this.audioChunks, { type: 'audio/wav' });
                
                // Convert to base64 for sending to server
                const reader = new FileReader();
                reader.readAsDataURL(audioBlob);
                reader.onloadend = () => {
                    const base64Audio = reader.result.split(',')[1];
                    
                    if (this.config.autoSubmit && this.form && this.inputField) {
                        // If auto-submit is enabled and we have a transcript, submit the form
                        if (this.inputField.value.trim() !== '') {
                            this.form.submit();
                        }
                    }
                    
                    // Optional: Send the audio to the server for processing
                    // this.sendAudioToServer(base64Audio);
                };
                
                // Stop all tracks
                stream.getTracks().forEach(track => track.stop());
            };
            
            // Start recording
            this.mediaRecorder.start();
            this.isRecording = true;
            
            // Update UI
            this.button.classList.add(this.config.recordingClass);
            this.button.innerHTML = '<i class="fas fa-stop"></i>';
            
            // Start speech recognition if available
            if (this.recognition) {
                this.recognition.start();
            }
            
            // Set timeout to stop recording after max time
            this.recordingTimeout = setTimeout(() => {
                if (this.isRecording) {
                    this.stopRecording();
                }
            }, this.config.maxRecordingTime);
            
        } catch (error) {
            console.error('Error starting recording:', error);
            this.showError('Could not access microphone. Please check your browser permissions.');
        }
    }
    
    stopRecording() {
        // Clear recording timeout
        if (this.recordingTimeout) {
            clearTimeout(this.recordingTimeout);
            this.recordingTimeout = null;
        }
        
        // Stop media recorder if it's active
        if (this.mediaRecorder && this.mediaRecorder.state !== 'inactive') {
            this.mediaRecorder.stop();
        }
        
        // Stop speech recognition if it's active
        if (this.recognition) {
            try {
                this.recognition.stop();
            } catch (e) {
                // Recognition may not be started, ignore errors
            }
        }
        
        // Update state and UI
        this.isRecording = false;
        this.button.classList.remove(this.config.recordingClass);
        this.button.innerHTML = '<i class="fas fa-microphone"></i>';
    }
    
    sendAudioToServer(base64Audio) {
        // Example function to send audio to server for processing
        // This would typically be customized based on your backend
        fetch('/api/speech-to-text', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ audio: base64Audio }),
        })
        .then(response => response.json())
        .then(data => {
            if (data.success && data.transcript) {
                // If the server returns a transcript, update the input field
                if (this.inputField) {
                    this.inputField.value = data.transcript;
                    
                    // Auto-submit if configured
                    if (this.config.autoSubmit && this.form) {
                        this.form.submit();
                    }
                }
                
                // Update output element if it exists
                if (this.outputElement) {
                    this.outputElement.textContent = data.transcript;
                }
            } else if (data.error) {
                this.showError(data.error);
            }
        })
        .catch(error => {
            console.error('Error sending audio to server:', error);
            this.showError('Failed to process audio. Please try again.');
        });
    }
    
    showError(message) {
        // Display error message to user
        const errorDiv = document.createElement('div');
        errorDiv.className = 'alert alert-danger alert-dismissible fade show mt-2';
        errorDiv.innerHTML = `
            <div class="d-flex align-items-center">
                <i class="fas fa-exclamation-circle me-2"></i>
                ${message}
            </div>
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        `;
        
        // Insert after the button
        this.button.parentNode.insertBefore(errorDiv, this.button.nextSibling);
        
        // Auto-dismiss after 5 seconds
        setTimeout(() => {
            errorDiv.classList.remove('show');
            setTimeout(() => errorDiv.remove(), 150);
        }, 5000);
    }
}

// Initialize voice recorder when the DOM is fully loaded
document.addEventListener('DOMContentLoaded', () => {
    // Check if voice button exists
    if (document.getElementById('voiceBtn')) {
        // Initialize with configuration
        const recorder = new VoiceRecorder({
            buttonId: 'voiceBtn',
            formId: 'commandForm',
            inputFieldId: 'commandInput',
            autoSubmit: true
        });
        
        // Make available globally
        window.voiceRecorder = recorder;
    }
}); 