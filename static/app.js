/**
 * NOUS Chat Application - JavaScript
 * Professional-grade chat interface with theme management
 */

class ChatApp {
    constructor(config) {
        this.config = config;
        this.messages = [];
        this.currentTheme = this.loadTheme();
        
        this.initializeElements();
        this.initializeEventListeners();
        this.initializeTheme();
        this.setupAutoResize();
        
        console.log('NOUS Chat App initialized');
    }
    
    initializeElements() {
        // Chat elements
        this.chatMessages = document.getElementById('chat-messages');
        this.messageInput = document.getElementById('message-input');
        this.sendBtn = document.getElementById('send-btn');
        this.chatForm = document.getElementById('chat-form');
        this.charCount = document.getElementById('char-count');
        this.clearBtn = document.getElementById('clear-chat');
        this.loadingIndicator = document.getElementById('loading-indicator');
        
        // Theme elements
        this.themeSelect = document.getElementById('theme-select');
        
        // Validation
        if (!this.chatMessages || !this.messageInput || !this.sendBtn) {
            console.error('Required chat elements not found');
            return;
        }
    }
    
    initializeEventListeners() {
        // Form submission
        this.chatForm.addEventListener('submit', (e) => {
            e.preventDefault();
            this.sendMessage();
        });
        
        // Input handling
        this.messageInput.addEventListener('input', () => {
            this.updateCharCount();
            this.updateSendButton();
        });
        
        // Enter key handling (Shift+Enter for new line, Enter to send)
        this.messageInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });
        
        // Clear chat
        this.clearBtn.addEventListener('click', () => {
            this.clearChat();
        });
        
        // Theme selector
        if (this.themeSelect) {
            this.themeSelect.addEventListener('change', (e) => {
                this.changeTheme(e.target.value);
            });
        }
        
        // Auto-scroll to bottom when new messages arrive
        this.setupAutoScroll();
    }
    
    initializeTheme() {
        // Set initial theme
        document.body.setAttribute('data-theme', this.currentTheme);
        if (this.themeSelect) {
            this.themeSelect.value = this.currentTheme;
        }
    }
    
    setupAutoResize() {
        // Auto-resize textarea
        this.messageInput.addEventListener('input', () => {
            this.messageInput.style.height = 'auto';
            this.messageInput.style.height = Math.min(this.messageInput.scrollHeight, 120) + 'px';
        });
    }
    
    setupAutoScroll() {
        // Observer for auto-scrolling
        const observer = new MutationObserver(() => {
            this.scrollToBottom();
        });
        
        observer.observe(this.chatMessages, {
            childList: true,
            subtree: true
        });
    }
    
    async sendMessage() {
        const message = this.messageInput.value.trim();
        
        if (!message) {
            return;
        }
        
        // Disable input while sending
        this.setInputEnabled(false);
        this.showLoading(true);
        
        try {
            // Add user message to chat
            this.addMessage({
                content: message,
                sender: 'user',
                timestamp: new Date()
            });
            
            // Clear input
            this.messageInput.value = '';
            this.updateCharCount();
            this.messageInput.style.height = 'auto';
            
            // Send to API
            const response = await this.callChatAPI(message);
            
            if (response.ok) {
                const data = await response.json();
                
                // Add assistant response
                this.addMessage({
                    content: data.message,
                    sender: 'assistant',
                    timestamp: new Date(data.timestamp)
                });
            } else {
                throw new Error(`API Error: ${response.status}`);
            }
            
        } catch (error) {
            console.error('Error sending message:', error);
            
            // Add error message
            this.addMessage({
                content: 'Sorry, I encountered an error processing your message. Please try again.',
                sender: 'system',
                timestamp: new Date(),
                isError: true
            });
        } finally {
            this.setInputEnabled(true);
            this.showLoading(false);
            this.messageInput.focus();
        }
    }
    
    async callChatAPI(message) {
        const response = await fetch(this.config.apiEndpoint, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-Requested-With': 'XMLHttpRequest'
            },
            credentials: 'same-origin',
            body: JSON.stringify({ message })
        });
        
        return response;
    }
    
    addMessage(messageData) {
        const messageElement = this.createMessageElement(messageData);
        this.chatMessages.appendChild(messageElement);
        
        // Store message
        this.messages.push(messageData);
        
        // Scroll to bottom
        this.scrollToBottom();
    }
    
    createMessageElement(messageData) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message-bubble ${messageData.sender}-message`;
        
        if (messageData.isError) {
            messageDiv.classList.add('error-message');
        }
        
        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';
        
        // Handle different content types
        if (typeof messageData.content === 'string') {
            // Simple text content
            contentDiv.textContent = messageData.content;
        } else if (messageData.content.html) {
            // HTML content
            contentDiv.innerHTML = messageData.content.html;
        }
        
        const timeDiv = document.createElement('div');
        timeDiv.className = 'message-time';
        timeDiv.textContent = this.formatTime(messageData.timestamp);
        
        messageDiv.appendChild(contentDiv);
        messageDiv.appendChild(timeDiv);
        
        return messageDiv;
    }
    
    formatTime(timestamp) {
        const date = new Date(timestamp);
        return date.toLocaleTimeString([], { 
            hour: '2-digit', 
            minute: '2-digit' 
        });
    }
    
    scrollToBottom() {
        this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
    }
    
    updateCharCount() {
        const count = this.messageInput.value.length;
        this.charCount.textContent = count;
        
        // Color coding for character count
        if (count > 1800) {
            this.charCount.style.color = 'var(--error-color)';
        } else if (count > 1500) {
            this.charCount.style.color = 'var(--warning-color)';
        } else {
            this.charCount.style.color = 'var(--text-muted)';
        }
    }
    
    updateSendButton() {
        const hasText = this.messageInput.value.trim().length > 0;
        this.sendBtn.disabled = !hasText;
    }
    
    setInputEnabled(enabled) {
        this.messageInput.disabled = !enabled;
        this.sendBtn.disabled = !enabled;
        
        if (enabled) {
            this.updateSendButton();
        }
    }
    
    showLoading(show) {
        if (show) {
            this.loadingIndicator.classList.add('show');
        } else {
            this.loadingIndicator.classList.remove('show');
        }
    }
    
    clearChat() {
        if (confirm('Are you sure you want to clear the chat history?')) {
            // Remove all message bubbles except system messages
            const messages = this.chatMessages.querySelectorAll('.message-bubble:not(.system-message)');
            messages.forEach(message => message.remove());
            
            // Clear stored messages
            this.messages = this.messages.filter(msg => msg.sender === 'system');
            
            console.log('Chat cleared');
        }
    }
    
    // Theme Management
    changeTheme(themeName) {
        this.currentTheme = themeName;
        document.body.setAttribute('data-theme', themeName);
        this.saveTheme(themeName);
        
        console.log(`Theme changed to: ${themeName}`);
    }
    
    loadTheme() {
        return localStorage.getItem('nous-theme') || 'light';
    }
    
    saveTheme(themeName) {
        localStorage.setItem('nous-theme', themeName);
    }
    
    // Utility Methods
    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }
    
    // Public API
    getMessages() {
        return [...this.messages];
    }
    
    getCurrentTheme() {
        return this.currentTheme;
    }
    
    addSystemMessage(content) {
        this.addMessage({
            content,
            sender: 'system',
            timestamp: new Date()
        });
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    console.log('DOM loaded, waiting for chat app initialization...');
});

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ChatApp;
}

// Additional utility functions for theme management
function getAvailableThemes() {
    return ['light', 'dark', 'ocean', 'forest', 'sunset', 'purple', 'pink', 'peacock', 'love', 'star'];
}

function validateTheme(themeName) {
    return getAvailableThemes().includes(themeName);
}

// Global error handler for unhandled promises
window.addEventListener('unhandledrejection', (event) => {
    console.error('Unhandled promise rejection:', event.reason);
    event.preventDefault();
});

// Service worker registration for PWA capabilities (future enhancement)
if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
        navigator.serviceWorker.register('/static/sw.js')
            .then((registration) => {
                console.log('SW registered: ', registration);
            })
            .catch((registrationError) => {
                console.log('SW registration failed: ', registrationError);
            });
    });
}