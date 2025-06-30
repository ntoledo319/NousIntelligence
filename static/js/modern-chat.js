/**
 * NOUS Modern Chat Application
 * Combines the existing NOUS functionality with modern Tailwind UI
 */

class NOUSModernChat {
    constructor(config = {}) {
        this.config = {
            userName: config.userName || 'User',
            userAvatar: config.userAvatar || null,
            apiEndpoint: config.apiEndpoint || '/api/v1/chat',
            userEndpoint: config.userEndpoint || '/api/v1/user',
            legacyApiEndpoint: config.legacyApiEndpoint || '/api/chat',
            ...config
        };

        // DOM element selectors for modern UI
        this.selectors = {
            theme: {
                toggleBtn: '#theme-toggle',
                darkIcon: '#theme-toggle-dark-icon',
                lightIcon: '#theme-toggle-light-icon',
            },
            ui: {
                sidebar: '#sidebar',
                mainContent: 'main',
                backButton: '#back-to-conversations',
                conversationListItems: '#conversation-list li',
            },
            chat: {
                form: '#message-form',
                input: '#message-input',
                stream: '#message-stream',
                streamContainer: '#message-stream .space-y-4',
            },
            search: {
                input: '#global-search',
                btn: '#search-btn',
                results: '#search-results',
            },
            notifications: {
                btn: '#notification-btn',
                badge: '#notification-badge',
                dropdown: '#notification-dropdown',
                list: '#notification-list',
                markAllRead: '#mark-all-read',
            },
            fab: {
                main: '#fab-main',
                menu: '#fab-menu',
                actions: '.fab-action',
            }
        };

        this.initializeElements();
    }

    initializeElements() {
        // Cache DOM elements
        this.dom = {};
        Object.keys(this.selectors).forEach(category => {
            this.dom[category] = {};
            Object.keys(this.selectors[category]).forEach(element => {
                const selector = this.selectors[category][element];
                if (selector.startsWith('.')) {
                    this.dom[category][element] = document.querySelectorAll(selector);
                } else {
                    this.dom[category][element] = document.querySelector(selector);
                }
            });
        });
    }

    init() {
        this.initTheme();
        this.initResponsiveUI();
        this.initChat();
        this.initSearch();
        this.initNotifications();
        this.initQuickActions();
        this.initEnhancedFeatures();
        console.log("NOUS Modern Chat Initialized");
    }

    // --- THEME MANAGEMENT ---
    initTheme() {
        if (!this.dom.theme.toggleBtn) return;

        const isDarkMode = localStorage.getItem('color-theme') === 'dark' ||
            (!('color-theme' in localStorage) && window.matchMedia('(prefers-color-scheme: dark)').matches);
        this.updateTheme(isDarkMode);

        this.dom.theme.toggleBtn.addEventListener('click', () => {
            this.updateTheme(!document.documentElement.classList.contains('dark'));
        });
    }

    updateTheme(isDark) {
        if (isDark) {
            document.documentElement.classList.add('dark');
            localStorage.setItem('color-theme', 'dark');
            if (this.dom.theme.lightIcon) this.dom.theme.lightIcon.classList.remove('hidden');
            if (this.dom.theme.darkIcon) this.dom.theme.darkIcon.classList.add('hidden');
        } else {
            document.documentElement.classList.remove('dark');
            localStorage.setItem('color-theme', 'light');
            if (this.dom.theme.lightIcon) this.dom.theme.lightIcon.classList.add('hidden');
            if (this.dom.theme.darkIcon) this.dom.theme.darkIcon.classList.remove('hidden');
        }

        // Preserve existing NOUS theme compatibility
        document.body.setAttribute('data-theme', isDark ? 'dark' : 'light');
    }

    // --- RESPONSIVE UI ---
    initResponsiveUI() {
        if (this.dom.ui.conversationListItems) {
            this.dom.ui.conversationListItems.forEach(item => {
                item.addEventListener('click', () => {
                    if (window.innerWidth < 768) this.showMainContent();
                });
            });
        }

        if (this.dom.ui.backButton) {
            this.dom.ui.backButton.addEventListener('click', () => {
                if (window.innerWidth < 768) this.showSidebar();
            });
        }
    }

