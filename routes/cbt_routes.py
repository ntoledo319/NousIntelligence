"""
CBT (Cognitive Behavioral Therapy) Routes
Comprehensive CBT feature set for NOUS personal assistant
All routes are prefixed with /cbt
"""

import os
import json
from datetime import datetime, date, timedelta
from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash, session, current_app
from flask_login import login_required, current_user

# Import database
from database import db

# Import CBT models
from models.health_models import (
    CBTThoughtRecord, CBTCognitiveBias, CBTBehaviorExperiment,
    CBTActivitySchedule, CBTMoodLog, CBTCopingSkill, CBTSkillUsage, CBTGoal
)

# Import CBT helper functions
from utils.cbt_helper import (
    create_thought_record, complete_thought_record, get_thought_records, analyze_thought_patterns,
    identify_cognitive_bias, log_cognitive_bias,
    log_mood, get_mood_trends,
    get_coping_skills, recommend_coping_skill, log_skill_usage,
    create_behavior_experiment, complete_behavior_experiment,
    schedule_activity, complete_activity,
    cbt_ai_assistant, COGNITIVE_BIASES
)

# Create blueprint
cbt_bp = Blueprint('cbt', __name__, url_prefix='/cbt')

def get_user_id():
    """Get current user ID"""
    return str(current_user.id) if current_user.is_authenticated else None

# ===== MAIN CBT DASHBOARD =====

@cbt_bp.route('/')
@login_required
def dashboard():
    """Main CBT dashboard"""
    try:
        # Get recent thought records
        recent_thoughts = get_thought_records(session, limit=5)
        
        # Get recent mood logs
        user_id = get_user_id()
        recent_moods = CBTMoodLog.query.filter_by(user_id=user_id)\
                                      .order_by(CBTMoodLog.created_at.desc())\
                                      .limit(5).all()
        
        # Get current goals
        current_goals = CBTGoal.query.filter_by(user_id=user_id, status='active')\
                                    .order_by(CBTGoal.priority.desc())\
                                    .limit(3).all()
        
        # Get upcoming activities
        upcoming_activities = CBTActivitySchedule.query.filter_by(user_id=user_id)\
                                                      .filter(CBTActivitySchedule.scheduled_date >= date.today())\
                                                      .filter_by(completion_status='planned')\
                                                      .order_by(CBTActivitySchedule.scheduled_date)\
                                                      .limit(5).all()
        
        # Get most used coping skills
        popular_skills = CBTCopingSkill.query.filter(
            db.or_(CBTCopingSkill.user_id == None, CBTCopingSkill.user_id == user_id)
        ).order_by(CBTCopingSkill.usage_count.desc()).limit(5).all()
        
        return render_template('cbt/dashboard.html',
                             recent_thoughts=recent_thoughts,
                             recent_moods=[mood.to_dict() for mood in recent_moods],
                             current_goals=[goal.to_dict() for goal in current_goals],
                             upcoming_activities=[activity.to_dict() for activity in upcoming_activities],
                             popular_skills=[skill.to_dict() for skill in popular_skills])
    
    except Exception as e:
        flash(f"Error loading CBT dashboard: {str(e)}", "error")
        return render_template('cbt/dashboard.html', 
                             recent_thoughts=[], recent_moods=[], current_goals=[], 
                             upcoming_activities=[], popular_skills=[])

# ===== THOUGHT RECORDS =====

@cbt_bp.route('/thought-records')
@login_required
def thought_records():
    """Thought records management page"""
    thoughts = get_thought_records(session, limit=20)
    return render_template('cbt/thought_records.html', thoughts=thoughts)

@cbt_bp.route('/thought-records/new')
@login_required
def new_thought_record():
    """Create new thought record page"""
    return render_template('cbt/new_thought_record.html')

@cbt_bp.route('/thought-records/<int:record_id>')
@login_required
def view_thought_record(record_id):
    """View specific thought record"""
    user_id = get_user_id()
    record = CBTThoughtRecord.query.filter_by(id=record_id, user_id=user_id).first()
    if not record:
        flash("Thought record not found", "error")
        return redirect(url_for('cbt.thought_records'))
    
    return render_template('cbt/view_thought_record.html', record=record.to_dict())

