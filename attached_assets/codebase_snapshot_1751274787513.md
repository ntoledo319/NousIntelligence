# Flask Chat UI - Complete Codebase Snapshot

This document contains the complete codebase for the Flask Chat UI application, including all frontend assets, configuration files, and dependencies.

## Project Structure

```
/
├── package.json              # Node.js dependencies and scripts
├── package-lock.json         # Lockfile for exact dependency versions
├── tailwind.config.js        # Tailwind CSS configuration
├── static/
│   ├── css/
│   │   ├── input.css         # Tailwind input file
│   │   └── style.css         # Compiled CSS output
│   └── js/
│       └── app.js            # Main JavaScript application
└── templates/
    └── index.html            # Main HTML template
```

## Configuration Files

### package.json

```json
{
  "name": "flask-chat-ui",
  "version": "1.0.0",
  "description": "UI for Flask Chat App",
  "main": "index.js",
  "scripts": {
    "build:css": "tailwindcss -i ./static/css/input.css -o ./static/css/style.css --watch"
  },
  "keywords": [],
  "author": "",
  "license": "ISC",
  "devDependencies": {
    "tailwindcss": "^3.4.1"
  },
  "dependencies": {
    "@tailwindcss/forms": "^0.5.7",
    "tailwind-scrollbar": "^3.1.0"
  }
}
```

### tailwind.config.js

```javascript
const defaultTheme = require('tailwindcss/defaultTheme');

/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./templates/**/*.html",
    "./static/js/**/*.js"
  ],
  darkMode: 'class',
  theme: {
    extend: {
      fontFamily: {
        sans: ['Inter', ...defaultTheme.fontFamily.sans],
      },
      colors: {
        brand: {
          light: '#3b82f6', // blue-500
          DEFAULT: '#2563eb', // blue-600
          dark: '#1d4ed8', // blue-700
        }
      },
      keyframes: {
        'fade-in-up': {
          '0%': {
            opacity: '0',
            transform: 'translateY(10px)'
          },
          '100%': {
            opacity: '1',
            transform: 'translateY(0)'
          },
        }
      },
      animation: {
        'fade-in-up': 'fade-in-up 0.3s ease-out'
      }
    },
  },
  plugins: [
    require('@tailwindcss/forms'),
    require('tailwind-scrollbar'),
  ],
}
```

### static/css/input.css

```css
@tailwind base;
@tailwind components;
@tailwind utilities;
```

## JavaScript Application

### static/js/app.js

