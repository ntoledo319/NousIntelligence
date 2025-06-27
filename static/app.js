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
        this.registerServiceWorker();
        this.setupIntersectionObserver();
        this.initFeaturesMenu();
        
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
        // Try primary API endpoint first, then fallback to legacy
        const endpoints = [
            this.config.apiEndpoint,
            this.config.legacyApiEndpoint
        ].filter(Boolean);
        
        for (const endpoint of endpoints) {
            try {
                const response = await fetch(endpoint, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-Requested-With': 'XMLHttpRequest'
                    },
                    credentials: 'same-origin',
                    body: JSON.stringify({ message })
                });
                
                if (response.ok) {
                    return response;
                } else if (response.status !== 404) {
                    // If it's not a 404, return the response (auth error, etc.)
                    return response;
                }
            } catch (error) {
                console.warn(`API endpoint ${endpoint} failed:`, error);
                continue;
            }
        }
        
        // If all endpoints fail, throw error
        throw new Error('All API endpoints failed');
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
    
    // Service Worker registration for PWA functionality
    async registerServiceWorker() {
        if ('serviceWorker' in navigator) {
            try {
                const registration = await navigator.serviceWorker.register('/static/sw.js');
                console.log('Service Worker registered successfully:', registration);
                
                registration.addEventListener('updatefound', () => {
                    const newWorker = registration.installing;
                    newWorker.addEventListener('statechange', () => {
                        if (newWorker.state === 'installed' && navigator.serviceWorker.controller) {
                            this.showUpdateNotification();
                        }
                    });
                });
            } catch (error) {
                console.log('Service Worker registration failed:', error);
            }
        }
    }
    
    showUpdateNotification() {
        const notification = document.createElement('div');
        notification.className = 'update-notification';
        notification.innerHTML = `
            <div class="notification-content">
                <span>A new version is available!</span>
                <button class="update-btn" onclick="window.location.reload()">Update</button>
                <button class="dismiss-btn" onclick="this.parentElement.parentElement.remove()">×</button>
            </div>
        `;
        
        notification.style.cssText = `
            position: fixed; top: 1rem; right: 1rem;
            background: var(--surface-color); border: 1px solid var(--border-color);
            border-radius: 0.5rem; padding: 1rem; z-index: 1000; max-width: 300px;
            box-shadow: 0 4px 12px var(--shadow-color);
        `;
        
        document.body.appendChild(notification);
        setTimeout(() => notification.parentElement && notification.remove(), 10000);
    }
    
    setupIntersectionObserver() {
        if ('IntersectionObserver' in window) {
            this.messageObserver = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        entry.target.classList.add('message-visible');
                    }
                });
            }, { threshold: 0.1, rootMargin: '50px' });
        }
    }
    
    observeMessage(messageElement) {
        if (this.messageObserver) {
            this.messageObserver.observe(messageElement);
        }
    }

    initFeaturesMenu() {
        const featuresBtn = document.querySelector('.features-btn');
        const featuresDropdown = document.querySelector('.features-dropdown');

        if (featuresBtn && featuresDropdown) {
            featuresBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                featuresDropdown.style.display = featuresDropdown.style.display === 'block' ? 'none' : 'block';
            });

            document.addEventListener('click', (e) => {
                if (!featuresBtn.contains(e.target) && !featuresDropdown.contains(e.target)) {
                    featuresDropdown.style.display = 'none';
                }
            });
        }
    }

    initErrorHandling() {
        // Global error handler for unhandled promises
        window.addEventListener('unhandledrejection', (event) => {
            console.error('Unhandled promise rejection:', event.reason);
            event.preventDefault();
        });
    }

    // Enhanced functionality for new features
    initSearchSystem() {
        const searchInput = document.getElementById('global-search');
        const searchBtn = document.getElementById('search-btn');
        const searchResults = document.getElementById('search-results');

        if (!searchInput || !searchBtn || !searchResults) return;

        let searchTimeout;

        searchInput.addEventListener('input', (e) => {
            clearTimeout(searchTimeout);
            const query = e.target.value.trim();

            if (query.length < 2) {
                searchResults.style.display = 'none';
                return;
            }

            searchTimeout = setTimeout(() => {
                this.performSearch(query);
            }, 300);
        });

        searchInput.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                searchResults.style.display = 'none';
                searchInput.blur();
            }
        });

        searchBtn.addEventListener('click', () => {
            const query = searchInput.value.trim();
            if (query) {
                this.performSearch(query);
            }
        });

        // Close search results when clicking outside
        document.addEventListener('click', (e) => {
            if (!searchInput.contains(e.target) && !searchResults.contains(e.target)) {
                searchResults.style.display = 'none';
            }
        });
    }

    async performSearch(query) {
        const searchResults = document.getElementById('search-results');
        
        try {
            const response = await fetch(`/api/v1/search/?q=${encodeURIComponent(query)}`, {
                credentials: 'same-origin'
            });

            if (response.ok) {
                const data = await response.json();
                this.displaySearchResults(data.data);
            } else {
                this.displaySearchResults({ results: [], total_count: 0 });
            }
        } catch (error) {
            console.error('Search error:', error);
            this.displaySearchResults({ results: [], total_count: 0 });
        }
    }

    displaySearchResults(searchData) {
        const searchResults = document.getElementById('search-results');
        
        if (searchData.results.length === 0) {
            searchResults.innerHTML = '<div class="notification-empty">No results found</div>';
        } else {
            searchResults.innerHTML = searchData.results.map(result => `
                <div class="search-result-item" onclick="window.chatApp.openSearchResult('${result.content_type}', '${result.content_id}')">
                    <div class="search-result-title">${result.title}</div>
                    <div class="search-result-content">${result.content.substring(0, 100)}...</div>
                    <span class="search-result-type">${result.content_type}</span>
                </div>
            `).join('');
        }

        searchResults.style.display = 'block';
    }

    openSearchResult(contentType, contentId) {
        // Handle opening search results based on content type
        const routes = {
            'task': '/tasks',
            'chat': '/app',
            'note': '/notes',
            'goal': '/goals',
            'health': '/health'
        };

        const route = routes[contentType] || '/app';
        window.location.href = `${route}#${contentId}`;
    }

    initNotificationCenter() {
        const notificationBtn = document.getElementById('notification-btn');
        const notificationDropdown = document.getElementById('notification-dropdown');
        const notificationBadge = document.getElementById('notification-badge');
        const markAllReadBtn = document.getElementById('mark-all-read');

        if (!notificationBtn || !notificationDropdown) return;

        notificationBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            if (notificationDropdown.style.display === 'block') {
                notificationDropdown.style.display = 'none';
            } else {
                this.loadNotifications();
                notificationDropdown.style.display = 'block';
            }
        });

        if (markAllReadBtn) {
            markAllReadBtn.addEventListener('click', () => {
                this.markAllNotificationsRead();
            });
        }

        // Close dropdown when clicking outside
        document.addEventListener('click', (e) => {
            if (!notificationBtn.contains(e.target) && !notificationDropdown.contains(e.target)) {
                notificationDropdown.style.display = 'none';
            }
        });

        // Load notification summary on init
        this.loadNotificationSummary();

        // Poll for new notifications every minute
        setInterval(() => {
            this.loadNotificationSummary();
        }, 60000);
    }

    async loadNotifications() {
        try {
            const response = await fetch('/api/v1/notifications/', {
                credentials: 'same-origin'
            });

            if (response.ok) {
                const data = await response.json();
                this.displayNotifications(data.data.notifications);
            }
        } catch (error) {
            console.error('Error loading notifications:', error);
        }
    }

    async loadNotificationSummary() {
        try {
            const response = await fetch('/api/v1/notifications/summary', {
                credentials: 'same-origin'
            });

            if (response.ok) {
                const data = await response.json();
                this.updateNotificationBadge(data.data.total_unread);
            }
        } catch (error) {
            console.error('Error loading notification summary:', error);
        }
    }

    updateNotificationBadge(count) {
        const badge = document.getElementById('notification-badge');
        if (badge) {
            if (count > 0) {
                badge.textContent = count > 99 ? '99+' : count.toString();
                badge.style.display = 'block';
            } else {
                badge.style.display = 'none';
            }
        }
    }

    displayNotifications(notifications) {
        const notificationList = document.getElementById('notification-list');
        
        if (notifications.length === 0) {
            notificationList.innerHTML = '<div class="notification-empty">No notifications</div>';
        } else {
            notificationList.innerHTML = notifications.map(notification => `
                <div class="notification-item ${!notification.is_read ? 'unread' : ''}" 
                     onclick="window.chatApp.handleNotificationClick(${notification.id})">
                    <div class="notification-title">${notification.title}</div>
                    <div class="notification-message">${notification.message}</div>
                    <div class="notification-time">${this.formatTimeAgo(notification.created_at)}</div>
                </div>
            `).join('');
        }
    }

    async handleNotificationClick(notificationId) {
        try {
            await fetch(`/api/v1/notifications/${notificationId}/read`, {
                method: 'POST',
                credentials: 'same-origin'
            });
            
            this.loadNotifications();
            this.loadNotificationSummary();
        } catch (error) {
            console.error('Error marking notification as read:', error);
        }
    }

    async markAllNotificationsRead() {
        try {
            await fetch('/api/v1/notifications/mark-all-read', {
                method: 'POST',
                credentials: 'same-origin'
            });
            
            this.loadNotifications();
            this.loadNotificationSummary();
        } catch (error) {
            console.error('Error marking all notifications as read:', error);
        }
    }

    initQuickActions() {
        const fabMain = document.getElementById('fab-main');
        const fabMenu = document.getElementById('fab-menu');

        if (!fabMain || !fabMenu) return;

        fabMain.addEventListener('click', (e) => {
            e.stopPropagation();
            if (fabMenu.style.display === 'block') {
                fabMenu.style.display = 'none';
            } else {
                fabMenu.style.display = 'block';
            }
        });

        // Handle fab action clicks
        document.querySelectorAll('.fab-action').forEach(action => {
            action.addEventListener('click', (e) => {
                const actionType = e.currentTarget.dataset.action;
                this.handleQuickAction(actionType);
                fabMenu.style.display = 'none';
            });
        });

        // Close menu when clicking outside
        document.addEventListener('click', (e) => {
            if (!fabMain.contains(e.target) && !fabMenu.contains(e.target)) {
                fabMenu.style.display = 'none';
            }
        });
    }

    handleQuickAction(actionType) {
        switch (actionType) {
            case 'new-task':
                this.openTaskModal();
                break;
            case 'voice-note':
                this.startVoiceNote();
                break;
            case 'quick-mood':
                this.openMoodLogger();
                break;
            case 'new-goal':
                this.openGoalModal();
                break;
            case 'analytics':
                window.location.href = '/analytics';
                break;
        }
    }

    openTaskModal() {
        const message = prompt('What task would you like to add?');
        if (message) {
            this.messageInput.value = `Add task: ${message}`;
            this.sendMessage();
        }
    }

    startVoiceNote() {
        alert('Voice note feature coming soon!');
    }

    openMoodLogger() {
        const mood = prompt('How are you feeling right now? (1-10)');
        if (mood && !isNaN(mood) && mood >= 1 && mood <= 10) {
            this.messageInput.value = `Log mood: ${mood}/10`;
            this.sendMessage();
        }
    }

    openGoalModal() {
        window.location.href = '/goals';
    }

    initKeyboardShortcuts() {
        document.addEventListener('keydown', (e) => {
            // Ctrl/Cmd + / : Open search
            if ((e.ctrlKey || e.metaKey) && e.key === '/') {
                e.preventDefault();
                const searchInput = document.getElementById('global-search');
                if (searchInput) {
                    searchInput.focus();
                }
            }

            // Ctrl/Cmd + K : Open quick actions
            if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
                e.preventDefault();
                const fabMain = document.getElementById('fab-main');
                if (fabMain) {
                    fabMain.click();
                }
            }

            // Ctrl/Cmd + N : New task
            if ((e.ctrlKey || e.metaKey) && e.key === 'n') {
                e.preventDefault();
                this.openTaskModal();
            }

            // Escape : Close modals/dropdowns
            if (e.key === 'Escape') {
                this.closeAllModals();
            }
        });
    }

    closeAllModals() {
        // Close search results
        const searchResults = document.getElementById('search-results');
        if (searchResults) searchResults.style.display = 'none';

        // Close notification dropdown
        const notificationDropdown = document.getElementById('notification-dropdown');
        if (notificationDropdown) notificationDropdown.style.display = 'none';

        // Close fab menu
        const fabMenu = document.getElementById('fab-menu');
        if (fabMenu) fabMenu.style.display = 'none';

        // Close help panel
        const helpPanel = document.getElementById('help-panel');
        if (helpPanel) helpPanel.style.display = 'none';

        // Close onboarding
        const onboardingOverlay = document.getElementById('onboarding-overlay');
        if (onboardingOverlay) onboardingOverlay.style.display = 'none';
    }

    initOnboardingSystem() {
        const onboardingOverlay = document.getElementById('onboarding-overlay');
        const closeOnboarding = document.getElementById('close-onboarding');

        if (!onboardingOverlay) return;

        // Check if user has completed onboarding
        const hasCompletedOnboarding = localStorage.getItem('nous-onboarding-completed');
        
        if (!hasCompletedOnboarding) {
            setTimeout(() => {
                onboardingOverlay.style.display = 'flex';
            }, 1000);
        }

        if (closeOnboarding) {
            closeOnboarding.addEventListener('click', () => {
                onboardingOverlay.style.display = 'none';
                localStorage.setItem('nous-onboarding-completed', 'true');
            });
        }

        // Handle onboarding step navigation
        document.querySelectorAll('.onboarding-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const action = e.target.dataset.action;
                this.handleOnboardingAction(action);
            });
        });
    }

    handleOnboardingAction(action) {
        const progressFill = document.querySelector('.progress-fill');
        const progressText = document.querySelector('.progress-text');

        switch (action) {
            case 'set-goals':
                this.showOnboardingStep(2, '66.66%', '2 of 3');
                break;
            case 'explore-features':
                this.showOnboardingStep(3, '100%', '3 of 3');
                break;
            case 'finish-onboarding':
                document.getElementById('onboarding-overlay').style.display = 'none';
                localStorage.setItem('nous-onboarding-completed', 'true');
                this.addSystemMessage('Welcome to NOUS! 🎉 You\'re all set up and ready to go!');
                break;
        }

        if (progressFill && progressText) {
            if (action === 'set-goals') {
                progressFill.style.width = '66.66%';
                progressText.textContent = '2 of 3';
            } else if (action === 'explore-features') {
                progressFill.style.width = '100%';
                progressText.textContent = '3 of 3';
            }
        }
    }

    showOnboardingStep(stepNumber, progressWidth, progressText) {
        document.querySelectorAll('.onboarding-step').forEach((step, index) => {
            step.style.display = (index + 1 === stepNumber) ? 'block' : 'none';
        });

        const progressFill = document.querySelector('.progress-fill');
        const progressTextEl = document.querySelector('.progress-text');
        
        if (progressFill) progressFill.style.width = progressWidth;
        if (progressTextEl) progressTextEl.textContent = progressText;
    }

    initHelpSystem() {
        const helpToggle = document.getElementById('help-toggle');
        const helpPanel = document.getElementById('help-panel');
        const closeHelp = document.getElementById('close-help');

        if (!helpToggle || !helpPanel) return;

        helpToggle.addEventListener('click', (e) => {
            e.stopPropagation();
            if (helpPanel.style.display === 'block') {
                helpPanel.style.display = 'none';
            } else {
                helpPanel.style.display = 'block';
            }
        });

        if (closeHelp) {
            closeHelp.addEventListener('click', () => {
                helpPanel.style.display = 'none';
            });
        }

        // Close help when clicking outside
        document.addEventListener('click', (e) => {
            if (!helpToggle.contains(e.target) && !helpPanel.contains(e.target)) {
                helpPanel.style.display = 'none';
            }
        });
    }

    formatTimeAgo(timestamp) {
        const now = new Date();
        const time = new Date(timestamp);
        const diffInSeconds = Math.floor((now - time) / 1000);

        if (diffInSeconds < 60) return 'Just now';
        if (diffInSeconds < 3600) return `${Math.floor(diffInSeconds / 60)}m ago`;
        if (diffInSeconds < 86400) return `${Math.floor(diffInSeconds / 3600)}h ago`;
        return `${Math.floor(diffInSeconds / 86400)}d ago`;
    }

    // Activity tracking for analytics
    trackActivity(activityType, activityCategory = null, activityData = {}, durationSeconds = 0) {
        fetch('/api/v1/analytics/activity', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            credentials: 'same-origin',
            body: JSON.stringify({
                activity_type: activityType,
                activity_category: activityCategory,
                activity_data: activityData,
                duration_seconds: durationSeconds,
                session_id: this.sessionId || 'default'
            })
        }).catch(error => {
            console.warn('Activity tracking failed:', error);
        });
    }

    // Enhanced initialization
    initEnhancedFeatures() {
        this.initSearchSystem();
        this.initNotificationCenter();
        this.initQuickActions();
        this.initKeyboardShortcuts();
        this.initOnboardingSystem();
        this.initHelpSystem();
        
        // Track app initialization
        this.trackActivity('app_init', 'engagement');
        
        // Generate session ID for activity tracking
        this.sessionId = 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
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

// Enhanced ChatApp methods for new features
ChatApp.prototype.initEnhancedFeatures = function() {
    this.initSearchSystem();
    this.initNotificationCenter();
    this.initQuickActions();
    this.initKeyboardShortcuts();
    this.initOnboardingSystem();
    this.initHelpSystem();
    
    // Track app initialization
    this.trackActivity('app_init', 'engagement');
    
    // Generate session ID for activity tracking
    this.sessionId = 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
};

ChatApp.prototype.initSearchSystem = function() {
    const searchInput = document.getElementById('global-search');
    const searchBtn = document.getElementById('search-btn');
    const searchResults = document.getElementById('search-results');

    if (!searchInput || !searchBtn || !searchResults) return;

    let searchTimeout;
    const self = this;

    searchInput.addEventListener('input', (e) => {
        clearTimeout(searchTimeout);
        const query = e.target.value.trim();

        if (query.length < 2) {
            searchResults.style.display = 'none';
            return;
        }

        searchTimeout = setTimeout(() => {
            self.performSearch(query);
        }, 300);
    });

    searchInput.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') {
            searchResults.style.display = 'none';
            searchInput.blur();
        }
    });

    searchBtn.addEventListener('click', () => {
        const query = searchInput.value.trim();
        if (query) {
            self.performSearch(query);
        }
    });

    // Close search results when clicking outside
    document.addEventListener('click', (e) => {
        if (!searchInput.contains(e.target) && !searchResults.contains(e.target)) {
            searchResults.style.display = 'none';
        }
    });
};

