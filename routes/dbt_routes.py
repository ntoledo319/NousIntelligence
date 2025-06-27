"""
Dialectical Behavior Therapy routes
All routes are prefixed with /dbt
"""

import os
import json
import datetime
from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash, session, current_app, abort, Response
from flask_login import login_required, current_user

# Import database from app to avoid circular imports
from app import db

# Import DBT models
from models.health_models import (
    DBTSkillLog, DBTDiaryCard, DBTSkillCategory,
    DBTSkillRecommendation, DBTSkillChallenge,
    DBTCrisisResource, DBTEmotionTrack
)

# Import helper functions
from utils.dbt_helper import (
    log_dbt_skill, get_skill_logs, create_diary_card, get_diary_cards,
    analyze_skill_effectiveness, get_skill_recommendations,
    get_available_challenges, create_challenge, update_challenge_progress,
    mark_challenge_completed, reset_challenge, generate_personalized_challenge,
    skills_on_demand, generate_diary_card, validate_experience,
    distress_tolerance, chain_analysis, wise_mind, radical_acceptance,
    interpersonal_effectiveness, dialectic_generator, trigger_map,
    skill_of_the_day, edit_message, advise
)

# Create blueprint
dbt_bp = Blueprint('dbt', __name__, url_prefix='/dbt')

# Helper to get user_id from current_user
def get_user_id():
    return str(current_user.id) if current_user.is_authenticated else None

# Main DBT dashboard
@dbt_bp.route('/')
@login_required
def dashboard():
    """Main DBT dashboard"""
    user_id = get_user_id()

    # Get recent skill logs
    recent_skills = get_skill_logs(session, limit=5)

    # Get recent diary cards
    recent_cards = get_diary_cards(session, limit=5)

    # Get available challenges
    challenges = get_available_challenges(session)

    # Get skill recommendations
    recommendations = get_skill_recommendations(session)

    return render_template('dbt/dashboard.html',
                          recent_skills=recent_skills,
                          recent_cards=recent_cards,
                          challenges=challenges,
                          recommendations=recommendations)

# Skills routes
@dbt_bp.route('/skills')
@login_required
def skills():
    """DBT skills page"""
    user_id = get_user_id()

    # Get skill logs
    logs = get_skill_logs(session)

    # Get skill categories
    categories = DBTSkillCategory.query.all()

    # Get recommendations
    recommendations = get_skill_recommendations(session)

    return render_template('dbt/skills.html',
                          logs=logs,
                          categories=categories,
                          recommendations=recommendations)

@dbt_bp.route('/skills/log', methods=['POST'])
@login_required
def log_skill():
    """Log a DBT skill usage"""
    user_id = get_user_id()

    skill_name = request.form.get('skill_name')
    category = request.form.get('category')
    situation = request.form.get('situation')

    # Optional fields
    effectiveness = None
    if 'effectiveness' in request.form:
        try:
            effectiveness = int(request.form.get('effectiveness'))
        except (ValueError, TypeError):
            pass

    notes = request.form.get('notes')

    result = log_dbt_skill(session, skill_name, category, situation, effectiveness, notes)

    if result.get('status') == 'success':
        flash('Skill logged successfully', 'success')
    else:
        flash(f'Error logging skill: {result.get("message")}', 'error')

    return redirect(url_for('dbt.skills'))

@dbt_bp.route('/skills/recommend', methods=['GET', 'POST'])
@login_required
def recommend_skills():
    """Get skill recommendations"""
    user_id = get_user_id()

    if request.method == 'POST':
        # Get recommendations based on situation
        situation = request.form.get('situation')
        recommendations = get_skill_recommendations(session, situation)
    else:
        # Get general recommendations
        recommendations = get_skill_recommendations(session)

    return render_template('dbt/recommendations.html',
                          recommendations=recommendations)

