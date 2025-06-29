"""

def require_authentication():
    """Check if user is authenticated, allow demo mode"""
    from flask import session, request, redirect, url_for, jsonify
    
    # Check session authentication
    if 'user' in session and session['user']:
        return None  # User is authenticated
    
    # Allow demo mode
    if request.args.get('demo') == 'true':
        return None  # Demo mode allowed
    
    # For API endpoints, return JSON error
    if request.path.startswith('/api/'):
        return jsonify({'error': 'Authentication required', 'demo_available': True}), 401
    
    # For web routes, redirect to login
    return redirect(url_for('login'))

def get_current_user():
    """Get current user from session with demo fallback"""
    from flask import session
    return session.get('user', {
        'id': 'demo_user',
        'name': 'Demo User',
        'email': 'demo@example.com',
        'is_demo': True
    })

def is_authenticated():
    """Check if user is authenticated"""
    from flask import session
    return 'user' in session and session['user'] is not None

Language Learning Routes

This module defines routes for language learning features including
vocabulary management, language practice, conversation exercises,
and progress tracking.
"""

import os
import logging
import json
from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, request, jsonify, session, flash

from models.language_learning_models import (
    LanguageProfile, VocabularyItem, LearningSession
)
from services.language_learning_service import LanguageLearningService
from utils.multilingual_voice import (
    generate_speech, transcribe_speech, get_pronunciation_feedback,
    get_available_languages, LANGUAGE_CODES
)

# Set up logger
logger = logging.getLogger(__name__)

# Initialize blueprint
language_bp = Blueprint('language', __name__, url_prefix='/language')

# Initialize service
language_service = LanguageLearningService()

@language_bp.route('/')
def index():
    """Language learning dashboard"""
    user_id = session.get('user', {}).get('id', 'demo_user')
    profiles = language_service.get_user_language_profiles(user_id)
    available_languages = get_available_languages()

    return render_template(
        'language/index.html',
        profiles=profiles,
        available_languages=available_languages
    )

@language_bp.route('/profile/new', methods=['GET', 'POST'])
def new_profile():
    """Create a new language learning profile"""
    if request.method == 'POST':
        user_id = session.get('user', {}).get('id', 'demo_user')
        learning_language = request.form.get('learning_language', '')
        if not learning_language:
            flash('Learning language is required', 'error')
            return redirect(url_for('language.new_profile'))

        native_language = request.form.get('native_language', 'en-US')
        proficiency_level = request.form.get('proficiency_level', 'beginner')
        daily_goal_minutes = int(request.form.get('daily_goal_minutes', 15))
        weekly_goal_days = int(request.form.get('weekly_goal_days', 5))
        focus_areas = request.form.get('focus_areas', 'vocabulary,pronunciation,conversation')

        profile = language_service.create_language_profile(
            user_id=user_id,
            learning_language=learning_language,
            native_language=native_language,
            proficiency_level=proficiency_level,
            daily_goal_minutes=daily_goal_minutes,
            weekly_goal_days=weekly_goal_days,
            focus_areas=focus_areas
        )

        if profile:
            flash('Language profile created successfully!', 'success')
            return redirect(url_for('language.profile', profile_id=profile.id))
        else:
            flash('Failed to create language profile. Please try again.', 'error')

    available_languages = get_available_languages()
    return render_template(
        'language/new_profile.html',
        available_languages=available_languages
    )

@language_bp.route('/profile/<int:profile_id>')

    # Check authentication
    auth_result = require_authentication()
    if auth_result:
        return auth_result

def profile(profile_id):
    """View a language learning profile"""
    profile_info = language_service.get_language_profile_details(profile_id)

    if not profile_info or profile_info['profile'].user_id != session.get('user', {}).get('id', 'demo_user'):
        flash('Language profile not found or access denied.', 'error')
        return redirect(url_for('language.index'))

    return render_template(
        'language/profile.html',
        profile=profile_info
    )

@language_bp.route('/vocabulary/<int:profile_id>')

    # Check authentication
    auth_result = require_authentication()
    if auth_result:
        return auth_result

