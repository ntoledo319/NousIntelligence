// NOUS Personal Assistant - Main JavaScript
// Optimized for fast loading and smooth user experience

document.addEventListener('DOMContentLoaded', () => {
    // Initialize performance metrics
    if (window.performance) {
        const timing = window.performance.timing;
        const pageLoadTime = timing.loadEventEnd - timing.navigationStart;
        console.log(`Page loaded in ${pageLoadTime}ms`);
    }

    // Smooth scrolling for navigation links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();
            const targetId = this.getAttribute('href');
            if (targetId === '#') return;
            
            const targetElement = document.querySelector(targetId);
            if (targetElement) {
                targetElement.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });

    // Function to check system status
    const checkSystemStatus = async () => {
        try {
            const response = await fetch('/health');
            const data = await response.json();
            
            const statusIndicator = document.querySelector('.status-indicator');
            const statusText = document.querySelector('.status-container p');
            
            if (statusIndicator && statusText) {
                if (data.status === 'healthy') {
                    statusIndicator.style.backgroundColor = '#2ecc71'; // Green
                    statusText.innerHTML = '<span class="status-indicator"></span> All systems operational';
                } else if (data.status === 'degraded') {
                    statusIndicator.style.backgroundColor = '#f39c12'; // Yellow/orange
                    statusText.innerHTML = '<span class="status-indicator"></span> Some services degraded';
                } else {
                    statusIndicator.style.backgroundColor = '#e74c3c'; // Red
                    statusText.innerHTML = '<span class="status-indicator"></span> System issues detected';
                }
            }
        } catch (error) {
            console.error('Error checking system status:', error);
        }
    };

    // Check system status on page load
    checkSystemStatus();

    // Add animation to feature cards
    const animateOnScroll = () => {
        const features = document.querySelectorAll('.feature');
        features.forEach(feature => {
            const featurePosition = feature.getBoundingClientRect().top;
            const screenPosition = window.innerHeight / 1.3;
            
            if (featurePosition < screenPosition) {
                feature.style.opacity = 1;
                feature.style.transform = 'translateY(0)';
            }
        });
    };

    // Initialize feature animations
    const features = document.querySelectorAll('.feature');
    features.forEach(feature => {
        feature.style.opacity = 0;
        feature.style.transform = 'translateY(20px)';
        feature.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
    });

    // Listen for scroll events
    window.addEventListener('scroll', animateOnScroll);
    
    // Run animation on initial load
    animateOnScroll();
});