@cbt_bp.route('/api/thought-records', methods=['POST'])
@login_required
def api_create_thought_record():
    """Create a new thought record"""
    data = request.get_json()
    
    if not data or 'situation' not in data or 'automatic_thought' not in data:
        return jsonify({"error": "Missing required fields: situation, automatic_thought"}), 400
    
    result = create_thought_record(
        session,
        situation=data['situation'],
        automatic_thought=data['automatic_thought'],
        emotion=data.get('emotion'),
        emotion_intensity=data.get('emotion_intensity')
    )
    
    if result.get('success'):
        # Identify potential cognitive biases
        biases = identify_cognitive_bias(data['automatic_thought'])
        result['identified_biases'] = biases
        
        return jsonify(result), 201
    else:
        return jsonify(result), 400

@cbt_bp.route('/api/thought-records/<int:record_id>', methods=['PUT'])
@login_required
def api_complete_thought_record(record_id):
    """Complete a thought record with cognitive restructuring"""
    data = request.get_json()
    
    result = complete_thought_record(
        record_id=record_id,
        evidence_for=data.get('evidence_for'),
        evidence_against=data.get('evidence_against'),
        balanced_thought=data.get('balanced_thought'),
        new_emotion=data.get('new_emotion'),
        new_emotion_intensity=data.get('new_emotion_intensity')
    )
    
    return jsonify(result), 200 if result.get('success') else 400

@cbt_bp.route('/api/thought-records/analysis')
@login_required
def api_thought_pattern_analysis():
    """Get analysis of thought patterns"""
    result = analyze_thought_patterns(session)
    return jsonify(result)

# ===== MOOD TRACKING =====

@cbt_bp.route('/mood-tracking')
@login_required
def mood_tracking():
    """Mood tracking dashboard"""
    mood_trends = get_mood_trends(session, days=30)
    return render_template('cbt/mood_tracking.html', mood_trends=mood_trends)

@cbt_bp.route('/api/mood', methods=['POST'])
@login_required
def api_log_mood():
    """Log a mood entry"""
    data = request.get_json()
    
    if not data or 'primary_emotion' not in data or 'emotion_intensity' not in data:
        return jsonify({"error": "Missing required fields: primary_emotion, emotion_intensity"}), 400
    
    result = log_mood(
        session,
        primary_emotion=data['primary_emotion'],
        emotion_intensity=data['emotion_intensity'],
        triggers=data.get('triggers'),
        thoughts=data.get('thoughts'),
        coping_strategy_used=data.get('coping_strategy_used'),
        effectiveness_rating=data.get('effectiveness_rating')
    )
    
    return jsonify(result), 201 if result.get('success') else 400

@cbt_bp.route('/api/mood/trends')
@login_required
def api_mood_trends():
    """Get mood trends analysis"""
    days = request.args.get('days', 30, type=int)
    result = get_mood_trends(session, days=days)
    return jsonify(result)

# ===== COPING SKILLS =====

@cbt_bp.route('/coping-skills')
@login_required
def coping_skills():
    """Coping skills library"""
    category = request.args.get('category')
    skills = get_coping_skills(session, category=category)
    categories = ['grounding', 'relaxation', 'cognitive', 'behavioral', 'social']
    
    return render_template('cbt/coping_skills.html', 
                         skills=skills, 
                         categories=categories,
                         selected_category=category)

@cbt_bp.route('/coping-skills/<int:skill_id>')
@login_required
def view_coping_skill(skill_id):
    """View specific coping skill"""
    user_id = get_user_id()
    skill = CBTCopingSkill.query.filter(
        db.and_(
            CBTCopingSkill.id == skill_id,
            db.or_(CBTCopingSkill.user_id == None, CBTCopingSkill.user_id == user_id)
        )
    ).first()
    
    if not skill:
        flash("Coping skill not found", "error")
        return redirect(url_for('cbt.coping_skills'))
    
    return render_template('cbt/view_coping_skill.html', skill=skill.to_dict())

