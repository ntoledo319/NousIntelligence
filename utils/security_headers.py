"""
Security Headers Module

This module provides middleware for adding security headers to HTTP responses
to protect against various web vulnerabilities like XSS, clickjacking, etc.

@module: security_headers
@author: NOUS Development Team
"""
import os
from flask import Flask, request, current_app
from typing import Dict, Any, Optional, Callable, List

# Default security headers
DEFAULT_SECURITY_HEADERS = {
    'Content-Security-Policy': "default-src 'self'; script-src 'self' https://unpkg.com; style-src 'self' https://unpkg.com; img-src 'self' data:; font-src 'self'; frame-ancestors 'none'; form-action 'self';",
    'X-Content-Type-Options': 'nosniff',
    'X-Frame-Options': 'DENY',
    'X-XSS-Protection': '1; mode=block',
    'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
    'Referrer-Policy': 'strict-origin-when-cross-origin',
    'Permissions-Policy': 'camera=(), microphone=(), geolocation=(self), interest-cohort=()'
}

# Environment flag to disable HSTS locally
ENABLE_HSTS = os.environ.get('ENABLE_HSTS', 'true').lower() == 'true'

def init_security_headers(app: Flask, custom_headers: Optional[Dict[str, str]] = None) -> None:
    """
    Initialize security headers middleware for a Flask application
    
    Args:
        app: Flask application instance
        custom_headers: Optional dictionary of custom headers to use instead of defaults
    """
    headers = DEFAULT_SECURITY_HEADERS.copy()
    
    # Apply custom headers if provided
    if custom_headers:
        headers.update(custom_headers)
    
    # Disable HSTS in development if configured
    if not ENABLE_HSTS and 'Strict-Transport-Security' in headers:
        del headers['Strict-Transport-Security']
    
    @app.after_request
    def add_security_headers(response):
        """Add security headers to all responses"""
        # Skip for static files
        if request.path.startswith('/static/'):
            return response
        
        # Add headers
        for header, value in headers.items():
            if header not in response.headers:
                response.headers[header] = value
        
        return response

def get_csp_header(
    default_src: List[str] = ["'self'"],
    script_src: Optional[List[str]] = None,
    style_src: Optional[List[str]] = None,
    img_src: Optional[List[str]] = None,
    font_src: Optional[List[str]] = None,
    connect_src: Optional[List[str]] = None,
    frame_src: Optional[List[str]] = None,
    frame_ancestors: Optional[List[str]] = None,
    form_action: Optional[List[str]] = None,
    report_uri: Optional[str] = None
) -> str:
    """
    Generate a Content Security Policy header value
    
    Args:
        default_src: Default source list (applies to all unspecified directives)
        script_src: Allowed sources for JavaScript
        style_src: Allowed sources for CSS
        img_src: Allowed sources for images
        font_src: Allowed sources for fonts
        connect_src: Allowed sources for fetch, XHR, WebSocket
        frame_src: Allowed sources for frames
        frame_ancestors: Allowed embedders of the page
        form_action: Allowed targets for form submissions
        report_uri: URI to report CSP violations to
        
    Returns:
        CSP header value string
    """
    # Start with default-src
    csp_parts = [f"default-src {' '.join(default_src)}"]
    
    # Add directives if specified
    if script_src:
        csp_parts.append(f"script-src {' '.join(script_src)}")
    
    if style_src:
        csp_parts.append(f"style-src {' '.join(style_src)}")
    
    if img_src:
        csp_parts.append(f"img-src {' '.join(img_src)}")
    
    if font_src:
        csp_parts.append(f"font-src {' '.join(font_src)}")
    
    if connect_src:
        csp_parts.append(f"connect-src {' '.join(connect_src)}")
    
    if frame_src:
        csp_parts.append(f"frame-src {' '.join(frame_src)}")
    
    if frame_ancestors:
        csp_parts.append(f"frame-ancestors {' '.join(frame_ancestors)}")
    else:
        csp_parts.append("frame-ancestors 'none'")  # Default to none for security
    
    if form_action:
        csp_parts.append(f"form-action {' '.join(form_action)}")
    else:
        csp_parts.append("form-action 'self'")  # Default to self for security
    
    if report_uri:
        csp_parts.append(f"report-uri {report_uri}")
    
    return "; ".join(csp_parts)

def get_hsts_header(max_age_seconds: int = 31536000, include_subdomains: bool = True, preload: bool = False) -> str:
    """
    Generate a Strict-Transport-Security header value
    
    Args:
        max_age_seconds: Time in seconds browsers should remember to use HTTPS
        include_subdomains: Whether to apply to all subdomains
        preload: Whether to include in browser preload list
        
    Returns:
        HSTS header value string
    """
    hsts_parts = [f"max-age={max_age_seconds}"]
    
    if include_subdomains:
        hsts_parts.append("includeSubDomains")
    
    if preload:
        hsts_parts.append("preload")
    
    return "; ".join(hsts_parts)

def get_permissions_policy_header(
    camera: bool = False,
    microphone: bool = False,
    geolocation: bool = False,
    payment: bool = False,
    autoplay: bool = False
) -> str:
    """
    Generate a Permissions-Policy header value
    
    Args:
        camera: Whether to allow camera access
        microphone: Whether to allow microphone access
        geolocation: Whether to allow geolocation access
        payment: Whether to allow payment API access
        autoplay: Whether to allow autoplay
        
    Returns:
        Permissions-Policy header value string
    """
    permissions = {
        "camera": "()" if not camera else "(self)",
        "microphone": "()" if not microphone else "(self)",
        "geolocation": "()" if not geolocation else "(self)",
        "payment": "()" if not payment else "(self)",
        "autoplay": "()" if not autoplay else "(self)",
        "interest-cohort": "()"  # Always disable FLoC
    }
    
    return ", ".join(f"{permission}={value}" for permission, value in permissions.items()) 