def vocabulary(profile_id):
    """Vocabulary management for a language profile"""
    profile_info = language_service.get_language_profile_details(profile_id)

    if not profile_info or profile_info['profile'].user_id != session.get('user', {}).get('id', 'demo_user'):
        flash('Language profile not found or access denied.', 'error')
        return redirect(url_for('language.index'))

    vocabulary_items = language_service.get_all_vocabulary(profile_id)

    return render_template(
        'language/vocabulary.html',
        profile=profile_info,
        vocabulary_items=vocabulary_items
    )

@language_bp.route('/vocabulary/add/<int:profile_id>', methods=['GET', 'POST'])

    # Check authentication
    auth_result = require_authentication()
    if auth_result:
        return auth_result

def add_vocabulary(profile_id):
    """Add vocabulary to a language profile"""
    profile_info = language_service.get_language_profile_details(profile_id)

    if not profile_info or profile_info['profile'].user_id != session.get('user', {}).get('id', 'demo_user'):
        flash('Language profile not found or access denied.', 'error')
        return redirect(url_for('language.index'))

    if request.method == 'POST':
        word = request.form.get('word', '')
        if not word:
            flash('Word is required', 'error')
            return redirect(url_for('language.add_vocabulary', profile_id=profile_id))

        translation = request.form.get('translation', '')
        if not translation:
            flash('Translation is required', 'error')
            return redirect(url_for('language.add_vocabulary', profile_id=profile_id))

        pronunciation = request.form.get('pronunciation')
        example = request.form.get('example')
        part_of_speech = request.form.get('part_of_speech')

        item = language_service.add_vocabulary_item(
            profile_id=profile_id,
            word=word,
            translation=translation,
            pronunciation=pronunciation,
            example=example,
            part_of_speech=part_of_speech
        )

        if item:
            flash('Vocabulary item added successfully!', 'success')
            return redirect(url_for('language.vocabulary', profile_id=profile_id))
        else:
            flash('Failed to add vocabulary item. Please try again.', 'error')

    return render_template(
        'language/add_vocabulary.html',
        profile=profile_info
    )

@language_bp.route('/practice/<int:profile_id>')

    # Check authentication
    auth_result = require_authentication()
    if auth_result:
        return auth_result

def practice_dashboard(profile_id):
    """Practice dashboard for a language profile"""
    profile_info = language_service.get_language_profile_details(profile_id)

    if not profile_info or profile_info['profile'].user_id != session.get('user', {}).get('id', 'demo_user'):
        flash('Language profile not found or access denied.', 'error')
        return redirect(url_for('language.index'))

    # Get vocabulary due for review
    review_items = language_service.get_vocabulary_for_review(profile_id)

    # Get available conversation templates
    conversation_templates = language_service.get_conversation_templates(
        profile_info['profile'].learning_language,
        profile_info['profile'].proficiency_level
    )

    return render_template(
        'language/practice_dashboard.html',
        profile=profile_info,
        review_items=review_items,
        conversation_templates=conversation_templates
    )

@language_bp.route('/practice/vocabulary/<int:profile_id>')

    # Check authentication
    auth_result = require_authentication()
    if auth_result:
        return auth_result

def practice_vocabulary(profile_id):
    """Vocabulary practice for a language profile"""
    profile_info = language_service.get_language_profile_details(profile_id)

    if not profile_info or profile_info['profile'].user_id != session.get('user', {}).get('id', 'demo_user'):
        flash('Language profile not found or access denied.', 'error')
        return redirect(url_for('language.index'))

    # Get vocabulary due for review
    review_items = language_service.get_vocabulary_for_review(profile_id)

    # Start a learning session
    learning_session = language_service.start_learning_session(profile_id, 'vocabulary')
    if learning_session:
        session['current_learning_session'] = {
            'id': learning_session.id,
            'start_time': datetime.utcnow().timestamp(),
            'items_covered': 0,
            'correct_count': 0
        }
    else:
        session['current_learning_session'] = {
            'id': None,
            'start_time': datetime.utcnow().timestamp(),
            'items_covered': 0,
            'correct_count': 0
        }

    return render_template(
        'language/practice_vocabulary.html',
        profile=profile_info,
        review_items=review_items
    )

@language_bp.route('/practice/conversation/<int:profile_id>/<int:template_id>')

    # Check authentication
    auth_result = require_authentication()
    if auth_result:
        return auth_result

