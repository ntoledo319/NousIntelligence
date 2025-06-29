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

Alcoholics Anonymous Content Routes

This module provides routes for accessing AA content such as
the Big Book text, audio versions, and speaker recordings.
"""

import os
import logging
from flask import Blueprint, render_template, request, jsonify, send_file, abort, current_app

from models.health_models import AABigBook, AASpeakerRecording, AAFavorite, db
from models.aa_content_models import AABigBookAudio
from utils.aa_content_loader import load_aa_content

# Set up blueprint
aa_content = Blueprint('aa_content', __name__, url_prefix='/aa')

# Set up logging
logger = logging.getLogger(__name__)

@aa_content.route('/')

    # Check authentication
    auth_result = require_authentication()
    if auth_result:
        return auth_result

def index():
    """AA content main page"""
    return render_template('aa/index.html')

@aa_content.route('/big-book')

    # Check authentication
    auth_result = require_authentication()
    if auth_result:
        return auth_result

def big_book():
    """AA Big Book reader"""
    # Get all chapters
    chapters = AABigBook.query.order_by(AABigBook.chapter_number).all()

    # Check if we have content
    if not chapters:
        # Try to load content
        load_result = load_aa_content()
        if load_result['big_book_text']:
            # Refresh chapters list
            chapters = AABigBook.query.order_by(AABigBook.chapter_number).all()
        else:
            # Still no content
            return render_template('aa/big_book.html',
                chapters=[],
                current_chapter=None,
                error="Could not load Big Book content"
            )

    # Get requested chapter or default to first
    chapter_id = request.args.get('chapter', default=None, type=int)
    if chapter_id:
        current_chapter = AABigBook.query.get(chapter_id)
    else:
        current_chapter = chapters[0] if chapters else None

    # Get audio for current chapter if available
    audio = None
    if current_chapter:
        audio = AABigBookAudio.query.filter_by(chapter_id=current_chapter.id).first()

    return render_template('aa/big_book.html',
        chapters=chapters,
        current_chapter=current_chapter,
        audio=audio
    )

@aa_content.route('/big-book/<int:chapter_id>')

    # Check authentication
    auth_result = require_authentication()
    if auth_result:
        return auth_result

def big_book_chapter(chapter_id):
    """Get a specific Big Book chapter"""
    chapter = AABigBook.query.get_or_404(chapter_id)
    audio = AABigBookAudio.query.filter_by(chapter_id=chapter_id).first()

    return render_template('aa/chapter.html',
        chapter=chapter,
        audio=audio
    )

@aa_content.route('/big-book/audio/<int:audio_id>')

    # Check authentication
    auth_result = require_authentication()
    if auth_result:
        return auth_result

def big_book_audio(audio_id):
    """Stream Big Book audio file"""
    audio = AABigBookAudio.query.get_or_404(audio_id)

    # Check if file exists
    file_path = os.path.join(current_app.root_path, audio.file_path.lstrip('/'))
    if not os.path.exists(file_path):
        abort(404)

    return send_file(file_path)

@aa_content.route('/speakers')

    # Check authentication
    auth_result = require_authentication()
    if auth_result:
        return auth_result

def speakers():
    """AA speaker recordings list"""
    # Get all recordings
    recordings = AASpeakerRecording.query.order_by(AASpeakerRecording.speaker_name).all()

    # Check if we have content
    if not recordings:
        # Try to load content
        load_result = load_aa_content()
        if load_result['speaker_recordings']:
            # Refresh recordings list
            recordings = AASpeakerRecording.query.order_by(AASpeakerRecording.speaker_name).all()
        else:
            # Still no content
            return render_template('aa/speakers.html',
                recordings=[],
                error="Could not load speaker recordings"
            )

    return render_template('aa/speakers.html', recordings=recordings)

@aa_content.route('/speakers/<int:recording_id>')

    # Check authentication
    auth_result = require_authentication()
    if auth_result:
        return auth_result

def speaker_detail(recording_id):
    """Detail view for a specific speaker recording"""
    recording = AASpeakerRecording.query.get_or_404(recording_id)

    return render_template('aa/speaker_detail.html', recording=recording)

@aa_content.route('/speakers/audio/<int:recording_id>')

    # Check authentication
    auth_result = require_authentication()
    if auth_result:
        return auth_result

def speaker_audio(recording_id):
    """Stream speaker recording audio file"""
    recording = AASpeakerRecording.query.get_or_404(recording_id)

    # Check if file exists
    file_path = os.path.join(current_app.root_path, recording.file_path.lstrip('/'))
    if not os.path.exists(file_path):
        abort(404)

    return send_file(file_path)

@aa_content.route('/favorites', methods=['GET'])
def favorites():
    """User's favorite AA content"""
    user_favorites = AAFavorite.query.filter_by(user_id=session.get('user', {}).get('id', 'demo_user')).all()

    # Collect the actual content for each favorite
    favorite_content = []
    for fav in user_favorites:
        if fav.content_type == 'big_book':
            content = AABigBook.query.get(fav.content_id)
            if content:
                favorite_content.append({
                    'favorite_id': fav.id,
                    'type': 'big_book',
                    'title': content.chapter_title,
                    'notes': fav.notes,
                    'url': f'/aa/big-book/{content.id}',
                    'content': content
                })
        elif fav.content_type == 'speaker':
            content = AASpeakerRecording.query.get(fav.content_id)
            if content:
                favorite_content.append({
                    'favorite_id': fav.id,
                    'type': 'speaker',
                    'title': f"{content.title} by {content.speaker_name}",
                    'notes': fav.notes,
                    'url': f'/aa/speakers/{content.id}',
                    'content': content
                })

    return render_template('aa/favorites.html', favorites=favorite_content)