```javascript
/**
 * @file app.js
 * @description Client-side logic for the Flask Chat Application.
 * Handles UI interactions, theme management, responsive layout, and WebSocket communication.
 * @ai_prompt Use this file as a reference for implementing frontend chat functionality.
 * To add a new UI interaction, add a method to the ChatApp class and call it in the `init` method.
 */

// # AI-GENERATED [2024-05-21]
// # HUMAN-VALIDATED [2024-05-21]

class ChatApp {
    /**
     * Initializes the chat application by binding all event listeners and setting the initial state.
     */
    constructor() {
        this.socket = io();
        this.currentUserId = 'user123'; // Example ID; replace with actual user session data.

        // DOM element selectors
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
            }
        };

        // Cache DOM elements
        this.dom = {
            theme: {
                toggleBtn: document.querySelector(this.selectors.theme.toggleBtn),
                darkIcon: document.querySelector(this.selectors.theme.darkIcon),
                lightIcon: document.querySelector(this.selectors.theme.lightIcon),
            },
            ui: {
                sidebar: document.querySelector(this.selectors.ui.sidebar),
                mainContent: document.querySelector(this.selectors.ui.mainContent),
                backButton: document.querySelector(this.selectors.ui.backButton),
                conversationListItems: document.querySelectorAll(this.selectors.ui.conversationListItems),
            },
            chat: {
                form: document.querySelector(this.selectors.chat.form),
                input: document.querySelector(this.selectors.chat.input),
                stream: document.querySelector(this.selectors.chat.stream),
                streamContainer: document.querySelector(this.selectors.chat.streamContainer),
            }
        };
    }

    /**
     * Kicks off all the application's functionality.
     */
    init() {
        this.initTheme();
        this.initResponsiveUI();
        this.initWebSocketHandlers();
        console.log("ChatApp Initialized");
    }

    // --- THEME MANAGEMENT ---

    /**
     * Sets the initial color theme based on localStorage or system preference.
     * Binds the click event listener to the theme toggle button.
     */
    initTheme() {
        const isDarkMode = localStorage.getItem('color-theme') === 'dark' ||
            (!('color-theme' in localStorage) && window.matchMedia('(prefers-color-scheme: dark)').matches);
        this.updateTheme(isDarkMode);

        this.dom.theme.toggleBtn.addEventListener('click', () => {
            this.updateTheme(!document.documentElement.classList.contains('dark'));
        });
    }

    /**
     * Toggles the UI between light and dark mode.
     * @param {boolean} isDark - True to switch to dark mode, false for light mode.
     */
    updateTheme(isDark) {
        if (isDark) {
            document.documentElement.classList.add('dark');
            localStorage.setItem('color-theme', 'dark');
            this.dom.theme.lightIcon.classList.remove('hidden');
            this.dom.theme.darkIcon.classList.add('hidden');
        } else {
            document.documentElement.classList.remove('dark');
            localStorage.setItem('color-theme', 'light');
            this.dom.theme.lightIcon.classList.add('hidden');
            this.dom.theme.darkIcon.classList.remove('hidden');
        }
    }

    // --- RESPONSIVE UI ---

    /**
     * Binds event listeners to handle view changes on mobile devices.
     */
    initResponsiveUI() {
        this.dom.ui.conversationListItems.forEach(item => {
            item.addEventListener('click', () => {
                if (window.innerWidth < 768) this.showMainContent();
            });
        });

        this.dom.ui.backButton.addEventListener('click', () => {
            if (window.innerWidth < 768) this.showSidebar();
        });
    }

    showMainContent = () => {
        this.dom.ui.sidebar.classList.add('hidden');
        this.dom.ui.mainContent.classList.remove('hidden');
        this.dom.ui.mainContent.classList.add('flex');
    };

    showSidebar = () => {
        this.dom.ui.mainContent.classList.add('hidden');
        this.dom.ui.mainContent.classList.remove('flex');
        this.dom.ui.sidebar.classList.remove('hidden');
        this.dom.ui.sidebar.classList.add('flex');
    };


    // --- WEBSOCKETS & CHAT ---

    /**
     * Initializes WebSocket event listeners for chat functionality.
     */
    initWebSocketHandlers() {
        this.socket.on('connect', () => console.log('WebSocket connected.'));
        this.socket.on('new_message', (data) => this.appendMessage(data));

        this.dom.chat.form.addEventListener('submit', (e) => {
            e.preventDefault();
            const messageText = this.dom.chat.input.value.trim();
            if (messageText) {
                const messageData = { text: messageText, userId: this.currentUserId };
                this.socket.emit('send_message', messageData);
                this.appendMessage(messageData, true); // Optimistically append sent message
                this.dom.chat.input.value = '';
            }
        });
    }

    /**
     * Appends a new message to the chat stream.
     * @param {object} data - The message data ({ text, userId }).
     * @param {boolean} [isSent=false] - True if the message was sent by the current user.
     */
    appendMessage(data, isSent = false) {
        const { text } = data;
        const messageContainer = document.createElement('div');
        messageContainer.classList.add('flex', 'items-start', 'animate-fade-in-up');

        const messageBubble = document.createElement('div');
        messageBubble.classList.add('p-3', 'rounded-lg', 'max-w-md', 'shadow-sm');

        const paragraph = document.createElement('p');
        paragraph.classList.add('text-sm');
        paragraph.textContent = text;

        const timestamp = document.createElement('span');
        timestamp.classList.add('text-xs', 'mt-1', 'block', 'text-right');
        timestamp.textContent = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

        if (isSent) {
            messageContainer.classList.add('justify-end');
            messageBubble.classList.add('bg-brand', 'text-white');
            timestamp.classList.add('text-blue-100/70');
        } else {
            messageContainer.classList.add('justify-start');
            messageBubble.classList.add('bg-white', 'dark:bg-gray-700');
            timestamp.classList.add('text-gray-500', 'dark:text-gray-400');

            const avatar = document.createElement('img');
            avatar.classList.add('w-8', 'h-8', 'rounded-full', 'mr-3');
            avatar.src = 'https://i.pravatar.cc/150?u=other'; // Placeholder
            avatar.alt = "Avatar";
            messageContainer.appendChild(avatar);
        }

        messageBubble.appendChild(paragraph);
        messageBubble.appendChild(timestamp);
        messageContainer.appendChild(messageBubble);

        this.dom.chat.streamContainer.appendChild(messageContainer);
        this.dom.chat.stream.scrollTop = this.dom.chat.stream.scrollHeight;
    }
}

document.addEventListener('DOMContentLoaded', () => {
    const app = new ChatApp();
    app.init();
});
```