ChatApp.prototype.performSearch = async function(query) {
    const searchResults = document.getElementById('search-results');
    
    try {
        const response = await fetch(`/api/v1/search/?q=${encodeURIComponent(query)}`, {
            credentials: 'same-origin'
        });

        if (response.ok) {
            const data = await response.json();
            this.displaySearchResults(data.data);
        } else {
            this.displaySearchResults({ results: [], total_count: 0 });
        }
    } catch (error) {
        console.error('Search error:', error);
        this.displaySearchResults({ results: [], total_count: 0 });
    }
};

ChatApp.prototype.displaySearchResults = function(searchData) {
    const searchResults = document.getElementById('search-results');
    
    if (searchData.results.length === 0) {
        searchResults.innerHTML = '<div class="notification-empty">No results found</div>';
    } else {
        searchResults.innerHTML = searchData.results.map(result => `
            <div class="search-result-item" onclick="window.chatApp.openSearchResult('${result.content_type}', '${result.content_id}')">
                <div class="search-result-title">${result.title}</div>
                <div class="search-result-content">${result.content.substring(0, 100)}...</div>
                <span class="search-result-type">${result.content_type}</span>
            </div>
        `).join('');
    }

    searchResults.style.display = 'block';
};

ChatApp.prototype.initNotificationCenter = function() {
    const notificationBtn = document.getElementById('notification-btn');
    const notificationDropdown = document.getElementById('notification-dropdown');
    const markAllReadBtn = document.getElementById('mark-all-read');
    const self = this;

    if (!notificationBtn || !notificationDropdown) return;

    notificationBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        if (notificationDropdown.style.display === 'block') {
            notificationDropdown.style.display = 'none';
        } else {
            self.loadNotifications();
            notificationDropdown.style.display = 'block';
        }
    });

    if (markAllReadBtn) {
        markAllReadBtn.addEventListener('click', () => {
            self.markAllNotificationsRead();
        });
    }

    // Close dropdown when clicking outside
    document.addEventListener('click', (e) => {
        if (!notificationBtn.contains(e.target) && !notificationDropdown.contains(e.target)) {
            notificationDropdown.style.display = 'none';
        }
    });

    // Load notification summary on init
    this.loadNotificationSummary();

    // Poll for new notifications every minute
    setInterval(() => {
        self.loadNotificationSummary();
    }, 60000);
};

