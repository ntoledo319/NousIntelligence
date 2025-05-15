import os
import logging
import requests
import json
from flask import session
from datetime import datetime
from models import db, DBTCrisisResource

# Crisis resources management

def get_crisis_resources(session_obj, is_emergency_only=False):
    """
    Get crisis resources for the user
    
    Args:
        session_obj: Flask session object
        is_emergency_only: If True, only return emergency resources
        
    Returns:
        list: Crisis resources
    """
    try:
        user_id = session_obj.get("user_id")
        if not user_id:
            return []
        
        query = DBTCrisisResource.query.filter_by(user_id=user_id)
        
        if is_emergency_only:
            query = query.filter_by(is_emergency=True)
            
        resources = query.order_by(
            DBTCrisisResource.is_emergency.desc(),
            DBTCrisisResource.name
        ).all()
        
        if not resources:
            # If no resources yet, create some defaults
            create_default_crisis_resources(session_obj)
            
            # Query again
            query = DBTCrisisResource.query.filter_by(user_id=user_id)
            if is_emergency_only:
                query = query.filter_by(is_emergency=True)
                
            resources = query.order_by(
                DBTCrisisResource.is_emergency.desc(),
                DBTCrisisResource.name
            ).all()
        
        return [resource.to_dict() for resource in resources]
        
    except Exception as e:
        logging.error(f"Error getting crisis resources: {str(e)}")
        return []


def add_crisis_resource(session_obj, name, contact_info, resource_type, notes=None, is_emergency=False):
    """
    Add a new crisis resource
    
    Args:
        session_obj: Flask session object
        name: Resource name
        contact_info: Contact information (phone, url, etc)
        resource_type: Type of resource (hotline, therapist, hospital, etc)
        notes: Additional notes
        is_emergency: Whether this is an emergency resource
        
    Returns:
        dict: Status of the operation
    """
    try:
        user_id = session_obj.get("user_id")
        if not user_id:
            return {"status": "error", "message": "User not logged in"}
            
        # Create new resource
        resource = DBTCrisisResource()
        resource.user_id = user_id
        resource.name = name
        resource.contact_info = contact_info
        resource.resource_type = resource_type
        resource.notes = notes
        resource.is_emergency = is_emergency
        resource.created_at = datetime.utcnow()
        
        db.session.add(resource)
        db.session.commit()
        
        return {
            "status": "success", 
            "message": f"Crisis resource '{name}' added successfully",
            "id": resource.id
        }
        
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error adding crisis resource: {str(e)}")
        return {"status": "error", "message": f"Error adding resource: {str(e)}"}


def update_crisis_resource(session_obj, resource_id, name=None, contact_info=None, 
                          resource_type=None, notes=None, is_emergency=None):
    """
    Update a crisis resource
    
    Args:
        session_obj: Flask session object
        resource_id: ID of the resource to update
        name: New name (if changing)
        contact_info: New contact info (if changing)
        resource_type: New resource type (if changing)
        notes: New notes (if changing)
        is_emergency: New emergency status (if changing)
        
    Returns:
        dict: Status of the operation
    """
    try:
        user_id = session_obj.get("user_id")
        if not user_id:
            return {"status": "error", "message": "User not logged in"}
            
        # Find the resource
        resource = DBTCrisisResource.query.filter_by(
            id=resource_id,
            user_id=user_id
        ).first()
        
        if not resource:
            return {"status": "error", "message": "Crisis resource not found"}
            
        # Update fields if provided
        if name is not None:
            resource.name = name
            
        if contact_info is not None:
            resource.contact_info = contact_info
            
        if resource_type is not None:
            resource.resource_type = resource_type
            
        if notes is not None:
            resource.notes = notes
            
        if is_emergency is not None:
            resource.is_emergency = is_emergency
            
        db.session.commit()
        
        return {
            "status": "success", 
            "message": f"Crisis resource updated successfully"
        }
        
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error updating crisis resource: {str(e)}")
        return {"status": "error", "message": f"Error updating resource: {str(e)}"}


def delete_crisis_resource(session_obj, resource_id):
    """
    Delete a crisis resource
    
    Args:
        session_obj: Flask session object
        resource_id: ID of the resource to delete
        
    Returns:
        dict: Status of the operation
    """
    try:
        user_id = session_obj.get("user_id")
        if not user_id:
            return {"status": "error", "message": "User not logged in"}
            
        # Find the resource
        resource = DBTCrisisResource.query.filter_by(
            id=resource_id,
            user_id=user_id
        ).first()
        
        if not resource:
            return {"status": "error", "message": "Crisis resource not found"}
            
        # Delete the resource
        db.session.delete(resource)
        db.session.commit()
        
        return {
            "status": "success", 
            "message": f"Crisis resource '{resource.name}' deleted"
        }
        
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error deleting crisis resource: {str(e)}")
        return {"status": "error", "message": f"Error deleting resource: {str(e)}"}