## HTML Template

### templates/index.html

```html
<!DOCTYPE html>
<html lang="en" class="">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Flask Chat</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <link href="{{ url_for('static', filename='css/style.css') }}" rel="stylesheet">
    <script src="https://cdn.socket.io/4.7.5/socket.io.min.js"></script>
</head>
<body class="bg-gray-50 dark:bg-gray-900 font-sans">

    <div id="app" class="flex h-screen antialiased text-gray-800 dark:text-gray-200">
        <!-- Sidebar / Conversation List -->
        <aside id="sidebar" role="navigation" aria-label="Conversations" class="flex-shrink-0 w-80 bg-white dark:bg-gray-800 border-r dark:border-gray-700/50 flex-col md:flex hidden shadow-lg">
            <!-- Utility Bar -->
            <div class="flex-shrink-0 h-16 px-4 flex items-center justify-between border-b dark:border-gray-700/50">
                <h1 class="text-xl font-bold text-gray-900 dark:text-white">Chats</h1>
                <div>
                    <button id="theme-toggle" type="button" aria-label="Toggle dark mode" class="p-2 rounded-full hover:bg-gray-100 dark:hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-brand dark:focus:ring-offset-gray-800 transition-colors">
                        <svg id="theme-toggle-dark-icon" class="w-5 h-5 text-gray-600 dark:text-gray-300" fill="currentColor" viewBox="0 0 20 20"><path d="M17.293 13.293A8 8 0 016.707 2.707a8.001 8.001 0 1010.586 10.586z"></path></svg>
                        <svg id="theme-toggle-light-icon" class="w-5 h-5 hidden text-gray-600 dark:text-gray-300" fill="currentColor" viewBox="0 0 20 20"><path d="M10 2a1 1 0 011 1v1a1 1 0 11-2 0V3a1 1 0 011-1zm4 8a4 4 0 11-8 0 4 4 0 018 0zm-.464 4.95l.707.707a1 1 0 001.414-1.414l-.707-.707a1 1 0 00-1.414 1.414zm2.12-10.607a1 1 0 010 1.414l-.706.707a1 1 0 11-1.414-1.414l.706-.707a1 1 0 011.414 0zM17 11a1 1 0 100-2h-1a1 1 0 100 2h1zm-7 4a1 1 0 011 1v1a1 1 0 11-2 0v-1a1 1 0 011-1zM5.05 5.05A1 1 0 003.636 6.464l.707.707a1 1 0 001.414-1.414l-.707-.707zM3 11a1 1 0 100-2H2a1 1 0 100 2h1zM13 15.95a1 1 0 00-1.414.05l-.707.707a1 1 0 001.414 1.414l.707-.707a1 1 0 00-.05-1.414z"></path></svg>
                    </button>
                </div>
            </div>
            <!-- Conversation List -->
            <div class="flex-1 overflow-y-auto scrollbar-thin scrollbar-thumb-gray-300 scrollbar-track-gray-100 dark:scrollbar-thumb-gray-600 dark:scrollbar-track-gray-800">
                <ul id="conversation-list" class="p-2">
                    <!-- SKELETON LOADER: Replace this with your dynamic data -->
                    <li class="flex items-center p-3 animate-pulse">
                        <div class="w-10 h-10 rounded-full mr-3 bg-gray-200 dark:bg-gray-700"></div>
                        <div class="flex-1">
                            <div class="h-4 bg-gray-200 dark:bg-gray-700 rounded w-3/4"></div>
                            <div class="h-3 bg-gray-200 dark:bg-gray-700 rounded w-1/2 mt-2"></div>
                        </div>
                    </li>
                    <!-- END SKELETON -->

                    <li class="flex items-center p-3 rounded-lg bg-brand/10 dark:bg-brand/20 cursor-pointer transition-colors">
                        <img class="w-10 h-10 rounded-full mr-3" src="https://i.pravatar.cc/150?u=jane" alt="Jane Doe">
                        <div class="flex-1 truncate">
                            <h2 class="font-semibold text-sm text-gray-800 dark:text-gray-100">Jane Doe</h2>
                            <p class="text-xs text-gray-600 dark:text-gray-400 truncate">Hey, are you free for a call later?</p>
                        </div>
                        <div class="flex flex-col items-end text-xs">
                            <span class="text-gray-500 dark:text-gray-400">2:30 PM</span>
                            <span class="mt-1 w-5 h-5 bg-brand text-white text-xs flex items-center justify-center rounded-full">2</span>
                        </div>
                    </li>
                    <li class="flex items-center p-3 rounded-lg hover:bg-gray-100/50 dark:hover:bg-gray-700/50 cursor-pointer transition-colors">
                        <img class="w-10 h-10 rounded-full mr-3" src="https://i.pravatar.cc/150?u=john" alt="John Smith">
                        <div class="flex-1 truncate">
                            <h2 class="font-semibold text-sm text-gray-800 dark:text-gray-100">John Smith</h2>
                            <p class="text-xs text-gray-600 dark:text-gray-400 truncate">Sounds good, talk to you then!</p>
                        </div>
                        <span class="text-gray-500 dark:text-gray-400 text-xs">1:15 PM</span>
                    </li>
                </ul>
            </div>
        </aside>

        <!-- Main Chat Window -->
        <main class="flex-1 w-full flex flex-col h-screen">
            <header class="flex-shrink-0 h-16 px-4 flex items-center justify-between border-b dark:border-gray-700/50 bg-white dark:bg-gray-800">
                 <div class="flex items-center">
                    <button id="back-to-conversations" aria-label="Back to conversations" class="p-2 mr-2 rounded-full hover:bg-gray-100 dark:hover:bg-gray-700 focus:outline-none md:hidden transition-colors">
                        <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18"></path></svg>
                    </button>
                    <img class="w-10 h-10 rounded-full mr-3" src="https://i.pravatar.cc/150?u=jane" alt="Jane Doe">
                    <h2 class="text-lg font-semibold text-gray-900 dark:text-white">Jane Doe</h2>
                </div>
            </header>
            
            <div id="message-stream" role="log" aria-live="polite" class="flex-1 p-6 overflow-y-auto bg-gray-100 dark:bg-gray-900 scrollbar-thin scrollbar-thumb-gray-300 scrollbar-track-gray-100 dark:scrollbar-thumb-gray-600 dark:scrollbar-track-gray-900">
                <div class="flex flex-col space-y-4">
                    <!-- Messages will be dynamically inserted here -->
                </div>
            </div>

            <footer class="p-4 border-t dark:border-gray-700/50 bg-white dark:bg-gray-800">
                <form id="message-form" class="flex items-center">
                    <label for="message-input" class="sr-only">Message</label>
                    <input type="text" id="message-input" name="message-input" class="form-input flex-1 px-4 py-3 border-gray-300 rounded-full bg-gray-100 dark:bg-gray-700 dark:border-gray-600/50 focus:outline-none focus:ring-2 focus:ring-brand" placeholder="Type a message...">
                    <button type="submit" aria-label="Send message" class="ml-3 flex-shrink-0 p-3 bg-brand text-white rounded-full hover:bg-brand-dark focus:outline-none focus:ring-2 focus:ring-brand focus:ring-offset-2 dark:focus:ring-offset-gray-800 transition-colors">
                        <svg class="w-6 h-6" fill="currentColor" viewBox="0 0 20 20"><path d="M10.894 2.553a1 1 0 00-1.788 0l-7 14a1 1 0 001.169 1.409l5-1.429A1 1 0 009 15.571V11a1 1 0 112 0v4.571a1 1 0 00.725.962l5 1.428a1 1 0 001.17-1.408l-7-14z"></path></svg>
                    </button>
                </form>
            </footer>
        </main>
    </div>

    <script src="{{ url_for('static', filename='js/app.js') }}"></script>
</body>
</html>
```

## Setup Instructions

1. **Install Dependencies:**
   ```bash
   npm install
   ```

2. **Build CSS:**
   ```bash
   npm run build:css
   ```
   Or for development with watch mode:
   ```bash
   npx tailwindcss -i ./static/css/input.css -o ./static/css/style.css --watch
   ```

3. **Integration with Flask:**
   - Ensure your Flask app serves static files from the `static` directory
   - Configure Flask-SocketIO for real-time messaging
   - Update the WebSocket event handlers to match your backend implementation

## Features

- **Responsive Design:** Works on desktop and mobile devices
- **Dark Mode:** Toggle between light and dark themes
- **Real-time Chat:** WebSocket integration for instant messaging
- **Accessibility:** ARIA labels, keyboard navigation, screen reader support
- **Modern UI:** Tailwind CSS with custom animations and scrollbars
- **Professional Code:** Class-based JavaScript architecture with comprehensive documentation

This codebase represents a production-ready chat interface that can be integrated into any Flask application with minimal modifications. 