@cbt_bp.route('/api/coping-skills')
@login_required
def api_get_coping_skills():
    """Get coping skills"""
    category = request.args.get('category')
    situation = request.args.get('situation')
    skills = get_coping_skills(session, category=category, situation=situation)
    return jsonify({"skills": skills})

@cbt_bp.route('/api/coping-skills/recommend', methods=['POST'])
@login_required
def api_recommend_coping_skill():
    """Get coping skill recommendation"""
    data = request.get_json()
    
    if not data or 'situation' not in data:
        return jsonify({"error": "Missing required field: situation"}), 400
    
    result = recommend_coping_skill(
        session,
        situation=data['situation'],
        current_emotion=data.get('current_emotion'),
        intensity=data.get('intensity')
    )
    
    return jsonify(result)

@cbt_bp.route('/api/coping-skills/<int:skill_id>/use', methods=['POST'])
@login_required
def api_log_skill_usage(skill_id):
    """Log usage of a coping skill"""
    data = request.get_json()
    
    result = log_skill_usage(
        session,
        skill_id=skill_id,
        situation=data.get('situation'),
        mood_before=data.get('mood_before'),
        mood_after=data.get('mood_after'),
        effectiveness_rating=data.get('effectiveness_rating'),
        duration_used=data.get('duration_used'),
        notes=data.get('notes')
    )
    
    return jsonify(result), 201 if result.get('success') else 400

# ===== BEHAVIORAL EXPERIMENTS =====

@cbt_bp.route('/behavior-experiments')
@login_required
def behavior_experiments():
    """Behavioral experiments management"""
    user_id = get_user_id()
    experiments = CBTBehaviorExperiment.query.filter_by(user_id=user_id)\
                                            .order_by(CBTBehaviorExperiment.created_at.desc()).all()
    
    return render_template('cbt/behavior_experiments.html', 
                         experiments=[exp.to_dict() for exp in experiments])

@cbt_bp.route('/api/behavior-experiments', methods=['POST'])
@login_required
def api_create_behavior_experiment():
    """Create a new behavioral experiment"""
    data = request.get_json()
    
    if not data or 'belief_to_test' not in data or 'experiment_description' not in data:
        return jsonify({"error": "Missing required fields: belief_to_test, experiment_description"}), 400
    
    result = create_behavior_experiment(
        session,
        belief_to_test=data['belief_to_test'],
        experiment_description=data['experiment_description'],
        predicted_outcome=data.get('predicted_outcome'),
        confidence_before=data.get('confidence_before'),
        planned_date=data.get('planned_date')
    )
    
    return jsonify(result), 201 if result.get('success') else 400

@cbt_bp.route('/api/behavior-experiments/<int:experiment_id>/complete', methods=['PUT'])
@login_required
def api_complete_behavior_experiment(experiment_id):
    """Complete a behavioral experiment"""
    data = request.get_json()
    
    if not data or 'actual_outcome' not in data:
        return jsonify({"error": "Missing required field: actual_outcome"}), 400
    
    result = complete_behavior_experiment(
        experiment_id=experiment_id,
        actual_outcome=data['actual_outcome'],
        confidence_after=data.get('confidence_after'),
        lessons_learned=data.get('lessons_learned')
    )
    
    return jsonify(result), 200 if result.get('success') else 400

# ===== ACTIVITY SCHEDULING =====

@cbt_bp.route('/activity-scheduling')
@login_required
def activity_scheduling():
    """Activity scheduling dashboard"""
    user_id = get_user_id()
    
    # Get upcoming activities
    upcoming = CBTActivitySchedule.query.filter_by(user_id=user_id)\
                                       .filter(CBTActivitySchedule.scheduled_date >= date.today())\
                                       .order_by(CBTActivitySchedule.scheduled_date).all()
    
    # Get recent completed activities
    recent_completed = CBTActivitySchedule.query.filter_by(user_id=user_id)\
                                               .filter(CBTActivitySchedule.completion_status.in_(['completed', 'partial']))\
                                               .order_by(CBTActivitySchedule.scheduled_date.desc())\
                                               .limit(10).all()
    
    return render_template('cbt/activity_scheduling.html',
                         upcoming_activities=[act.to_dict() for act in upcoming],
                         recent_completed=[act.to_dict() for act in recent_completed])

