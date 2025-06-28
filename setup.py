#!/usr/bin/env python3
"""
Alternative setup.py for NOUS Personal Assistant
Bypasses setuptools package discovery issues
"""

from setuptools import setup, find_packages
import os

# Read the README file
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Define packages explicitly to avoid discovery issues
packages = [
    "models",
    "routes", 
    "utils",
    "config",
    "api",
    "services",
    "handlers",
    "core",
    "voice_interface"
]

# Find packages with explicit include/exclude
found_packages = find_packages(
    include=[
        "models*",
        "routes*", 
        "utils*",
        "config*",
        "api*",
        "services*", 
        "handlers*",
        "core*",
        "voice_interface*"
    ],
    exclude=[
        "backup*",
        "logs*", 
        "uploads*",
        "cleanup*",
        "instance*",
        "flask_session*",
        "attached_assets*",
        "static*",
        "templates*",
        "tests*",
        "scripts*",
        "__pycache__*",
        "*.tests*",
        "docs*"
    ]
)

setup(
    name="nous-personal-assistant",
    version="0.2.0",
    author="NOUS Development Team",
    description="AI-powered personal assistant with comprehensive life management",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/nous-personal-assistant",
    
    # Use explicit package list instead of automatic discovery
    packages=found_packages,
    py_modules=["main", "app", "database"],
    
    # Package data
    package_data={
        "": ["*.html", "*.css", "*.js", "*.json", "*.txt", "*.md"],
    },
    include_package_data=True,
    
    # Python version requirement
    python_requires=">=3.11",
    
    # Dependencies
    install_requires=[
        "flask>=3.1.1",
        "werkzeug>=3.1.3", 
        "gunicorn>=22.0.0",
        "flask-sqlalchemy>=3.1.1",
        "flask-migrate>=4.0.7",
        "psycopg2-binary>=2.9.9",
        "authlib>=1.3.0",
        "flask-login>=0.6.3",
        "flask-session>=0.8.0",
        "python-dotenv>=1.0.1",
        "requests>=2.32.3",
        "psutil>=5.9.8",
        "soundfile>=0.12.1",
        "librosa>=0.10.1",
    ],
    
    # Optional dependencies
    extras_require={
        "audio": ["soundfile>=0.12.1", "librosa>=0.10.1"],
        "security": ["flask-wtf>=1.2.1"],
        "ai": ["google-generativeai>=0.8.0"],
        "dev": [
            "pytest>=8.0.0",
            "pytest-cov>=4.1.0",
            "pytest-mock>=3.12.0",
            "pytest-flask>=1.3.0",
            "flask-testing>=0.8.1",
            "flake8>=7.0.0",
            "black>=24.0.0",
            "mypy>=1.8.0",
            "isort>=5.13.0",
            "bandit>=1.7.6",
            "coverage>=7.4.0",
            "pipdeptree>=2.13.0",
            "pip-audit>=2.6.1",
            "deptry>=0.16.1",
        ]
    },
    
    # Entry points
    entry_points={
        "console_scripts": [
            "nous=main:main",
        ],
    },
    
    # Classifiers
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Framework :: Flask",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Office/Business :: Scheduling",
    ],
    
    # Keywords
    keywords="ai personal-assistant flask web-application productivity",
    
    # Project URLs
    project_urls={
        "Bug Reports": "https://github.com/yourusername/nous-personal-assistant/issues",
        "Source": "https://github.com/yourusername/nous-personal-assistant",
        "Documentation": "https://nous-docs.example.com",
    },
)