    showMainContent() {
        if (this.dom.ui.sidebar) this.dom.ui.sidebar.classList.add('hidden');
        if (this.dom.ui.mainContent) {
            this.dom.ui.mainContent.classList.remove('hidden');
            this.dom.ui.mainContent.classList.add('flex');
        }
    }

    showSidebar() {
        if (this.dom.ui.mainContent) {
            this.dom.ui.mainContent.classList.add('hidden');
            this.dom.ui.mainContent.classList.remove('flex');
        }
        if (this.dom.ui.sidebar) {
            this.dom.ui.sidebar.classList.remove('hidden');
            this.dom.ui.sidebar.classList.add('flex');
        }
    }

    // --- CHAT FUNCTIONALITY ---
    initChat() {
        if (!this.dom.chat.form) return;

        this.dom.chat.form.addEventListener('submit', async (e) => {
            e.preventDefault();
            const messageText = this.dom.chat.input.value.trim();
            if (messageText) {
                await this.sendMessage(messageText);
                this.dom.chat.input.value = '';
            }
        });

        // Auto-resize textarea
        if (this.dom.chat.input) {
            this.dom.chat.input.addEventListener('input', (e) => {
                e.target.style.height = 'auto';
                e.target.style.height = e.target.scrollHeight + 'px';
            });
        }
    }