def practice_conversation(profile_id, template_id):
    """Conversation practice for a language profile"""
    profile_info = language_service.get_language_profile_details(profile_id)

    if not profile_info or profile_info['profile'].user_id != session.get('user', {}).get('id', 'demo_user'):
        flash('Language profile not found or access denied.', 'error')
        return redirect(url_for('language.index'))

    # Get the conversation template with prompts
    template_data = language_service.get_template_with_prompts(template_id)

    if not template_data:
        flash('Conversation template not found.', 'error')
        return redirect(url_for('language.practice_dashboard', profile_id=profile_id))

    # Start a learning session
    learning_session = language_service.start_learning_session(profile_id, 'conversation')
    if learning_session:
        session['current_learning_session'] = {
            'id': learning_session.id,
            'start_time': datetime.utcnow().timestamp(),
            'items_covered': 0,
            'correct_count': 0
        }
    else:
        session['current_learning_session'] = {
            'id': None,
            'start_time': datetime.utcnow().timestamp(),
            'items_covered': 0,
            'correct_count': 0
        }

    return render_template(
        'language/practice_conversation.html',
        profile=profile_info,
        template=template_data['template'],
        prompts=template_data['prompts']
    )

@language_bp.route('/api/complete-session', methods=['POST'])

    # Check authentication
    auth_result = require_authentication()
    if auth_result:
        return auth_result

def complete_session():
    """API endpoint to complete a learning session"""
    data = request.get_json()

    if not data or 'session_id' not in data:
        return jsonify({'success': False, 'error': 'Missing session ID'})

    session_id = data.get('session_id')
    duration_minutes = data.get('duration_minutes')
    score = data.get('score')
    items_covered = data.get('items_covered')
    success_rate = data.get('success_rate')
    notes = data.get('notes')

    result = language_service.complete_learning_session(
        session_id=session_id,
        duration_minutes=duration_minutes,
        score=score,
        items_covered=items_covered,
        success_rate=success_rate,
        notes=notes
    )

    if result:
        return jsonify({'success': True})
    else:
        return jsonify({'success': False, 'error': 'Failed to complete session'})

@language_bp.route('/api/update-vocabulary', methods=['POST'])

    # Check authentication
    auth_result = require_authentication()
    if auth_result:
        return auth_result

def update_vocabulary():
    """API endpoint to update vocabulary after review"""
    data = request.get_json()

    if not data or 'item_id' not in data or 'correct' not in data:
        return jsonify({'success': False, 'error': 'Missing required data'})

    item_id = data.get('item_id')
    correct = data.get('correct')

    result = language_service.update_vocabulary_after_review(item_id, correct)

    if result:
        return jsonify({'success': True})
    else:
        return jsonify({'success': False, 'error': 'Failed to update vocabulary'})

@language_bp.route('/api/translate', methods=['POST'])

    # Check authentication
    auth_result = require_authentication()
    if auth_result:
        return auth_result

def translate():
    """API endpoint for text translation"""
    data = request.get_json()

    if not data or 'text' not in data or 'source_lang' not in data or 'target_lang' not in data:
        return jsonify({'success': False, 'error': 'Missing required data'})

    text = data.get('text')
    source_lang = data.get('source_lang')
    target_lang = data.get('target_lang')

    result = language_service.translate_text(text, source_lang, target_lang)

    return jsonify(result)

@language_bp.route('/api/pronounce', methods=['POST'])

    # Check authentication
    auth_result = require_authentication()
    if auth_result:
        return auth_result

def pronounce():
    """API endpoint to get pronunciation audio"""
    data = request.get_json()

    if not data or 'text' not in data or 'language' not in data:
        return jsonify({'success': False, 'error': 'Missing required data'})

    text = data.get('text')
    language = data.get('language')

    result = language_service.get_pronunciation_audio(text, language)

    return jsonify(result)

# Add to the app factory
def register_language_learning_routes(app):
    """Register language learning routes with the app"""
    app.register_blueprint(language_bp)

    # Add language profile creation to navbar if user is logged in
    @app.context_processor
    def inject_language_data():
        """Inject language data into all templates"""
        return {
            'available_languages': LANGUAGE_CODES
        }