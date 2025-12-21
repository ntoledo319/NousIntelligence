/**
 * NOUS Service Worker - PWA and Performance
 * Implements caching strategies for optimal performance
 */

const CACHE_NAME = 'nous-v1';
const STATIC_CACHE = 'nous-static-v1';
const API_CACHE = 'nous-api-v1';

// Static assets to precache
const STATIC_ASSETS = ['/', '/static/styles.css', '/static/app.js', '/static/favicon.ico'];

// Install event - precache critical assets
self.addEventListener('install', (event) => {
  console.log('NOUS Service Worker installing...');

  event.waitUntil(
    caches
      .open(STATIC_CACHE)
      .then((cache) => {
        console.log('Precaching static assets...');
        return cache.addAll(STATIC_ASSETS);
      })
      .then(() => self.skipWaiting())
  );
});

// Activate event - cleanup old caches
self.addEventListener('activate', (event) => {
  console.log('NOUS Service Worker activating...');

  event.waitUntil(
    caches
      .keys()
      .then((cacheNames) => {
        return Promise.all(
          cacheNames.map((cacheName) => {
            if (cacheName !== STATIC_CACHE && cacheName !== API_CACHE && cacheName !== CACHE_NAME) {
              console.log('Deleting old cache:', cacheName);
              return caches.delete(cacheName);
            }
          })
        );
      })
      .then(() => self.clients.claim())
  );
});

// Fetch event - handle requests with caching strategies
self.addEventListener('fetch', (event) => {
  const { request } = event;
  const url = new URL(request.url);

  // Handle API requests with network-first strategy
  if (url.pathname.startsWith('/api/')) {
    event.respondWith(networkFirstStrategy(request, API_CACHE));
    return;
  }

  // Handle static assets with cache-first strategy
  if (
    request.destination === 'style' ||
    request.destination === 'script' ||
    request.destination === 'image'
  ) {
    event.respondWith(cacheFirstStrategy(request, STATIC_CACHE));
    return;
  }

  // Handle navigation requests with network-first strategy
  if (request.mode === 'navigate') {
    event.respondWith(networkFirstStrategy(request, CACHE_NAME));
    return;
  }

  // Default: pass through to network
  event.respondWith(fetch(request));
});

// Network-first strategy (good for API and HTML)
async function networkFirstStrategy(request, cacheName) {
  try {
    const networkResponse = await fetch(request);

    // Only cache successful responses
    if (networkResponse.status === 200) {
      const cache = await caches.open(cacheName);
      cache.put(request, networkResponse.clone());
    }

    return networkResponse;
  } catch (error) {
    console.log('Network failed, trying cache:', error);
    const cachedResponse = await caches.match(request);

    if (cachedResponse) {
      return cachedResponse;
    }

    // Return offline page for navigation requests
    if (request.mode === 'navigate') {
      return new Response(
        `<!DOCTYPE html>
                <html>
                <head>
                    <meta charset="UTF-8">
                    <meta name="viewport" content="width=device-width, initial-scale=1.0">
                    <title>NOUS - Offline</title>
                    <style>
                        body { 
                            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                            text-align: center; 
                            padding: 2rem; 
                            background: #f8fafc; 
                        }
                        .offline-container { max-width: 400px; margin: 0 auto; }
                        .offline-title { font-size: 2rem; margin-bottom: 1rem; color: #1e293b; }
                        .offline-message { color: #64748b; margin-bottom: 2rem; }
                        .retry-btn { 
                            background: #2563eb; 
                            color: white; 
                            padding: 0.75rem 1.5rem; 
                            border: none; 
                            border-radius: 0.5rem; 
                            cursor: pointer; 
                            font-size: 1rem;
                        }
                    </style>
                </head>
                <body>
                    <div class="offline-container">
                        <h1 class="offline-title">🧠 NOUS</h1>
                        <p class="offline-message">You're currently offline. Please check your connection and try again.</p>
                        <button class="retry-btn" onclick="window.location.reload()">Retry</button>
                    </div>
                </body>
                </html>`,
        {
          status: 200,
          headers: { 'Content-Type': 'text/html' },
        }
      );
    }

    throw error;
  }
}

// Cache-first strategy (good for static assets)
async function cacheFirstStrategy(request, cacheName) {
  const cachedResponse = await caches.match(request);

  if (cachedResponse) {
    return cachedResponse;
  }

  try {
    const networkResponse = await fetch(request);

    if (networkResponse.status === 200) {
      const cache = await caches.open(cacheName);
      cache.put(request, networkResponse.clone());
    }

    return networkResponse;
  } catch (error) {
    console.log('Failed to fetch resource:', request.url, error);
    throw error;
  }
}

// Background sync for offline actions (future enhancement)
self.addEventListener('sync', (event) => {
  if (event.tag === 'background-sync') {
    event.waitUntil(doBackgroundSync());
  }
});

async function doBackgroundSync() {
  // Implement background sync logic here
  console.log('Background sync triggered');
}

// Push notifications (future enhancement)
self.addEventListener('push', (event) => {
  const options = {
    body: event.data ? event.data.text() : 'New notification from NOUS',
    icon: '/static/favicon.ico',
    badge: '/static/favicon.ico',
    tag: 'nous-notification',
    renotify: true,
  };

  event.waitUntil(self.registration.showNotification('NOUS', options));
});

// Handle notification clicks
self.addEventListener('notificationclick', (event) => {
  event.notification.close();

  event.waitUntil(clients.openWindow('/'));
});