    async sendMessage(message) {
        try {
            // Add user message immediately
            this.appendMessage({
                text: message,
                sender: 'user',
                timestamp: new Date()
            });

            // Show loading indicator
            this.showLoadingIndicator();

            // Send to API
            const response = await fetch(this.config.apiEndpoint, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    message: message,
                    user_id: this.config.userName
                })
            });

            const data = await response.json();
            
            // Hide loading indicator
            this.hideLoadingIndicator();

            // Add AI response
            if (data.response) {
                this.appendMessage({
                    text: data.response,
                    sender: 'ai',
                    timestamp: new Date()
                });
            }

        } catch (error) {
            console.error('Error sending message:', error);
            this.hideLoadingIndicator();
            this.appendMessage({
                text: 'Sorry, I encountered an error. Please try again.',
                sender: 'ai',
                timestamp: new Date(),
                isError: true
            });
        }
    }

    appendMessage(data) {
        if (!this.dom.chat.streamContainer) return;

        const { text, sender, timestamp, isError } = data;
        const messageContainer = document.createElement('div');
        messageContainer.classList.add('flex', 'items-start', 'animate-fade-in-up');

        const messageBubble = document.createElement('div');
        messageBubble.classList.add('p-3', 'rounded-lg', 'max-w-md', 'shadow-sm');

        const paragraph = document.createElement('p');
        paragraph.classList.add('text-sm');
        paragraph.textContent = text;

        const timestampEl = document.createElement('span');
        timestampEl.classList.add('text-xs', 'mt-1', 'block', 'text-right');
        timestampEl.textContent = timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

        if (sender === 'user') {
            messageContainer.classList.add('justify-end');
            messageBubble.classList.add('bg-brand', 'text-white');
            timestampEl.classList.add('text-blue-100/70');
        } else {
            messageContainer.classList.add('justify-start');
            messageBubble.classList.add('bg-white', 'dark:bg-gray-700');
            timestampEl.classList.add('text-gray-500', 'dark:text-gray-400');

            if (isError) {
                messageBubble.classList.add('border-l-4', 'border-red-500');
            }

            // AI avatar
            const avatar = document.createElement('div');
            avatar.classList.add('w-8', 'h-8', 'rounded-full', 'mr-3', 'bg-brand', 'flex', 'items-center', 'justify-center', 'text-white', 'text-sm', 'font-semibold');
            avatar.textContent = '🧠';
            messageContainer.appendChild(avatar);
        }

        messageBubble.appendChild(paragraph);
        messageBubble.appendChild(timestampEl);
        messageContainer.appendChild(messageBubble);

        this.dom.chat.streamContainer.appendChild(messageContainer);
        this.dom.chat.stream.scrollTop = this.dom.chat.stream.scrollHeight;
    }

    showLoadingIndicator() {
        // Create loading message
        const loadingContainer = document.createElement('div');
        loadingContainer.classList.add('flex', 'items-start', 'justify-start');
        loadingContainer.id = 'loading-message';

        const avatar = document.createElement('div');
        avatar.classList.add('w-8', 'h-8', 'rounded-full', 'mr-3', 'bg-brand', 'flex', 'items-center', 'justify-center', 'text-white', 'text-sm');
        avatar.textContent = '🧠';

        const loadingBubble = document.createElement('div');
        loadingBubble.classList.add('p-3', 'rounded-lg', 'bg-white', 'dark:bg-gray-700', 'shadow-sm');

        const loadingText = document.createElement('div');
        loadingText.classList.add('flex', 'items-center', 'space-x-1');
        loadingText.innerHTML = `
            <span class="text-sm text-gray-600 dark:text-gray-300">NOUS is thinking</span>
            <div class="flex space-x-1">
                <div class="w-1 h-1 bg-gray-400 rounded-full animate-bounce"></div>
                <div class="w-1 h-1 bg-gray-400 rounded-full animate-bounce" style="animation-delay: 0.1s"></div>
                <div class="w-1 h-1 bg-gray-400 rounded-full animate-bounce" style="animation-delay: 0.2s"></div>
            </div>
        `;

        loadingBubble.appendChild(loadingText);
        loadingContainer.appendChild(avatar);
        loadingContainer.appendChild(loadingBubble);

        this.dom.chat.streamContainer.appendChild(loadingContainer);
        this.dom.chat.stream.scrollTop = this.dom.chat.stream.scrollHeight;
    }

    hideLoadingIndicator() {
        const loadingMessage = document.getElementById('loading-message');
        if (loadingMessage) {
            loadingMessage.remove();
        }
    }

    // --- SEARCH FUNCTIONALITY ---
    initSearch() {
        if (!this.dom.search.input) return;

        let searchTimeout;
        this.dom.search.input.addEventListener('input', (e) => {
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(() => {
                this.performSearch(e.target.value);
            }, 300);
        });

        if (this.dom.search.btn) {
            this.dom.search.btn.addEventListener('click', () => {
                this.performSearch(this.dom.search.input.value);
            });
        }

        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            if ((e.ctrlKey || e.metaKey) && e.key === '/') {
                e.preventDefault();
                this.dom.search.input.focus();
            }
        });
    }

    async performSearch(query) {
        if (!query.trim()) {
            if (this.dom.search.results) {
                this.dom.search.results.style.display = 'none';
            }
            return;
        }

        try {
            const response = await fetch(`/api/search?q=${encodeURIComponent(query)}`);
            const data = await response.json();
            this.displaySearchResults(data.results || []);
        } catch (error) {
            console.error('Search error:', error);
        }
    }

    displaySearchResults(results) {
        if (!this.dom.search.results) return;

        if (results.length === 0) {
            this.dom.search.results.innerHTML = '<div class="p-3 text-gray-500">No results found</div>';
        } else {
            this.dom.search.results.innerHTML = results.map(result => `
                <div class="p-3 hover:bg-gray-100 dark:hover:bg-gray-700 cursor-pointer border-b border-gray-200 dark:border-gray-600">
                    <div class="font-medium text-sm">${result.title}</div>
                    <div class="text-xs text-gray-500 mt-1">${result.description}</div>
                </div>
            `).join('');
        }

        this.dom.search.results.style.display = 'block';
    }

    // --- NOTIFICATIONS ---
    initNotifications() {
        if (!this.dom.notifications.btn) return;

        this.dom.notifications.btn.addEventListener('click', () => {
            this.toggleNotifications();
        });

        if (this.dom.notifications.markAllRead) {
            this.dom.notifications.markAllRead.addEventListener('click', () => {
                this.markAllNotificationsRead();
            });
        }

        // Load initial notifications
        this.loadNotifications();
    }

    toggleNotifications() {
        if (!this.dom.notifications.dropdown) return;

        const isVisible = this.dom.notifications.dropdown.style.display !== 'none';
        this.dom.notifications.dropdown.style.display = isVisible ? 'none' : 'block';
    }

    async loadNotifications() {
        try {
            const response = await fetch('/api/notifications');
            const data = await response.json();
            this.displayNotifications(data.notifications || []);
        } catch (error) {
            console.error('Error loading notifications:', error);
        }
    }

    displayNotifications(notifications) {
        if (!this.dom.notifications.list) return;

        const unreadCount = notifications.filter(n => !n.read).length;
        
        if (this.dom.notifications.badge) {
            if (unreadCount > 0) {
                this.dom.notifications.badge.textContent = unreadCount;
                this.dom.notifications.badge.style.display = 'block';
            } else {
                this.dom.notifications.badge.style.display = 'none';
            }
        }

        if (notifications.length === 0) {
            this.dom.notifications.list.innerHTML = '<div class="p-3 text-gray-500 text-center">No notifications</div>';
        } else {
            this.dom.notifications.list.innerHTML = notifications.map(notification => `
                <div class="p-3 border-b border-gray-200 dark:border-gray-600 ${!notification.read ? 'bg-blue-50 dark:bg-blue-900/20' : ''}">
                    <div class="font-medium text-sm">${notification.title}</div>
                    <div class="text-xs text-gray-500 mt-1">${notification.message}</div>
                    <div class="text-xs text-gray-400 mt-1">${new Date(notification.timestamp).toLocaleString()}</div>
                </div>
            `).join('');
        }
    }

    async markAllNotificationsRead() {
        try {
            await fetch('/api/notifications/mark-read', { method: 'POST' });
            this.loadNotifications();
        } catch (error) {
            console.error('Error marking notifications as read:', error);
        }
    }

    // --- QUICK ACTIONS ---
    initQuickActions() {
        if (!this.dom.fab.main) return;

        this.dom.fab.main.addEventListener('click', () => {
            this.toggleQuickActions();
        });

        if (this.dom.fab.actions) {
            this.dom.fab.actions.forEach(action => {
                action.addEventListener('click', (e) => {
                    const actionType = e.currentTarget.dataset.action;
                    this.handleQuickAction(actionType);
                });
            });
        }
    }

    toggleQuickActions() {
        if (!this.dom.fab.menu) return;

        const isVisible = this.dom.fab.menu.style.display !== 'none';
        this.dom.fab.menu.style.display = isVisible ? 'none' : 'block';
    }

    handleQuickAction(actionType) {
        switch (actionType) {
            case 'new-task':
                this.sendMessage('Create a new task for me');
                break;
            case 'voice-note':
                alert('Voice recording feature coming soon!');
                break;
            case 'quick-mood':
                this.sendMessage('Help me log my current mood');
                break;
            case 'new-goal':
                this.sendMessage('I want to set a new goal');
                break;
            case 'analytics':
                window.location.href = '/api/v1/analytics/dashboard-view';
                break;
            default:
                console.log('Unknown action:', actionType);
        }
        this.toggleQuickActions();
    }

    // --- ENHANCED FEATURES ---
    initEnhancedFeatures() {
        // Initialize any additional NOUS-specific features
        this.initKeyboardShortcuts();
        this.initAccessibility();
    }

    initKeyboardShortcuts() {
        document.addEventListener('keydown', (e) => {
            if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
                e.preventDefault();
                this.toggleQuickActions();
            }
            if ((e.ctrlKey || e.metaKey) && e.key === 'n') {
                e.preventDefault();
                this.handleQuickAction('new-task');
            }
        });
    }

    initAccessibility() {
        // Add ARIA labels and keyboard navigation
        document.querySelectorAll('button, [role="button"]').forEach(button => {
            if (!button.getAttribute('aria-label') && !button.textContent.trim()) {
                button.setAttribute('aria-label', 'Interactive button');
            }
        });
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.nousModernChat = new NOUSModernChat(window.chatConfig || {});
    window.nousModernChat.init();
});