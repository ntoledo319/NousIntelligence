#!/usr/bin/env python
"""
Initialize reflection prompts for the knowledge base
"""

from app import app
from utils.knowledge_helper import initialize_reflection_prompts

with app.app_context():
    initialize_reflection_prompts()
    print('Initial reflection prompts added successfully')