# Diary card routes
@dbt_bp.route('/diary', methods=['GET', 'POST'])
@login_required
def diary():
    """DBT diary card page"""
    user_id = get_user_id()

    if request.method == 'POST':
        # Create a new diary card
        mood_rating = request.form.get('mood_rating')
        try:
            mood_rating = int(mood_rating)
        except (ValueError, TypeError):
            mood_rating = 3  # Default

        triggers = request.form.get('triggers')
        urges = request.form.get('urges')
        skills_used = request.form.get('skills_used')
        reflection = request.form.get('reflection')

        result = create_diary_card(session, mood_rating, triggers, urges, skills_used, reflection)

        if result.get('status') == 'success':
            flash('Diary card created successfully', 'success')
        else:
            flash(f'Error creating diary card: {result.get("message")}', 'error')

        return redirect(url_for('dbt.diary'))

    # Get recent diary cards
    cards = get_diary_cards(session)

    return render_template('dbt/diary.html', cards=cards)

# Challenge routes
@dbt_bp.route('/challenges')
@login_required
def challenges():
    """DBT skill challenges page"""
    user_id = get_user_id()

    # Get category filter
    category = request.args.get('category')

    # Get challenges
    challenges = get_available_challenges(session, category)

    # Get categories
    categories = DBTSkillCategory.query.all()

    return render_template('dbt/challenges.html',
                          challenges=challenges,
                          categories=categories,
                          current_category=category)

@dbt_bp.route('/challenges/create', methods=['POST'])
@login_required
def create_new_challenge():
    """Create a new skill challenge"""
    user_id = get_user_id()

    name = request.form.get('name')
    description = request.form.get('description')
    category = request.form.get('category')

    difficulty = 1
    if 'difficulty' in request.form:
        try:
            difficulty = int(request.form.get('difficulty'))
        except (ValueError, TypeError):
            pass

    result = create_challenge(session, name, description, category, difficulty)

    if result.get('status') == 'success':
        flash('Challenge created successfully', 'success')
    else:
        flash(f'Error creating challenge: {result.get("message")}', 'error')

    return redirect(url_for('dbt.challenges'))

@dbt_bp.route('/challenges/update/<challenge_id>', methods=['POST'])
@login_required
def update_challenge(challenge_id):
    """Update a challenge's progress"""
    user_id = get_user_id()

    progress = request.form.get('progress', 0)
    try:
        progress = int(progress)
    except (ValueError, TypeError):
        progress = 0

    result = update_challenge_progress(session, challenge_id, progress)

    if result.get('status') == 'success':
        flash('Challenge progress updated', 'success')

        if result.get('completed'):
            flash('Congratulations on completing the challenge!', 'success')
    else:
        flash(f'Error updating challenge: {result.get("message")}', 'error')

    return redirect(url_for('dbt.challenges'))

@dbt_bp.route('/challenges/complete/<challenge_id>', methods=['POST'])
@login_required
def complete_challenge(challenge_id):
    """Mark a challenge as completed"""
    user_id = get_user_id()

    result = mark_challenge_completed(session, challenge_id)

    if result.get('status') == 'success':
        flash('Challenge completed successfully', 'success')
    else:
        flash(f'Error completing challenge: {result.get("message")}', 'error')

    return redirect(url_for('dbt.challenges'))

@dbt_bp.route('/challenges/reset/<challenge_id>', methods=['POST'])
@login_required
def reset_challenge_progress(challenge_id):
    """Reset a challenge to start again"""
    user_id = get_user_id()

    result = reset_challenge(session, challenge_id)

    if result.get('status') == 'success':
        flash('Challenge reset successfully', 'success')
    else:
        flash(f'Error resetting challenge: {result.get("message")}', 'error')

    return redirect(url_for('dbt.challenges'))

@dbt_bp.route('/challenges/generate', methods=['POST'])
@login_required
def generate_challenge():
    """Generate a personalized challenge"""
    user_id = get_user_id()

    category = request.form.get('category')

    result = generate_personalized_challenge(session, category)

    if result.get('status') == 'success':
        flash('New personalized challenge created', 'success')
    else:
        flash(f'Error generating challenge: {result.get("message")}', 'error')

    return redirect(url_for('dbt.challenges'))

# DBT chatbot API routes
@dbt_bp.route('/api/skills-on-demand', methods=['POST'])
@login_required
def api_skills_on_demand():
    """API endpoint for skill suggestions"""
    data = request.get_json()

    if not data or 'text' not in data:
        return jsonify({"error": "Missing text parameter"}), 400

    result = skills_on_demand(data['text'])

    return jsonify(result)

