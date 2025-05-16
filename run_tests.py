#!/usr/bin/env python
"""
Test Runner Script

This script runs all the tests in the project with pytest and generates a coverage report.
It can be used both during development and in CI/CD pipelines.

Usage:
    python run_tests.py [--html] [--verbose]

Options:
    --html      Generate HTML coverage report
    --verbose   Show more detailed test output

@module: run_tests
@author: NOUS Development Team
"""
import os
import sys
import subprocess
import argparse

def main():
    parser = argparse.ArgumentParser(description="Run NOUS tests with coverage reporting")
    parser.add_argument('--html', action='store_true', help='Generate HTML coverage report')
    parser.add_argument('--verbose', '-v', action='store_true', help='Show verbose test output')
    args = parser.parse_args()
    
    # Set up command
    cmd = [
        'python', '-m', 'pytest',
        '--cov=utils',
        '--cov=routes',
        '--cov=models',
        '--cov-report=term'
    ]
    
    # Add HTML report if requested
    if args.html:
        cmd.append('--cov-report=html')
    
    # Add verbosity if requested
    if args.verbose:
        cmd.append('-v')
    
    # Run the tests
    print("=" * 80)
    print("Running tests with coverage reporting...")
    print("=" * 80)
    
    result = subprocess.run(cmd)
    
    if args.html:
        print("\nHTML coverage report generated in htmlcov/index.html")
    
    # Return the exit code from pytest
    return result.returncode

if __name__ == '__main__':
    sys.exit(main()) 