def create_default_crisis_resources(session_obj):
    """
    Create default crisis resources for a new user
    
    Args:
        session_obj: Flask session object
        
    Returns:
        int: Number of resources created
    """
    try:
        user_id = session_obj.get("user_id")
        if not user_id:
            return 0
            
        # Check if user already has resources
        existing = DBTCrisisResource.query.filter_by(user_id=user_id).count()
        if existing > 0:
            return 0  # Don't create defaults if user already has resources
            
        # Default crisis resources
        default_resources = [
            {
                "name": "National Suicide Prevention Lifeline",
                "contact_info": "988 or 1-800-273-8255",
                "resource_type": "hotline",
                "notes": "Available 24/7 for everyone",
                "is_emergency": True
            },
            {
                "name": "Crisis Text Line",
                "contact_info": "Text HOME to 741741",
                "resource_type": "text hotline",
                "notes": "Free 24/7 support for those in crisis",
                "is_emergency": True
            },
            {
                "name": "SAMHSA National Helpline",
                "contact_info": "1-800-662-4357",
                "resource_type": "helpline",
                "notes": "Treatment referral and information service for individuals facing mental health or substance use disorders",
                "is_emergency": False
            },
            {
                "name": "Local Emergency Services",
                "contact_info": "911",
                "resource_type": "emergency",
                "notes": "Call for immediate life-threatening emergencies",
                "is_emergency": True
            }
        ]
        
        # Create each resource
        created_count = 0
        for resource_data in default_resources:
            resource = DBTCrisisResource()
            resource.user_id = user_id
            resource.name = resource_data["name"]
            resource.contact_info = resource_data["contact_info"]
            resource.resource_type = resource_data["resource_type"]
            resource.notes = resource_data["notes"]
            resource.is_emergency = resource_data["is_emergency"]
            resource.created_at = datetime.utcnow()
            
            db.session.add(resource)
            created_count += 1
            
        db.session.commit()
        return created_count
        
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error creating default crisis resources: {str(e)}")
        return 0


# Crisis plan generation

def generate_crisis_plan(session_obj, crisis_type=None):
    """
    Generate a personalized crisis plan based on user resources
    
    Args:
        session_obj: Flask session object
        crisis_type: Optional specific crisis type
        
    Returns:
        dict: Generated crisis plan
    """
    try:
        # Get user's crisis resources
        resources = get_crisis_resources(session_obj)
        
        # Format resources for the prompt
        resources_text = ""
        for i, resource in enumerate(resources):
            resources_text += f"{i+1}. {resource['name']} ({resource['resource_type']}): {resource['contact_info']}\n"
        
        crisis_context = f" for {crisis_type}" if crisis_type else ""
        
        # Generate crisis plan with AI
        from utils.dbt_helper import call_router_direct
        
        prompt = f"""
        Create a step-by-step personal crisis plan{crisis_context} that includes:

        1. A brief introduction about the purpose of this plan (2-3 sentences)
        2. The step-by-step crisis protocol:
           - Step 1: Immediate safety measures and grounding techniques
           - Step 2: Accessing distress tolerance skills
           - Step 3: Who to contact for help, including specific usage of these resources:
             {resources_text}
           - Step 4: Professional help escalation if needed
           - Step 5: Follow-up self-care after the crisis
        3. Reminders of personal strengths and reasons for living
        
        Format the response in clear, compassionate language with clear section headers and bullet points.
        The plan should be personalized, specific, and actionable.
        """
        
        response = call_router_direct(prompt)
        
        if not response:
            return {"status": "error", "message": "Could not generate crisis plan"}
            
        return {
            "status": "success",
            "plan": response,
            "resources": resources
        }
        
    except Exception as e:
        logging.error(f"Error generating crisis plan: {str(e)}")
        return {"status": "error", "message": f"Error generating crisis plan: {str(e)}"}


# Crisis support functions

def get_grounding_exercise(trigger_type=None):
    """
    Get a grounding exercise for crisis management
    
    Args:
        trigger_type: Optional specific trigger type
        
    Returns:
        dict: Grounding exercise
    """
    try:
        from utils.dbt_helper import call_router_direct
        
        trigger_context = f" specifically for {trigger_type}" if trigger_type else ""
        
        prompt = f"""
        Create a brief, actionable grounding exercise{trigger_context} that can be used in a moment of crisis.
        
        Include:
        1. A title for the exercise
        2. A brief explanation (1-2 sentences)
        3. Step-by-step instructions that are very specific and clear
        4. Expected outcome
        
        Keep it under 250 words and ensure it can be done anywhere with no special equipment.
        Focus on sensory awareness, present-moment techniques, and self-soothing.
        """
        
        response = call_router_direct(prompt)
        
        if not response:
            return {"status": "error", "message": "Could not generate grounding exercise"}
            
        return {
            "status": "success",
            "exercise": response
        }
        
    except Exception as e:
        logging.error(f"Error generating grounding exercise: {str(e)}")
        return {"status": "error", "message": f"Error generating exercise: {str(e)}"}


def get_crisis_de_escalation(intensity=5, emotion=None):
    """
    Get a step-by-step de-escalation process
    
    Args:
        intensity: Crisis intensity level (1-10)
        emotion: Optional specific emotion being experienced
        
    Returns:
        dict: De-escalation steps
    """
    try:
        from utils.dbt_helper import call_router_direct
        
        emotion_context = f" for intense {emotion}" if emotion else ""
        
        prompt = f"""
        Create a step-by-step crisis de-escalation process{emotion_context} for someone experiencing a level {intensity}/10 emotional crisis.
        
        The steps should:
        1. Start with immediate physical safety measures
        2. Include DBT-based interventions appropriate for the intensity level
        3. Provide very specific actions, not just general advice
        4. End with next steps after the crisis subsides
        
        Format as numbered steps with clear, compassionate directions written in second person ("you").
        Each step should be 1-2 sentences maximum for readability during crisis.
        """
        
        response = call_router_direct(prompt)
        
        if not response:
            return {"status": "error", "message": "Could not generate de-escalation steps"}
            
        return {
            "status": "success",
            "steps": response,
            "intensity": intensity
        }
        
    except Exception as e:
        logging.error(f"Error generating de-escalation steps: {str(e)}")
        return {"status": "error", "message": f"Error generating steps: {str(e)}"}