@dbt_bp.route('/api/generate-diary-card', methods=['POST'])
@login_required
def api_generate_diary_card():
    """API endpoint to generate a diary card"""
    data = request.get_json()

    if not data or 'text' not in data:
        return jsonify({"error": "Missing text parameter"}), 400

    result = generate_diary_card(data['text'])

    return jsonify(result)

@dbt_bp.route('/api/validate', methods=['POST'])
@login_required
def api_validate():
    """API endpoint for validation"""
    data = request.get_json()

    if not data or 'text' not in data:
        return jsonify({"error": "Missing text parameter"}), 400

    result = validate_experience(data['text'])

    return jsonify(result)

@dbt_bp.route('/api/distress', methods=['POST'])
@login_required
def api_distress():
    """API endpoint for distress tolerance"""
    data = request.get_json()

    if not data or 'text' not in data:
        return jsonify({"error": "Missing text parameter"}), 400

    result = distress_tolerance(data['text'])

    return jsonify(result)

@dbt_bp.route('/api/chain-analysis', methods=['POST'])
@login_required
def api_chain_analysis():
    """API endpoint for chain analysis"""
    data = request.get_json()

    if not data or 'text' not in data:
        return jsonify({"error": "Missing text parameter"}), 400

    result = chain_analysis(data['text'])

    return jsonify(result)

@dbt_bp.route('/api/wise-mind', methods=['POST'])
@login_required
def api_wise_mind():
    """API endpoint for wise mind"""
    data = request.get_json()

    if not data or 'text' not in data:
        return jsonify({"error": "Missing text parameter"}), 400

    result = wise_mind(data['text'])

    return jsonify(result)

@dbt_bp.route('/api/radical-acceptance', methods=['POST'])
@login_required
def api_radical_acceptance():
    """API endpoint for radical acceptance"""
    data = request.get_json()

    if not data or 'text' not in data:
        return jsonify({"error": "Missing text parameter"}), 400

    result = radical_acceptance(data['text'])

    return jsonify(result)

@dbt_bp.route('/api/interpersonal', methods=['POST'])
@login_required
def api_interpersonal():
    """API endpoint for interpersonal effectiveness"""
    data = request.get_json()

    if not data or 'text' not in data:
        return jsonify({"error": "Missing text parameter"}), 400

    result = interpersonal_effectiveness(data['text'])

    return jsonify(result)

@dbt_bp.route('/api/dialectic', methods=['POST'])
@login_required
def api_dialectic():
    """API endpoint for dialectical thinking"""
    data = request.get_json()

    if not data or 'text' not in data:
        return jsonify({"error": "Missing text parameter"}), 400

    result = dialectic_generator(data['text'])

    return jsonify(result)

@dbt_bp.route('/api/trigger-map', methods=['POST'])
@login_required
def api_trigger_map():
    """API endpoint for trigger mapping"""
    data = request.get_json()

    if not data or 'text' not in data:
        return jsonify({"error": "Missing text parameter"}), 400

    result = trigger_map(data['text'])

    return jsonify(result)

@dbt_bp.route('/api/skill-of-day')
@login_required
def api_skill_of_day():
    """API endpoint for skill of the day"""
    result = skill_of_the_day()

    return jsonify(result)

@dbt_bp.route('/api/edit-message', methods=['POST'])
@login_required
def api_edit_message():
    """API endpoint to edit a message with DBT skills"""
    data = request.get_json()

    if not data or 'original' not in data or 'target_skill' not in data or 'tone' not in data:
        return jsonify({"error": "Missing required parameters"}), 400

    result = edit_message(data['original'], data['target_skill'], data['tone'])

    return jsonify(result)

@dbt_bp.route('/api/advise', methods=['POST'])
@login_required
def api_advise():
    """API endpoint for DBT advice"""
    data = request.get_json()

    if not data or 'text' not in data:
        return jsonify({"error": "Missing text parameter"}), 400

    result = advise(data['text'])

    return jsonify(result)