"""
Dashboard Routes Module

This module defines routes for the dashboard and related functionality.

@module routes.dashboard
@description Dashboard and authenticated user routes
"""

import logging
from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from models import db, Task

# Create blueprint
dashboard_bp = Blueprint('dashboard', __name__)
logger = logging.getLogger(__name__)

@dashboard_bp.route('/dashboard')
@login_required
def dashboard():
    """Render the dashboard page"""
    # Get the user's incomplete tasks for the dashboard
    tasks = Task.query.filter_by(
        user_id=current_user.id, 
        completed=False
    ).order_by(Task.due_date.asc()).limit(5).all()
    
    return render_template('dashboard.html', tasks=tasks)

@dashboard_bp.route('/tasks', methods=['GET', 'POST'])
@login_required
def tasks():
    """Render the tasks page and handle task creation"""
    if request.method == 'POST':
        # Create a new task
        title = request.form.get('title')
        description = request.form.get('description')
        priority = request.form.get('priority', 'medium')
        due_date_str = request.form.get('due_date')
        
        # Validate input
        if not title:
            flash('Task title is required', 'warning')
            return redirect(url_for('dashboard.tasks'))
        
        # Parse due date if provided
        due_date = None
        if due_date_str:
            try:
                due_date = datetime.strptime(due_date_str, '%Y-%m-%d')
            except ValueError:
                flash('Invalid date format', 'warning')
                return redirect(url_for('dashboard.tasks'))
        
        # Create new task
        task = Task(
            user_id=current_user.id,
            title=title,
            description=description,
            priority=priority,
            due_date=due_date
        )
        
        # Save to database
        try:
            db.session.add(task)
            db.session.commit()
            flash('Task created successfully', 'success')
        except Exception as e:
            logger.error(f"Error creating task: {str(e)}")
            db.session.rollback()
            flash('An error occurred while creating the task', 'danger')
        
        return redirect(url_for('dashboard.tasks'))
    
    # Get all tasks for the user
    tasks = Task.query.filter_by(user_id=current_user.id).order_by(
        Task.completed, Task.due_date.asc() if Task.due_date else Task.created_at.desc()
    ).all()
    
    return render_template('tasks.html', tasks=tasks)

@dashboard_bp.route('/tasks/<int:task_id>/update', methods=['POST'])
@login_required
def update_task(task_id):
    """Update an existing task"""
    task = Task.query.filter_by(id=task_id, user_id=current_user.id).first_or_404()
    
    # Update task fields
    if 'title' in request.form:
        task.title = request.form.get('title')
    if 'description' in request.form:
        task.description = request.form.get('description')
    if 'priority' in request.form:
        task.priority = request.form.get('priority')
    if 'due_date' in request.form and request.form.get('due_date'):
        try:
            task.due_date = datetime.strptime(request.form.get('due_date'), '%Y-%m-%d')
        except ValueError:
            flash('Invalid date format', 'warning')
            return redirect(url_for('dashboard.tasks'))
    if 'completed' in request.form:
        task.completed = request.form.get('completed') == 'on'
    
    # Save changes
    try:
        db.session.commit()
        flash('Task updated successfully', 'success')
    except Exception as e:
        logger.error(f"Error updating task: {str(e)}")
        db.session.rollback()
        flash('An error occurred while updating the task', 'danger')
    
    return redirect(url_for('dashboard.tasks'))

@dashboard_bp.route('/tasks/<int:task_id>/delete', methods=['POST'])
@login_required
def delete_task(task_id):
    """Delete a task"""
    task = Task.query.filter_by(id=task_id, user_id=current_user.id).first_or_404()
    
    try:
        db.session.delete(task)
        db.session.commit()
        flash('Task deleted successfully', 'success')
    except Exception as e:
        logger.error(f"Error deleting task: {str(e)}")
        db.session.rollback()
        flash('An error occurred while deleting the task', 'danger')
    
    return redirect(url_for('dashboard.tasks'))

@dashboard_bp.route('/tasks/<int:task_id>/toggle', methods=['POST'])
@login_required
def toggle_task(task_id):
    """Toggle task completion status"""
    task = Task.query.filter_by(id=task_id, user_id=current_user.id).first_or_404()
    
    # Toggle completion status
    task.completed = not task.completed
    
    # Save changes
    try:
        db.session.commit()
        status = 'completed' if task.completed else 'marked as incomplete'
        flash(f'Task {status} successfully', 'success')
    except Exception as e:
        logger.error(f"Error toggling task: {str(e)}")
        db.session.rollback()
        flash('An error occurred while updating the task', 'danger')
    
    # If AJAX request, return minimal response
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return {'success': True, 'completed': task.completed}
    
    return redirect(url_for('dashboard.tasks')) 