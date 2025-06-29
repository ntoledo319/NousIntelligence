"""

def require_authentication():
    """Check if user is authenticated, allow demo mode"""
    from flask import session, request, redirect, url_for, jsonify
from utils.auth_compat import login_required, current_user, get_current_user, is_authenticated
    
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

Routes for image analysis features using Hugging Face's API
"""

import os
import logging
from io import BytesIO
from datetime import datetime
from flask import Blueprint, request, jsonify, render_template, redirect, url_for, session, flash
from werkzeug.utils import secure_filename
import base64

from utils.image_helper import (
    describe_image,
    detect_objects_in_image,
    analyze_image_for_travel,
    organize_images_by_content,
    get_uploaded_image_file,
    segment_image
)

# Create blueprint
image_routes = Blueprint('image_routes', __name__)

# Configure upload folder
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# Create upload directory if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    """Check if file has an allowed extension"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@image_routes.route('/image/analyze', methods=['GET', 'POST'])

    # Check authentication
    auth_result = require_authentication()
    if auth_result:
        return auth_result

def analyze_image():
    """Analyze an image using Hugging Face's API"""
    if request.method == 'GET':
        return render_template('image_upload.html')

    if 'image' not in request.files:
        flash('No image file provided')
        return redirect(request.url)

    file = request.files['image']

    if file.filename == '' or not file or not allowed_file(file.filename):
        flash('Invalid image file')
        return redirect(request.url)

    # Read the file
    file_data = file.read()

    # Get analysis type
    analysis_type = request.form.get('analysis_type', 'describe')

    # Process the image based on the analysis type
    if analysis_type == 'describe':
        result = describe_image(file_data)
    elif analysis_type == 'detect':
        result = detect_objects_in_image(file_data)
    elif analysis_type == 'travel':
        result = analyze_image_for_travel(file_data)
    elif analysis_type == 'segment':
        result = segment_image(file_data)
    else:
        result = describe_image(file_data)

    # Check for error
    if isinstance(result, dict) and 'error' in result:
        flash(f"Error during analysis: {result['error']}")
        return redirect(request.url)

    # Encode image to base64 for display
    image_base64 = base64.b64encode(file_data).decode('utf-8')

    # Create user directory if it doesn't exist
    user_id = session.get('user_id')
    user_dir = os.path.join(UPLOAD_FOLDER, f"user_{user_id}" if user_id else "anonymous")
    os.makedirs(user_dir, exist_ok=True)

    # Save the file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = secure_filename(file.filename)
    if filename:
        # Add timestamp to avoid overwriting
        filename = f"{timestamp}_{filename}"
        filepath = os.path.join(user_dir, filename)

        with open(filepath, 'wb') as f:
            f.write(file_data)

    # Return the results
    return render_template('image_results.html',
                           result=result,
                           analysis_type=analysis_type,
                           image_base64=image_base64,
                           filename=filename if filename else "unknown.jpg")

@image_routes.route('/image/gallery')

    # Check authentication
    auth_result = require_authentication()
    if auth_result:
        return auth_result

def image_gallery():
    """Display the user's uploaded image gallery, organized by content."""
    user_id = session.get('user_id')
    if not user_id:
        flash("Demo mode - some features limited")
        return redirect(url_for("main.demo"))  # Or wherever your login route is

    user_dir = os.path.join(UPLOAD_FOLDER, f"user_{user_id}")
    
    if not os.path.exists(user_dir):
        return render_template('image_gallery.html', albums={})

    image_files = []
    for filename in os.listdir(user_dir):
        if allowed_file(filename):
            filepath = os.path.join(user_dir, filename)
            with open(filepath, 'rb') as f:
                image_data = f.read()
            image_files.append({"data": image_data, "filename": filename})

    if not image_files:
        return render_template('image_gallery.html', albums={})

    albums = organize_images_by_content(image_files)

    return render_template('image_gallery.html', albums=albums, user_dir=f"user_{user_id}")

@image_routes.route('/image/organize', methods=['POST'])

    # Check authentication
    auth_result = require_authentication()
    if auth_result:
        return auth_result

def organize_images():
    """Organize multiple images by content using Hugging Face's API"""
    if 'images' not in request.files:
        flash('No image files provided')
        return redirect(url_for('image_routes.analyze_image'))

    files = request.files.getlist('images')

    if not files or len(files) == 0:
        flash('No valid image files provided')
        return redirect(url_for('image_routes.analyze_image'))

    user_id = session.get('user_id')
    user_dir = os.path.join(UPLOAD_FOLDER, f"user_{user_id}" if user_id else "anonymous")
    os.makedirs(user_dir, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    for i, file in enumerate(files):
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            if filename:
                filename = f"{timestamp}_{i}_{filename}"
                filepath = os.path.join(user_dir, filename)
                file.seek(0)
                file.save(filepath)

    flash("Images uploaded successfully and are being organized.", "success")
    return redirect(url_for('image_routes.image_gallery'))