@cbt_bp.route('/api/activities', methods=['POST'])
@login_required
def api_schedule_activity():
    """Schedule a new activity"""
    data = request.get_json()
    
    if not data or 'activity_name' not in data or 'category' not in data or 'scheduled_date' not in data:
        return jsonify({"error": "Missing required fields: activity_name, category, scheduled_date"}), 400
    
    result = schedule_activity(
        session,
        activity_name=data['activity_name'],
        category=data['category'],
        scheduled_date=data['scheduled_date'],
        scheduled_time=data.get('scheduled_time'),
        duration_minutes=data.get('duration_minutes'),
        difficulty_level=data.get('difficulty_level'),
        predicted_mood=data.get('predicted_mood')
    )
    
    return jsonify(result), 201 if result.get('success') else 400

@cbt_bp.route('/api/activities/<int:activity_id>/complete', methods=['PUT'])
@login_required
def api_complete_activity(activity_id):
    """Mark an activity as completed"""
    data = request.get_json()
    
    result = complete_activity(
        activity_id=activity_id,
        actual_mood_before=data.get('actual_mood_before'),
        actual_mood_after=data.get('actual_mood_after'),
        completion_status=data.get('completion_status', 'completed'),
        notes=data.get('notes')
    )
    
    return jsonify(result), 200 if result.get('success') else 400

# ===== COGNITIVE BIASES =====

@cbt_bp.route('/cognitive-biases')
@login_required
def cognitive_biases():
    """Cognitive biases tracking"""
    user_id = get_user_id()
    user_biases = CBTCognitiveBias.query.filter_by(user_id=user_id)\
                                       .order_by(CBTCognitiveBias.frequency_count.desc()).all()
    
    return render_template('cbt/cognitive_biases.html',
                         user_biases=[bias.to_dict() for bias in user_biases],
                         all_biases=COGNITIVE_BIASES)

@cbt_bp.route('/api/cognitive-biases/identify', methods=['POST'])
@login_required
def api_identify_cognitive_bias():
    """Identify cognitive biases in text"""
    data = request.get_json()
    
    if not data or 'thought_text' not in data:
        return jsonify({"error": "Missing required field: thought_text"}), 400
    
    biases = identify_cognitive_bias(data['thought_text'])
    
    return jsonify({
        "success": True,
        "identified_biases": biases,
        "total_found": len(biases)
    })

@cbt_bp.route('/api/cognitive-biases/log', methods=['POST'])
@login_required
def api_log_cognitive_bias():
    """Log a cognitive bias occurrence"""
    data = request.get_json()
    
    if not data or 'bias_type' not in data or 'example_thought' not in data:
        return jsonify({"error": "Missing required fields: bias_type, example_thought"}), 400
    
    result = log_cognitive_bias(session, data['bias_type'], data['example_thought'])
    
    return jsonify(result), 201 if result.get('success') else 400

# ===== GOALS =====

@cbt_bp.route('/goals')
@login_required
def goals():
    """CBT goals management"""
    user_id = get_user_id()
    active_goals = CBTGoal.query.filter_by(user_id=user_id, status='active')\
                                .order_by(CBTGoal.priority.desc()).all()
    completed_goals = CBTGoal.query.filter_by(user_id=user_id, status='completed')\
                                  .order_by(CBTGoal.updated_at.desc()).limit(10).all()
    
    return render_template('cbt/goals.html',
                         active_goals=[goal.to_dict() for goal in active_goals],
                         completed_goals=[goal.to_dict() for goal in completed_goals])

