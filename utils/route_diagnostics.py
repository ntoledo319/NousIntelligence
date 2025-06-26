"""
Route Diagnostics Tool

This module provides tools to diagnose and report on route standardization
and compliance across the application.
"""

import logging
import json
import re
from typing import Dict, List, Any, Optional, Tuple, Set
from flask import Flask, Blueprint, url_for, current_app
from werkzeug.routing import Rule

# Configure logging
logger = logging.getLogger(__name__)

class RouteDiagnostics:
    """
    Diagnostic tool for analyzing and reporting on application routes
    """

    def __init__(self, app: Optional[Flask] = None):
        """
        Initialize the route diagnostics tool

        Args:
            app: Optional Flask application to initialize with
        """
        self.app = app
        self.compliance_rules = {
            # URL format rules
            'url_format': {
                'api': r'^/api(/v\d+)?(/[\w\-]+)+$',  # API URL format: /api/vX/resource
                'web': r'^(/[\w\-]*)+$',              # Web URL format: /resource
                'auth': r'^/auth/[\w\-]+$',           # Auth URL format: /auth/action
                'static': r'^/static(/[\w\-\.]+)+$',  # Static URL format: /static/path/file.ext
            },

            # Naming conventions
            'naming_conventions': {
                'api_endpoint': r'^api\.[a-z][a-z0-9_]*$',     # API endpoint naming: api.resource_action
                'web_endpoint': r'^[a-z][a-z0-9_]*\.[a-z][a-z0-9_]*$',  # Web endpoint naming: blueprint.action
            },

            # Reserved paths that should not be used
            'reserved_paths': [
                '/admin',
                '/console',
                '/system',
                '/debug',
                '/phpMyAdmin',
            ],

            # Security standards
            'security_standards': {
                'no_sensitive_info': [
                    'password', 'token', 'secret', 'key', 'credentials',
                    'auth', 'login', 'pw', 'passwd',
                ],
            }
        }

    def analyze_routes(self) -> Dict[str, Any]:
        """
        Analyze all routes in the application for standards compliance

        Returns:
            Dict[str, Any]: Analysis report with compliance results
        """
        if not self.app:
            if current_app:
                self.app = current_app
            else:
                raise RuntimeError("No Flask application available for analysis")

        # Get all routes from the application
        routes = self._get_all_routes()

        # Generate analysis
        analysis = {
            'routes_count': len(routes),
            'route_categories': self._categorize_routes(routes),
            'compliance_issues': self._check_compliance(routes),
            'blueprint_summary': self._analyze_blueprints(routes),
            'route_details': self._get_route_details(routes),
        }

        return analysis

    def generate_report(self, output_format: str = 'dict') -> Any:
        """
        Generate a diagnostic report on route standardization

        Args:
            output_format: Format for the report ('dict', 'json', or 'text')

        Returns:
            Report in the requested format
        """
        # Run the analysis
        analysis = self.analyze_routes()

        # Format the results
        if output_format == 'json':
            return json.dumps(analysis, indent=2)
        elif output_format == 'text':
            return self._format_text_report(analysis)
        else:
            return analysis

    def check_url_compliance(self, url: str, url_type: str = None) -> Tuple[bool, Optional[str]]:
        """
        Check if a URL complies with standards for its type

        Args:
            url: URL to check
            url_type: Type of URL ('api', 'web', 'auth', 'static')

        Returns:
            Tuple[bool, Optional[str]]: (is_compliant, error_message)
        """
        # Determine URL type if not provided
        if not url_type:
            url_type = self._determine_url_type(url)

        # Check against reserved paths
        for reserved in self.compliance_rules['reserved_paths']:
            if url.startswith(reserved):
                return False, f"URL uses reserved path: {reserved}"

        # Check URL format pattern for the type
        pattern = self.compliance_rules['url_format'].get(url_type)
        if pattern and not re.match(pattern, url):
            return False, f"URL does not follow {url_type} format standard"

        # Check for security issues in URL
        for sensitive in self.compliance_rules['security_standards']['no_sensitive_info']:
            if sensitive in url.lower() and url_type != 'auth':
                return False, f"URL contains potentially sensitive term: {sensitive}"

        return True, None

    def check_endpoint_compliance(self, endpoint: str, url: str) -> Tuple[bool, Optional[str]]:
        """
        Check if an endpoint complies with naming standards

        Args:
            endpoint: Endpoint to check
            url: URL associated with the endpoint

        Returns:
            Tuple[bool, Optional[str]]: (is_compliant, error_message)
        """
        # Determine applicable naming convention
        convention_type = 'api_endpoint' if url.startswith('/api') else 'web_endpoint'

        # Skip checking Flask internal endpoints
        if endpoint.startswith('static') or '.' not in endpoint:
            return True, None

        # Check against naming convention pattern
        pattern = self.compliance_rules['naming_conventions'].get(convention_type)
        if pattern and not re.match(pattern, endpoint):
            return False, f"Endpoint name does not follow {convention_type.replace('_', ' ')} convention"

        return True, None

    def _get_all_routes(self) -> List[Dict[str, Any]]:
        """
        Get all routes from the application

        Returns:
            List[Dict[str, Any]]: List of route information
        """
        routes = []

        try:
            # Extract route information from url_map
            for rule in self.app.url_map.iter_rules():
                route_info = {
                    'endpoint': rule.endpoint,
                    'methods': list(rule.methods),
                    'url': str(rule),
                    'arguments': [arg for arg in rule.arguments],
                    'defaults': rule.defaults,
                    'rule_type': self._determine_url_type(str(rule)),
                    'blueprint': rule.endpoint.split('.')[0] if '.' in rule.endpoint else None,
                }
                routes.append(route_info)
        except Exception as e:
            logger.error(f"Error getting routes: {str(e)}")

        return routes

    def _determine_url_type(self, url: str) -> str:
        """
        Determine the type of URL

        Args:
            url: URL to check

        Returns:
            str: URL type ('api', 'web', 'auth', or 'static')
        """
        if url.startswith('/api/'):
            return 'api'
        elif url.startswith('/auth/'):
            return 'auth'
        elif url.startswith('/static/'):
            return 'static'
        else:
            return 'web'

    def _categorize_routes(self, routes: List[Dict[str, Any]]) -> Dict[str, int]:
        """
        Categorize routes by type

        Args:
            routes: List of route information

        Returns:
            Dict[str, int]: Count of routes by category
        """
        categories = {
            'api': 0,
            'web': 0,
            'auth': 0,
            'static': 0,
        }

        for route in routes:
            route_type = route['rule_type']
            categories[route_type] = categories.get(route_type, 0) + 1

        return categories

    def _check_compliance(self, routes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Check routes for compliance with standards

        Args:
            routes: List of route information

        Returns:
            List[Dict[str, Any]]: List of compliance issues
        """
        issues = []

        for route in routes:
            url = route['url']
            endpoint = route['endpoint']

            # Check URL compliance
            url_compliant, url_message = self.check_url_compliance(url, route['rule_type'])
            if not url_compliant:
                issues.append({
                    'type': 'url_format',
                    'url': url,
                    'endpoint': endpoint,
                    'message': url_message
                })

            # Check endpoint naming compliance
            endpoint_compliant, endpoint_message = self.check_endpoint_compliance(endpoint, url)
            if not endpoint_compliant:
                issues.append({
                    'type': 'naming_convention',
                    'url': url,
                    'endpoint': endpoint,
                    'message': endpoint_message
                })

        return issues

    def _analyze_blueprints(self, routes: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze blueprints used in the application

        Args:
            routes: List of route information

        Returns:
            Dict[str, Any]: Blueprint analysis results
        """
        blueprint_counts = {}
        blueprint_url_patterns = {}
        inconsistent_blueprints = []

        # Gather blueprint information
        for route in routes:
            blueprint = route['blueprint']
            if not blueprint:
                continue

            # Count routes by blueprint
            blueprint_counts[blueprint] = blueprint_counts.get(blueprint, 0) + 1

            # Analyze URL patterns
            url = route['url']
            prefix = self._extract_blueprint_prefix(url, blueprint)

            if blueprint not in blueprint_url_patterns:
                blueprint_url_patterns[blueprint] = {prefix}
            else:
                blueprint_url_patterns[blueprint].add(prefix)

        # Check for inconsistent URL prefixes
        for blueprint, prefixes in blueprint_url_patterns.items():
            if len(prefixes) > 1:
                inconsistent_blueprints.append({
                    'blueprint': blueprint,
                    'prefixes': list(prefixes)
                })

        return {
            'blueprint_counts': blueprint_counts,
            'inconsistent_prefixes': inconsistent_blueprints
        }

    def _extract_blueprint_prefix(self, url: str, blueprint: str) -> str:
        """
        Extract the URL prefix for a blueprint

        Args:
            url: URL to analyze
            blueprint: Blueprint name

        Returns:
            str: URL prefix
        """
        parts = url.split('/')

        # Handle special cases
        if blueprint == 'static':
            return '/static'

        # Try to find common prefix pattern
        if len(parts) >= 2:
            # Most blueprints use their name as the first URL segment
            if parts[1] == blueprint or parts[1] == blueprint.replace('_', '-'):
                return f"/{parts[1]}"

        # Return the first segment as a default
        return f"/{parts[1]}" if len(parts) >= 2 else "/"

    def _get_route_details(self, routes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Get detailed information about routes

        Args:
            routes: List of route information

        Returns:
            List[Dict[str, Any]]: Detailed route information
        """
        route_details = []

        for route in routes:
            # Skip static routes to keep the report cleaner
            if route['rule_type'] == 'static':
                continue

            detail = {
                'url': route['url'],
                'endpoint': route['endpoint'],
                'methods': route['methods'],
                'type': route['rule_type'],
                'blueprint': route['blueprint'],
                'url_compliance': self.check_url_compliance(route['url'], route['rule_type'])[0],
                'endpoint_compliance': self.check_endpoint_compliance(route['endpoint'], route['url'])[0],
            }
            route_details.append(detail)

        return route_details

    def _format_text_report(self, analysis: Dict[str, Any]) -> str:
        """
        Format analysis results as a text report

        Args:
            analysis: Analysis results

        Returns:
            str: Formatted text report
        """
        report = []

        report.append("=" * 80)
        report.append("ROUTE STANDARDIZATION DIAGNOSTIC REPORT")
        report.append("=" * 80)
        report.append("")

        # Overall statistics
        report.append("-" * 40)
        report.append("ROUTE STATISTICS")
        report.append("-" * 40)
        report.append(f"Total routes: {analysis['routes_count']}")
        for category, count in analysis['route_categories'].items():
            report.append(f"  {category.upper()} routes: {count}")
        report.append("")

        # Blueprint summary
        report.append("-" * 40)
        report.append("BLUEPRINT SUMMARY")
        report.append("-" * 40)
        for blueprint, count in analysis['blueprint_summary']['blueprint_counts'].items():
            report.append(f"Blueprint '{blueprint}': {count} routes")
        report.append("")

        # Inconsistent blueprints
        if analysis['blueprint_summary']['inconsistent_prefixes']:
            report.append("Inconsistent blueprint URL prefixes:")
            for item in analysis['blueprint_summary']['inconsistent_prefixes']:
                report.append(f"  Blueprint '{item['blueprint']}' has multiple prefixes: {', '.join(item['prefixes'])}")
            report.append("")

        # Compliance issues
        if analysis['compliance_issues']:
            report.append("-" * 40)
            report.append("COMPLIANCE ISSUES")
            report.append("-" * 40)
            for issue in analysis['compliance_issues']:
                report.append(f"Issue type: {issue['type']}")
                report.append(f"  URL: {issue['url']}")
                report.append(f"  Endpoint: {issue['endpoint']}")
                report.append(f"  Message: {issue['message']}")
                report.append("")
        else:
            report.append("No compliance issues found!")
            report.append("")

        # Route details (limited)
        report.append("-" * 40)
        report.append("ROUTE DETAILS (non-compliant only)")
        report.append("-" * 40)
        non_compliant = [r for r in analysis['route_details']
                         if not (r['url_compliance'] and r['endpoint_compliance'])]

        if non_compliant:
            for route in non_compliant:
                report.append(f"URL: {route['url']}")
                report.append(f"  Endpoint: {route['endpoint']}")
                report.append(f"  Methods: {', '.join(route['methods'])}")
                report.append(f"  Type: {route['type']}")
                report.append(f"  URL compliance: {'Yes' if route['url_compliance'] else 'No'}")
                report.append(f"  Endpoint compliance: {'Yes' if route['endpoint_compliance'] else 'No'}")
                report.append("")
        else:
            report.append("All routes comply with standards!")
            report.append("")

        return "\n".join(report)

# Singleton instance for global use
route_diagnostics = RouteDiagnostics()

def analyze_routes(app: Optional[Flask] = None, output_format: str = 'dict') -> Any:
    """
    Analyze all routes in the application (convenience function)

    Args:
        app: Flask application to analyze
        output_format: Format for the report ('dict', 'json', or 'text')

    Returns:
        Analysis report in the specified format
    """
    diagnostics = route_diagnostics
    diagnostics.app = app or current_app
    return diagnostics.generate_report(output_format)