/**
 * OAuth Handler - Manages OAuth flow UX
 */

// Configuration
const OAUTH_CONFIG = {
    timeouts: {
        redirectTimeout: 60000, // 1 minute
        notificationTimeout: 10000 // 10 seconds
    },
    retryAttempts: 3
};

document.addEventListener('DOMContentLoaded', function() {
    const googleSignInBtn = document.getElementById('google-signin-btn');
    
    if (googleSignInBtn) {
        googleSignInBtn.addEventListener('click', function(e) {
            // Don't prevent default - let the link work
            // Just add loading state
            const btnText = this.querySelector('.btn-text');
            const btnLoading = this.querySelector('.btn-loading');
            
            if (btnText && btnLoading) {
                btnText.style.display = 'none';
                btnLoading.style.display = 'inline-flex';
                
                // Disable button to prevent double-clicks
                this.style.pointerEvents = 'none';
                this.style.opacity = '0.7';
                
                // Store state in sessionStorage for recovery
                sessionStorage.setItem('oauth_redirect_initiated', Date.now());
            }
        });
    }
    
    // Check if we're returning from OAuth redirect
    const urlParams = new URLSearchParams(window.location.search);
    if (urlParams.has('oauth_error') || urlParams.has('error')) {
        // Clear loading state
        sessionStorage.removeItem('oauth_redirect_initiated');
        
        // Show user-friendly error
        const errorCode = urlParams.get('error') || 'unknown_error';
        showOAuthError(errorCode);
    }
    
    // Clear stale loading states
    const redirectTime = sessionStorage.getItem('oauth_redirect_initiated');
    if (redirectTime && (Date.now() - parseInt(redirectTime)) > OAUTH_CONFIG.timeouts.redirectTimeout) {
        sessionStorage.removeItem('oauth_redirect_initiated');
    }
});

function showOAuthError(errorCode) {
    const errorMessages = {
        'access_denied': 'You cancelled the sign-in process. Please try again when you\'re ready.',
        'temporarily_unavailable': 'Google Sign-in is temporarily unavailable. Please try again later.',
        'server_error': 'We encountered an error connecting to Google. Please try again.',
        'unknown_error': 'An unexpected error occurred. Please try again or use Demo mode.'
    };
    
    const message = errorMessages[errorCode] || errorMessages['unknown_error'];
    
    // Create error notification
    const notification = document.createElement('div');
    notification.className = 'oauth-error-notification';
    notification.innerHTML = `
        <div style="background: #fef2f2; border: 1px solid #fecaca; border-radius: 0.5rem; padding: 1rem; margin: 1rem;">
            <p style="color: #dc2626; font-weight: 500; margin: 0;">
                ⚠️ ${message}
            </p>
        </div>
    `;
    
    document.body.appendChild(notification);
    
    // Auto-remove after configured timeout
    setTimeout(() => {
        notification.remove();
    }, OAUTH_CONFIG.timeouts.notificationTimeout);
    
    // Add retry functionality for certain errors
    if (['network_error', 'timeout_error', 'server_error'].includes(errorCode)) {
        addRetryButton(notification, errorCode);
    }
}

function addRetryButton(notification, errorCode) {
    const retryButton = document.createElement('button');
    retryButton.textContent = 'Retry';
    retryButton.style.cssText = `
        background: #2563eb;
        color: white;
        border: none;
        padding: 0.5rem 1rem;
        border-radius: 0.25rem;
        margin-top: 0.5rem;
        cursor: pointer;
        font-size: 0.875rem;
    `;
    
    retryButton.addEventListener('click', function() {
        const attempts = parseInt(sessionStorage.getItem('oauth_retry_attempts') || '0');
        if (attempts < OAUTH_CONFIG.retryAttempts) {
            sessionStorage.setItem('oauth_retry_attempts', (attempts + 1).toString());
            window.location.href = '/auth/google';
        } else {
            retryButton.textContent = 'Max retries reached';
            retryButton.disabled = true;
        }
    });
    
    notification.querySelector('div').appendChild(retryButton);
}

// Clear retry attempts on successful page load
if (!window.location.search.includes('oauth_error')) {
    sessionStorage.removeItem('oauth_retry_attempts');
}