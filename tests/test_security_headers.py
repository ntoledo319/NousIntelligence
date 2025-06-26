"""
Unit tests for the security headers module

These tests verify the functionality of security headers features including:
- Adding security headers to responses
- CSP header generation
- HSTS header generation
- Permissions Policy header generation

@module: test_security_headers
@author: NOUS Development Team
"""
import unittest
import sys
import os
from unittest.mock import patch, MagicMock
from flask import Flask, jsonify

# Add parent directory to path to import modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.security_headers import (
    init_security_headers,
    DEFAULT_SECURITY_HEADERS,
    get_csp_header,
    get_hsts_header,
    get_permissions_policy_header
)

class TestSecurityHeaders(unittest.TestCase):
    """Test cases for security headers middleware"""

    def setUp(self):
        """Set up test environment"""
        self.app = Flask(__name__)

        # Create test route
        @self.app.route('/test')
        def test_route():
            return jsonify({"success": True})

        # Create static route
        @self.app.route('/static/test.css')
        def static_route():
            return "body { color: black; }", 200, {'Content-Type': 'text/css'}

    def test_default_headers(self):
        """Test that default security headers are added to responses"""
        # Initialize middleware with default headers
        init_security_headers(self.app)

        # Make request to test route
        with self.app.test_client() as client:
            response = client.get('/test')

            # Check all default headers are present
            for header, value in DEFAULT_SECURITY_HEADERS.items():
                self.assertIn(header, response.headers)
                self.assertEqual(response.headers[header], value)

    def test_custom_headers(self):
        """Test that custom headers override defaults"""
        # Custom headers to use
        custom_headers = {
            'Content-Security-Policy': "default-src 'self' https://example.com",
            'X-Custom-Header': 'CustomValue'
        }

        # Initialize middleware with custom headers
        init_security_headers(self.app, custom_headers=custom_headers)

        # Make request to test route
        with self.app.test_client() as client:
            response = client.get('/test')

            # Check custom headers are present
            for header, value in custom_headers.items():
                self.assertIn(header, response.headers)
                self.assertEqual(response.headers[header], value)

            # Check other default headers are still present
            for header, value in DEFAULT_SECURITY_HEADERS.items():
                if header not in custom_headers:
                    self.assertIn(header, response.headers)
                    self.assertEqual(response.headers[header], value)

    def test_static_files_skipped(self):
        """Test that static files are skipped"""
        # Initialize middleware
        init_security_headers(self.app)

        # Make request to static route
        with self.app.test_client() as client:
            response = client.get('/static/test.css')

            # Check security headers are not present
            for header in DEFAULT_SECURITY_HEADERS:
                self.assertNotIn(header, response.headers)

    @patch('utils.security_headers.ENABLE_HSTS', False)
    def test_hsts_disabled(self):
        """Test that HSTS can be disabled in development"""
        # Initialize middleware with HSTS disabled
        init_security_headers(self.app)

        # Make request to test route
        with self.app.test_client() as client:
            response = client.get('/test')

            # Check HSTS header is not present
            self.assertNotIn('Strict-Transport-Security', response.headers)

            # Check other headers are still present
            for header, value in DEFAULT_SECURITY_HEADERS.items():
                if header != 'Strict-Transport-Security':
                    self.assertIn(header, response.headers)
                    self.assertEqual(response.headers[header], value)

class TestCSPHeader(unittest.TestCase):
    """Test cases for CSP header generation"""

    def test_default_csp(self):
        """Test default CSP header generation"""
        csp = get_csp_header()

        # Check default-src is included
        self.assertIn("default-src 'self'", csp)

        # Check default values for frame-ancestors and form-action
        self.assertIn("frame-ancestors 'none'", csp)
        self.assertIn("form-action 'self'", csp)

    def test_custom_csp(self):
        """Test custom CSP header generation"""
        csp = get_csp_header(
            default_src=["'self'", "https://example.com"],
            script_src=["'self'", "'unsafe-inline'"],
            style_src=["'self'", "https://fonts.googleapis.com"],
            report_uri="https://example.com/report-csp"
        )

        # Check all directives are included
        self.assertIn("default-src 'self' https://example.com", csp)
        self.assertIn("script-src 'self' 'unsafe-inline'", csp)
        self.assertIn("style-src 'self' https://fonts.googleapis.com", csp)
        self.assertIn("report-uri https://example.com/report-csp", csp)

class TestHSTSHeader(unittest.TestCase):
    """Test cases for HSTS header generation"""

    def test_default_hsts(self):
        """Test default HSTS header generation"""
        hsts = get_hsts_header()

        # Check default values
        self.assertIn("max-age=31536000", hsts)  # 1 year
        self.assertIn("includeSubDomains", hsts)
        self.assertNotIn("preload", hsts)

    def test_custom_hsts(self):
        """Test custom HSTS header generation"""
        hsts = get_hsts_header(
            max_age_seconds=86400,  # 1 day
            include_subdomains=False,
            preload=True
        )

        # Check custom values
        self.assertIn("max-age=86400", hsts)
        self.assertNotIn("includeSubDomains", hsts)
        self.assertIn("preload", hsts)

class TestPermissionsPolicyHeader(unittest.TestCase):
    """Test cases for Permissions Policy header generation"""

    def test_default_permissions(self):
        """Test default Permissions Policy header generation"""
        policy = get_permissions_policy_header()

        # Check all features are disabled by default
        self.assertIn("camera=()", policy)
        self.assertIn("microphone=()", policy)
        self.assertIn("geolocation=()", policy)
        self.assertIn("payment=()", policy)
        self.assertIn("autoplay=()", policy)
        self.assertIn("interest-cohort=()", policy)  # Always disabled

    def test_custom_permissions(self):
        """Test custom Permissions Policy header generation"""
        policy = get_permissions_policy_header(
            camera=True,
            microphone=True,
            geolocation=False,
            payment=False,
            autoplay=True
        )

        # Check custom values
        self.assertIn("camera=(self)", policy)
        self.assertIn("microphone=(self)", policy)
        self.assertIn("geolocation=()", policy)
        self.assertIn("payment=()", policy)
        self.assertIn("autoplay=(self)", policy)
        self.assertIn("interest-cohort=()", policy)  # Always disabled

if __name__ == '__main__':
    unittest.main()