ChatApp.prototype.initQuickActions = function() {
    const fabMain = document.getElementById('fab-main');
    const fabMenu = document.getElementById('fab-menu');
    const self = this;

    if (!fabMain || !fabMenu) return;

    fabMain.addEventListener('click', (e) => {
        e.stopPropagation();
        if (fabMenu.style.display === 'block') {
            fabMenu.style.display = 'none';
        } else {
            fabMenu.style.display = 'block';
        }
    });

    // Handle fab action clicks
    document.querySelectorAll('.fab-action').forEach(action => {
        action.addEventListener('click', (e) => {
            const actionType = e.currentTarget.dataset.action;
            self.handleQuickAction(actionType);
            fabMenu.style.display = 'none';
        });
    });

    // Close menu when clicking outside
    document.addEventListener('click', (e) => {
        if (!fabMain.contains(e.target) && !fabMenu.contains(e.target)) {
            fabMenu.style.display = 'none';
        }
    });
};

ChatApp.prototype.initKeyboardShortcuts = function() {
    const self = this;
    
    document.addEventListener('keydown', (e) => {
        // Ctrl/Cmd + / : Open search
        if ((e.ctrlKey || e.metaKey) && e.key === '/') {
            e.preventDefault();
            const searchInput = document.getElementById('global-search');
            if (searchInput) {
                searchInput.focus();
            }
        }

        // Ctrl/Cmd + K : Open quick actions
        if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
            e.preventDefault();
            const fabMain = document.getElementById('fab-main');
            if (fabMain) {
                fabMain.click();
            }
        }

        // Ctrl/Cmd + N : New task
        if ((e.ctrlKey || e.metaKey) && e.key === 'n') {
            e.preventDefault();
            self.openTaskModal();
        }

        // Escape : Close modals/dropdowns
        if (e.key === 'Escape') {
            self.closeAllModals();
        }
    });
};

ChatApp.prototype.handleQuickAction = function(actionType) {
    switch (actionType) {
        case 'new-task':
            this.openTaskModal();
            break;
        case 'voice-note':
            this.startVoiceNote();
            break;
        case 'quick-mood':
            this.openMoodLogger();
            break;
        case 'new-goal':
            this.openGoalModal();
            break;
        case 'analytics':
            window.location.href = '/api/v1/analytics/dashboard-view';
            break;
    }
};

ChatApp.prototype.openTaskModal = function() {
    const message = prompt('What task would you like to add?');
    if (message) {
        this.messageInput.value = `Add task: ${message}`;
        this.sendMessage();
    }
};

ChatApp.prototype.trackActivity = function(activityType, activityCategory = null, activityData = {}, durationSeconds = 0) {
    fetch('/api/v1/analytics/activity', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        credentials: 'same-origin',
        body: JSON.stringify({
            activity_type: activityType,
            activity_category: activityCategory,
            activity_data: activityData,
            duration_seconds: durationSeconds,
            session_id: this.sessionId || 'default'
        })
    }).catch(error => {
        console.warn('Activity tracking failed:', error);
    });
};

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