@cbt_bp.route('/api/goals', methods=['POST'])
@login_required
def api_create_goal():
    """Create a new CBT goal"""
    data = request.get_json()
    
    if not data or 'title' not in data or 'description' not in data:
        return jsonify({"error": "Missing required fields: title, description"}), 400
    
    try:
        user_id = get_user_id()
        goal = CBTGoal(
            user_id=user_id,
            goal_type=data.get('goal_type', 'behavioral'),
            title=data['title'],
            description=data['description'],
            target_behavior=data.get('target_behavior'),
            success_criteria=data.get('success_criteria'),
            baseline_measurement=data.get('baseline_measurement'),
            target_measurement=data.get('target_measurement'),
            measurement_unit=data.get('measurement_unit'),
            target_date=datetime.strptime(data['target_date'], "%Y-%m-%d").date() if data.get('target_date') else None,
            priority=data.get('priority', 'medium')
        )
        
        db.session.add(goal)
        db.session.commit()
        
        return jsonify({
            "success": True,
            "message": "Goal created successfully",
            "data": goal.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e), "success": False}), 400

# ===== AI ASSISTANT =====

@cbt_bp.route('/ai-assistant')
@login_required
def ai_assistant():
    """CBT AI assistant interface"""
    return render_template('cbt/ai_assistant.html')

@cbt_bp.route('/api/ai-assistant', methods=['POST'])
@login_required
def api_cbt_ai_assistant():
    """Get AI-powered CBT assistance"""
    data = request.get_json()
    
    if not data or 'user_input' not in data:
        return jsonify({"error": "Missing required field: user_input"}), 400
    
    result = cbt_ai_assistant(
        user_input=data['user_input'],
        context=data.get('context', 'general')
    )
    
    return jsonify(result)

# ===== QUICK ACTIONS =====

@cbt_bp.route('/api/quick-check-in', methods=['POST'])
@login_required
def api_quick_check_in():
    """Quick mood and coping check-in"""
    data = request.get_json()
    
    if not data or 'emotion' not in data or 'intensity' not in data:
        return jsonify({"error": "Missing required fields: emotion, intensity"}), 400
    
    try:
        # Log the mood
        mood_result = log_mood(
            session,
            primary_emotion=data['emotion'],
            emotion_intensity=data['intensity'],
            triggers=data.get('triggers'),
            thoughts=data.get('thoughts')
        )
        
        # Get coping skill recommendation if intensity is high
        recommendation = None
        if data['intensity'] >= 7:
            rec_result = recommend_coping_skill(
                session,
                situation=data.get('situation', 'high_intensity_emotion'),
                current_emotion=data['emotion'],
                intensity=data['intensity']
            )
            if rec_result.get('success'):
                recommendation = rec_result.get('recommended_skill')
        
        return jsonify({
            "success": True,
            "mood_logged": mood_result.get('success', False),
            "recommendation": recommendation,
            "message": "Check-in completed successfully"
        })
        
    except Exception as e:
        return jsonify({"error": str(e), "success": False}), 400

@cbt_bp.route('/api/emergency-coping', methods=['POST'])
@login_required
def api_emergency_coping():
    """Emergency coping skill recommendations"""
    data = request.get_json()
    
    # Get grounding and immediate relief skills
    emergency_skills = get_coping_skills(session, category='grounding')
    relaxation_skills = get_coping_skills(session, category='relaxation')
    
    # Filter for quick, easy skills
    immediate_help = []
    for skill in emergency_skills + relaxation_skills:
        if skill.get('difficulty_level', 5) <= 2 and skill.get('duration_minutes', 30) <= 10:
            immediate_help.append(skill)
    
    # Sort by effectiveness
    immediate_help.sort(key=lambda x: -x.get('average_effectiveness', 0))
    
    return jsonify({
        "success": True,
        "emergency_skills": immediate_help[:3],
        "crisis_message": "Remember: This feeling will pass. You are safe. Take it one moment at a time.",
        "additional_help": "If you're having thoughts of self-harm, please contact emergency services or a crisis hotline immediately."
    })

# Error handlers
@cbt_bp.errorhandler(404)
def not_found(error):
    return render_template('cbt/error.html', 
                         error_message="Page not found",
                         error_code=404), 404

@cbt_bp.errorhandler(500)
def internal_error(error):
    return render_template('cbt/error.html', 
                         error_message="Internal server error",
                         error_code=500), 500