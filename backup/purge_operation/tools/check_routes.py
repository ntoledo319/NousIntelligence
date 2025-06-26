#!/usr/bin/env python
"""
Route Standardization Checker

This command-line tool analyzes the application's routes for compliance
with standardization rules and generates a detailed report.

Usage:
    python tools/check_routes.py [--format FORMAT] [--output FILE]

Options:
    --format FORMAT  Output format: text, json (default: text)
    --output FILE    Write output to file instead of stdout
    --fix            Attempt to fix non-compliant routes (experimental)
    --help           Show this help message and exit
"""

import os
import sys
import argparse
import json
import logging
from pathlib import Path

# Add parent directory to path to import application
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

def setup_logging():
    """Configure logging for the route checker"""
    logging.basicConfig(
        level=logging.INFO,
        format='[%(asctime)s] %(levelname)s: %(message)s',
        handlers=[logging.StreamHandler()]
    )
    return logging.getLogger('route_checker')

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description='Check route standardization')
    parser.add_argument('--format', choices=['text', 'json'], default='text',
                        help='Output format (default: text)')
    parser.add_argument('--output', type=str, default=None,
                        help='Output file (default: stdout)')
    parser.add_argument('--fix', action='store_true',
                        help='Attempt to fix non-compliant routes (experimental)')
    
    return parser.parse_args()

def create_app_context():
    """Create application context for analysis"""
    try:
        # Import app differently based on how the project is structured
        try:
            from app import app
        except ImportError:
            from app import create_app
            app = create_app()
            
        return app
    except Exception as e:
        logger.error(f"Failed to create application context: {str(e)}")
        sys.exit(1)

def analyze_routes(app, output_format):
    """Analyze application routes and return report"""
    try:
        from utils.route_diagnostics import analyze_routes
        return analyze_routes(app, output_format)
    except ImportError:
        logger.error("Route diagnostics utility not found. Make sure utils/route_diagnostics.py exists.")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Error analyzing routes: {str(e)}")
        sys.exit(1)

def output_report(report, args):
    """Output the report to stdout or file"""
    if args.output:
        try:
            with open(args.output, 'w') as f:
                f.write(report if isinstance(report, str) else json.dumps(report, indent=2))
            logger.info(f"Report written to {args.output}")
        except Exception as e:
            logger.error(f"Failed to write report to {args.output}: {str(e)}")
            sys.exit(1)
    else:
        # Output to stdout
        if isinstance(report, str):
            print(report)
        else:
            print(json.dumps(report, indent=2))

def attempt_fixes(app, report_data):
    """Attempt to fix non-compliant routes (experimental)"""
    logger.warning("Route fixing is experimental and may require manual review.")
    
    # Check if we have a dict report
    if not isinstance(report_data, dict):
        try:
            # Try to parse JSON if it's a string
            report_data = json.loads(report_data)
        except:
            logger.error("Cannot fix routes - report format not recognized")
            return False
    
    # Check for issues
    if not report_data.get('compliance_issues'):
        logger.info("No compliance issues to fix!")
        return True
    
    # TODO: Implement automated fixes for common issues
    # This would involve updating route definitions in the codebase
    
    logger.info("Route fixing not fully implemented yet.")
    logger.info("Suggested fixes:")
    
    for issue in report_data.get('compliance_issues', []):
        logger.info(f"- {issue['url']} ({issue['endpoint']}): {issue['message']}")
    
    return False

if __name__ == '__main__':
    # Set up logging
    logger = setup_logging()
    
    # Parse arguments
    args = parse_arguments()
    
    # Create application context
    logger.info("Creating application context...")
    app = create_app_context()
    
    # Analyze routes
    logger.info("Analyzing routes...")
    report = analyze_routes(app, args.format)
    
    # Attempt fixes if requested
    if args.fix:
        logger.info("Attempting to fix non-compliant routes...")
        attempt_fixes(app, report)
    
    # Output report
    output_report(report, args)
    
    logger.info("Route check complete.")