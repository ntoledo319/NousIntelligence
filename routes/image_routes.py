"""
Image processing routes for the application
Uses Hugging Face services for cost-efficient AI image processing
"""

import os
import logging
import json
from datetime import datetime
from flask import Blueprint, request, jsonify, current_app, render_template, flash, redirect, url_for
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename

# Import our custom image helpers
from utils.image_helper import (
    describe_image,
    classify_image,
    detect_objects,
    analyze_travel_photo,
    organize_travel_photos
)

# Create blueprint
image_routes = Blueprint('image_routes', __name__)

# Configure file uploads
UPLOAD_FOLDER = 'static/uploads/images'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    """Check if file has an allowed extension"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def ensure_upload_folder():
    """Ensure the upload folder exists"""
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    user_folder = os.path.join(UPLOAD_FOLDER, str(current_user.id))
    os.makedirs(user_folder, exist_ok=True)
    return user_folder

@image_routes.route('/image/analyze', methods=['POST'])
@login_required
def analyze_image():
    """Analyze an uploaded image using Hugging Face services"""
    try:
        # Check if image was uploaded
        if 'image' not in request.files:
            flash('No image file uploaded', 'error')
            return redirect(request.referrer or url_for('index'))
            
        file = request.files['image']
        if file.filename == '':
            flash('No image selected', 'error')
            return redirect(request.referrer or url_for('index'))
            
        if file and allowed_file(file.filename):
            # Create user upload folder
            user_folder = ensure_upload_folder()
            
            # Create a unique filename using timestamp
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            filename = f"{timestamp}_{secure_filename(file.filename)}"
            filepath = os.path.join(user_folder, filename)
            
            # Save the file
            file.save(filepath)
            
            # Analyze the image
            analysis_type = request.form.get('analysis_type', 'simple')
            
            if analysis_type == 'describe':
                # Generate a description of the image
                result = describe_image(filepath)
                
            elif analysis_type == 'classify':
                # Classify what's in the image
                result = classify_image(filepath)
                
            elif analysis_type == 'detect':
                # Detect objects in the image
                result = detect_objects(filepath)
                
            elif analysis_type == 'travel':
                # Comprehensive travel photo analysis
                result = analyze_travel_photo(filepath)
                
            else:
                # Default to simple description
                result = describe_image(filepath)
                
            # Add the image path for display
            display_path = filepath.replace('static/', '')
            result['image_path'] = display_path
            
            return render_template('image_analysis.html', analysis=result)
        else:
            flash('File type not allowed', 'error')
            return redirect(request.referrer or url_for('index'))
            
    except Exception as e:
        logging.error(f"Error analyzing image: {str(e)}")
        flash(f"Error analyzing image: {str(e)}", 'error')
        return redirect(request.referrer or url_for('index'))

@image_routes.route('/image/organize', methods=['POST'])
@login_required
def organize_images():
    """Organize and categorize multiple images"""
    try:
        # Check if any images were uploaded
        if 'images' not in request.files:
            flash('No image files uploaded', 'error')
            return redirect(request.referrer or url_for('index'))
            
        files = request.files.getlist('images')
        if not files or files[0].filename == '':
            flash('No images selected', 'error')
            return redirect(request.referrer or url_for('index'))
            
        # Create user upload folder
        user_folder = ensure_upload_folder()
        batch_folder = os.path.join(user_folder, f"batch_{datetime.now().strftime('%Y%m%d%H%M%S')}")
        os.makedirs(batch_folder, exist_ok=True)
            
        # Save all uploaded files
        saved_files = []
        for file in files:
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                filepath = os.path.join(batch_folder, filename)
                file.save(filepath)
                saved_files.append(filepath)
                
        if not saved_files:
            flash('No valid image files uploaded', 'error')
            return redirect(request.referrer or url_for('index'))
                
        # Organize the saved images
        result = organize_travel_photos(batch_folder)
            
        return render_template('image_organization.html', organization=result, batch_folder=batch_folder)
            
    except Exception as e:
        logging.error(f"Error organizing images: {str(e)}")
        flash(f"Error organizing images: {str(e)}", 'error')
        return redirect(request.referrer or url_for('index'))

@image_routes.route('/image/batch_analyze', methods=['POST'])
@login_required
def batch_analyze_images():
    """Analyze all images in a directory"""
    try:
        directory = request.form.get('directory')
        if not directory or not os.path.isdir(directory):
            flash('Invalid directory specified', 'error')
            return redirect(request.referrer or url_for('index'))
            
        # Only allow directories within the user's upload folder for security
        user_folder = os.path.join(UPLOAD_FOLDER, str(current_user.id))
        if not directory.startswith(user_folder):
            flash('Unauthorized directory access', 'error')
            return redirect(request.referrer or url_for('index'))
            
        # Analyze all images in the directory
        result = organize_travel_photos(directory)
            
        return render_template('image_organization.html', organization=result, batch_folder=directory)
            
    except Exception as e:
        logging.error(f"Error batch analyzing images: {str(e)}")
        flash(f"Error batch analyzing images: {str(e)}", 'error')
        return redirect(request.referrer or url_for('index'))