@aa_content.route('/favorites/add', methods=['POST'])

    # Check authentication
    auth_result = require_authentication()
    if auth_result:
        return auth_result

def add_favorite():
    """Add an item to favorites"""
    content_type = request.form.get('content_type')
    content_id = request.form.get('content_id', type=int)
    notes = request.form.get('notes', '')

    if not content_type or not content_id:
        return jsonify({'success': False, 'error': 'Missing required data'}), 400

    # Check if favorite already exists
    existing = AAFavorite.query.filter_by(
        user_id=session.get('user', {}).get('id', 'demo_user'),
        content_type=content_type,
        content_id=content_id
    ).first()

    if existing:
        # Update notes if provided
        if notes:
            existing.notes = notes
            db.session.commit()
        return jsonify({'success': True, 'message': 'Favorite updated'})

    # Create new favorite
    favorite = AAFavorite(
        user_id=session.get('user', {}).get('id', 'demo_user'),
        content_type=content_type,
        content_id=content_id,
        notes=notes
    )

    db.session.add(favorite)
    db.session.commit()

    return jsonify({'success': True, 'message': 'Added to favorites'})

@aa_content.route('/favorites/remove/<int:favorite_id>', methods=['POST'])
def remove_favorite(favorite_id):
    """Remove an item from favorites"""
    favorite = AAFavorite.query.filter_by(
        id=favorite_id,
        user_id=session.get('user', {}).get('id', 'demo_user')
    ).first_or_404()

    db.session.delete(favorite)
    db.session.commit()

    return jsonify({'success': True, 'message': 'Removed from favorites'})

@aa_content.route('/search', methods=['GET', 'POST'])

    # Check authentication
    auth_result = require_authentication()
    if auth_result:
        return auth_result

def search():
    """Search AA content"""
    query = request.args.get('q', '') or request.form.get('q', '')

    if not query:
        return render_template('aa/search.html', results=None)

    # Search in Big Book
    big_book_results = AABigBook.query.filter(
        (AABigBook.chapter_title.ilike(f'%{query}%')) |
        (AABigBook.content.ilike(f'%{query}%'))
    ).all()

    # Search in speaker recordings
    speaker_results = AASpeakerRecording.query.filter(
        (AASpeakerRecording.title.ilike(f'%{query}%')) |
        (AASpeakerRecording.speaker_name.ilike(f'%{query}%')) |
        (AASpeakerRecording.description.ilike(f'%{query}%'))
    ).all()

    # Combine results
    results = {
        'big_book': big_book_results,
        'speakers': speaker_results,
        'total_count': len(big_book_results) + len(speaker_results)
    }

    return render_template('aa/search.html', results=results, query=query)

# Register this blueprint in routes/__init__.py
# from routes.aa_content import aa_content
# app.register_blueprint(aa_content)