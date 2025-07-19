"""
Aa Content Routes
Aa Content functionality for the NOUS application
"""

from flask import Blueprint, render_template, session, request, redirect, url_for, jsonify
from utils.unified_auth import login_required, demo_allowed, get_demo_user, is_authenticated

aa_content_bp = Blueprint('aa_content', __name__)

def require_authentication():
    """Check if user is authenticated, allow demo mode"""
    # Check session authentication
    if 'user' in session and session['user']:
        return None  # User is authenticated
    
    # Allow demo mode
    if request.args.get('demo') == 'true':
        return None  # Demo mode allowed
    
    # For API endpoints, return JSON error
    if request.path.startswith('/api/'):
        return jsonify({'error': "Demo mode - limited access", 'demo_available': True}), 401
    
    # For web routes, redirect to login
    return redirect(url_for("main.demo"))

def get_demo_user():
    """Get current user from session with demo fallback"""
    return session.get('user', {
        'id': 'demo_user',
        'name': 'Demo User',
        'email': 'demo@example.com',
        'is_demo': True
    })

"""
Alcoholics Anonymous Content Routes

This module provides routes for accessing AA content such as
the Big Book text, audio versions, and speaker recordings.
"""

import os
import logging
from flask import send_file, abort, current_app

# Import models with fallback
try:
    from models.health_models import AABigBook, AASpeakerRecording, AAFavorite, db
    from models.aa_content_models import AABigBookAudio
    from utils.aa_content_loader import load_aa_content
except ImportError:
    # Fallback if models are not available
    def load_aa_content():
        return {'big_book_text': False, 'speaker_recordings': False}

# Set up blueprint
aa_content = Blueprint('aa_content', __name__, url_prefix='/aa')

# Set up logging
logger = logging.getLogger(__name__)

@aa_content.route('/')
def index():
    """AA content main page"""
    # Check authentication
    auth_result = require_authentication()
    if auth_result:
        return auth_result
        
    return render_template('aa/index.html')

@aa_content.route('/big-book')
def big_book():
    """AA Big Book reader"""
    # Check authentication
    auth_result = require_authentication()
    if auth_result:
        return auth_result
        
    # Get all chapters
    try:
        chapters = AABigBook.query.order_by(AABigBook.chapter_number).all()
    except:
        chapters = []

    # Check if we have content
    if not chapters:
        # Try to load content
        load_result = load_aa_content()
        if load_result['big_book_text']:
            # Refresh chapters list
            try:
                chapters = AABigBook.query.order_by(AABigBook.chapter_number).all()
            except:
                chapters = []
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
        try:
            current_chapter = AABigBook.query.get(chapter_id)
        except:
            current_chapter = None
    else:
        current_chapter = chapters[0] if chapters else None

    # Get audio for current chapter if available
    audio = None
    if current_chapter:
        try:
            audio = AABigBookAudio.query.filter_by(chapter_id=current_chapter.id).first()
        except:
            audio = None

    return render_template('aa/big_book.html',
        chapters=chapters,
        current_chapter=current_chapter,
        audio=audio
    )

@aa_content.route('/big-book/<int:chapter_id>')
def big_book_chapter(chapter_id):
    """Get a specific Big Book chapter"""
    # Check authentication
    auth_result = require_authentication()
    if auth_result:
        return auth_result
        
    try:
        chapter = AABigBook.query.get_or_404(chapter_id)
        audio = AABigBookAudio.query.filter_by(chapter_id=chapter_id).first()
    except:
        return jsonify({'error': 'Chapter not found'}), 404

    return render_template('aa/chapter.html',
        chapter=chapter,
        audio=audio
    )

@aa_content.route('/big-book/audio/<int:audio_id>')
def big_book_audio(audio_id):
    """Stream Big Book audio file"""
    # Check authentication
    auth_result = require_authentication()
    if auth_result:
        return auth_result
        
    try:
        audio = AABigBookAudio.query.get_or_404(audio_id)
        
        # Check if file exists
        file_path = os.path.join(current_app.root_path, audio.file_path.lstrip('/'))
        if not os.path.exists(file_path):
            abort(404)

        return send_file(file_path)
    except:
        abort(404)

@aa_content.route('/speakers')
def speakers():
    """AA speaker recordings list"""
    # Check authentication
    auth_result = require_authentication()
    if auth_result:
        return auth_result
        
    # Get all recordings
    try:
        recordings = AASpeakerRecording.query.order_by(AASpeakerRecording.speaker_name).all()
    except:
        recordings = []

    # Check if we have content
    if not recordings:
        # Try to load content
        load_result = load_aa_content()
        if load_result['speaker_recordings']:
            # Refresh recordings list
            try:
                recordings = AASpeakerRecording.query.order_by(AASpeakerRecording.speaker_name).all()
            except:
                recordings = []
        else:
            # Still no content
            return render_template('aa/speakers.html',
                recordings=[],
                error="Could not load speaker recordings"
            )

    return render_template('aa/speakers.html', recordings=recordings)

@aa_content.route('/speakers/<int:recording_id>')
def speaker_detail(recording_id):
    """Detail view for a specific speaker recording"""
    # Check authentication
    auth_result = require_authentication()
    if auth_result:
        return auth_result
        
    try:
        recording = AASpeakerRecording.query.get_or_404(recording_id)
    except:
        return jsonify({'error': 'Recording not found'}), 404

    return render_template('aa/speaker_detail.html', recording=recording)