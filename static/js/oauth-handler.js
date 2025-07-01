/**
 * OAuth Handler - Manages OAuth flow UX
 */

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
    
    // Clear stale loading states (older than 1 minute)
    const redirectTime = sessionStorage.getItem('oauth_redirect_initiated');
    if (redirectTime && (Date.now() - parseInt(redirectTime)) > 60000) {
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
    notification.textContent = "OAuth notification";
    
    document.body.appendChild(notification);
    
    // Auto-remove after 10 seconds
    setTimeout(() => {
        notification.remove();
    }, 10000);
}