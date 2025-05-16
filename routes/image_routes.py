"""
Routes for image analysis features using Hugging Face's API
"""

import os
import logging
from io import BytesIO
from datetime import datetime
from flask import Blueprint, request, jsonify, render_template, redirect, url_for, session, flash
from werkzeug.utils import secure_filename

from utils.image_helper import (
    describe_image,
    detect_objects_in_image,
    analyze_image_for_travel,
    organize_images_by_content,
    get_uploaded_image_file
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
    else:
        result = describe_image(file_data)
        
    # Check for error
    if isinstance(result, dict) and 'error' in result:
        flash(f"Error during analysis: {result['error']}")
        return redirect(request.url)
        
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
                          filename=filename if filename else "unknown.jpg")

@image_routes.route('/image/organize', methods=['POST'])
def organize_images():
    """Organize multiple images by content using Hugging Face's API"""
    if 'images' not in request.files:
        flash('No image files provided')
        return redirect(url_for('image_routes.analyze_image'))
        
    files = request.files.getlist('images')
    
    if not files or len(files) == 0:
        flash('No valid image files provided')
        return redirect(url_for('image_routes.analyze_image'))
        
    # Read all files
    image_data = []
    filenames = []
    
    for file in files:
        if file and allowed_file(file.filename):
            image_data.append(file.read())
            filenames.append(file.filename)
            
    if len(image_data) == 0:
        flash('No valid image files provided')
        return redirect(url_for('image_routes.analyze_image'))
        
    # Organize the images
    result = organize_images_by_content(image_data)
    
    # Check for error
    if isinstance(result, dict) and 'error' in result:
        flash(f"Error during organization: {result['error']}")
        return redirect(url_for('image_routes.analyze_image'))
        
    # Create user directory if it doesn't exist
    user_id = session.get('user_id')
    user_dir = os.path.join(UPLOAD_FOLDER, f"user_{user_id}" if user_id else "anonymous")
    os.makedirs(user_dir, exist_ok=True)
    
    # Save the files
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    saved_files = []
    
    for i, file_data in enumerate(image_data):
        if i < len(filenames):
            filename = secure_filename(filenames[i])
            if filename:
                # Add timestamp and index to avoid overwriting
                filename = f"{timestamp}_{i}_{filename}"
                filepath = os.path.join(user_dir, filename)
                
                with open(filepath, 'wb') as f:
                    f.write(file_data)
                    
                saved_files.append(filename)
                
    # Return the results
    return render_template('image_organization.html', 
                          categories=result, 
                          filenames=saved_files)