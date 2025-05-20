"""
Google Forms Helper Module

Provides utilities for working with Google Forms, including
form creation, response handling, and analysis.
"""

import os
import logging
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from utils.ai_helper import generate_ai_text, analyze_document_content

def get_forms_service(user_connection):
    """
    Build and return a Google Forms service object from user connection data
    
    Args:
        user_connection: User connection object with OAuth credentials
        
    Returns:
        Forms service object or None
    """
    try:
        # Create credentials from stored tokens
        creds = Credentials(
            token=user_connection.token,
            refresh_token=user_connection.refresh_token,
            token_uri=user_connection.token_uri,
            client_id=user_connection.client_id,
            client_secret=user_connection.client_secret,
            scopes=user_connection.scopes.split(",") if user_connection.scopes else []
        )
        
        # Build the Forms service
        service = build('forms', 'v1', credentials=creds)
        return service
    except Exception as e:
        logging.error(f"Error building Forms service: {str(e)}")
        return None

def create_form(forms_service, title, description=None):
    """
    Create a new Google Form
    
    Args:
        forms_service: Authorized Google Forms service
        title: Form title
        description: Form description (optional)
        
    Returns:
        Form ID and URL
    """
    try:
        # Create form info
        form = {
            'info': {
                'title': title,
                'documentTitle': title
            }
        }
        
        if description:
            form['info']['description'] = description
            
        # Create the form
        result = forms_service.forms().create(body=form).execute()
        
        return {
            'form_id': result['formId'],
            'url': f"https://docs.google.com/forms/d/{result['formId']}/edit"
        }
        
    except Exception as e:
        logging.error(f"Error creating form: {str(e)}")
        return {'error': str(e)}

def get_form(forms_service, form_id):
    """
    Get a Google Form by ID
    
    Args:
        forms_service: Authorized Google Forms service
        form_id: Form ID
        
    Returns:
        Form data
    """
    try:
        form = forms_service.forms().get(formId=form_id).execute()
        return form
    except Exception as e:
        logging.error(f"Error getting form: {str(e)}")
        return {'error': str(e)}

def add_text_item(forms_service, form_id, title, description=None, required=False):
    """
    Add a text item to a Google Form
    
    Args:
        forms_service: Authorized Google Forms service
        form_id: Form ID
        title: Question title
        description: Question description (optional)
        required: Whether the question is required
        
    Returns:
        Updated form
    """
    try:
        # Create request to add a text item
        request = {
            'requests': [
                {
                    'createItem': {
                        'item': {
                            'title': title,
                            'description': description if description else '',
                            'questionItem': {
                                'question': {
                                    'required': required,
                                    'textQuestion': {}
                                }
                            }
                        },
                        'location': {
                            'index': 0
                        }
                    }
                }
            ]
        }
        
        # Execute the request
        result = forms_service.forms().batchUpdate(formId=form_id, body=request).execute()
        
        return result
    except Exception as e:
        logging.error(f"Error adding text item: {str(e)}")
        return {'error': str(e)}

def add_multiple_choice_item(forms_service, form_id, title, options, description=None, required=False):
    """
    Add a multiple choice item to a Google Form
    
    Args:
        forms_service: Authorized Google Forms service
        form_id: Form ID
        title: Question title
        options: List of options
        description: Question description (optional)
        required: Whether the question is required
        
    Returns:
        Updated form
    """
    try:
        # Create options for the multiple choice item
        choices = [{'value': option} for option in options]
        
        # Create request to add a multiple choice item
        request = {
            'requests': [
                {
                    'createItem': {
                        'item': {
                            'title': title,
                            'description': description if description else '',
                            'questionItem': {
                                'question': {
                                    'required': required,
                                    'choiceQuestion': {
                                        'type': 'RADIO',
                                        'options': choices,
                                        'shuffle': False
                                    }
                                }
                            }
                        },
                        'location': {
                            'index': 0
                        }
                    }
                }
            ]
        }
        
        # Execute the request
        result = forms_service.forms().batchUpdate(formId=form_id, body=request).execute()
        
        return result
    except Exception as e:
        logging.error(f"Error adding multiple choice item: {str(e)}")
        return {'error': str(e)}

def get_form_responses(forms_service, form_id):
    """
    Get responses for a Google Form
    
    Args:
        forms_service: Authorized Google Forms service
        form_id: Form ID
        
    Returns:
        Form responses
    """
    try:
        responses = forms_service.forms().responses().list(formId=form_id).execute()
        return responses
    except Exception as e:
        logging.error(f"Error getting form responses: {str(e)}")
        return {'error': str(e)}

def analyze_form_responses(forms_service, form_id):
    """
    Analyze responses for a Google Form using AI
    
    Args:
        forms_service: Authorized Google Forms service
        form_id: Form ID
        
    Returns:
        Analysis of form responses
    """
    try:
        # Get form responses
        responses = get_form_responses(forms_service, form_id)
        
        if 'error' in responses:
            return responses
            
        # Get form details to understand the questions
        form = get_form(forms_service, form_id)
        
        if 'error' in form:
            return form
            
        # Prepare data for analysis
        response_data = {
            'form_title': form.get('info', {}).get('title', 'Unknown Form'),
            'question_count': len(form.get('items', [])),
            'response_count': len(responses.get('responses', [])),
            'responses': responses.get('responses', [])
        }
        
        # Use AI to analyze the responses
        analysis_prompt = f"Analyze the following form responses:\n{response_data}\n\nProvide insights on patterns, common responses, and any notable findings:"
        analysis = generate_ai_text(analysis_prompt)
        
        return {
            'form_id': form_id,
            'form_title': response_data['form_title'],
            'response_count': response_data['response_count'],
            'analysis': analysis
        }
        
    except Exception as e:
        logging.error(f"Error analyzing form responses: {str(e)}")
        return {'error': str(e)}

def create_recovery_assessment_form(forms_service, assessment_type="general"):
    """
    Create a recovery assessment form with appropriate questions
    
    Args:
        forms_service: Authorized Google Forms service
        assessment_type: Type of assessment (general, mood, coping, etc.)
        
    Returns:
        Form ID and URL
    """
    try:
        # Create basic form
        title = f"Recovery Assessment - {assessment_type.capitalize()}"
        description = "Please complete this assessment to help track your recovery progress."
        
        form_result = create_form(forms_service, title, description)
        
        if 'error' in form_result:
            return form_result
            
        form_id = form_result['form_id']
        
        # Add appropriate questions based on assessment type
        if assessment_type == "general":
            add_multiple_choice_item(
                forms_service, 
                form_id, 
                "How would you rate your overall well-being today?",
                ["1 - Very poor", "2 - Poor", "3 - Fair", "4 - Good", "5 - Excellent"],
                required=True
            )
            
            add_text_item(
                forms_service,
                form_id,
                "What challenges have you faced since your last check-in?",
                required=False
            )
            
            add_multiple_choice_item(
                forms_service,
                form_id,
                "Have you maintained your sobriety since your last check-in?",
                ["Yes", "No"],
                "Please answer honestly. This information is confidential.",
                required=True
            )
            
            add_text_item(
                forms_service,
                form_id,
                "What coping strategies have been most effective for you recently?",
                required=False
            )
            
        elif assessment_type == "mood":
            add_multiple_choice_item(
                forms_service,
                form_id,
                "How would you rate your mood today?",
                ["1 - Very negative", "2 - Somewhat negative", "3 - Neutral", "4 - Somewhat positive", "5 - Very positive"],
                required=True
            )
            
            add_multiple_choice_item(
                forms_service,
                form_id,
                "Have you experienced any intense emotional episodes since your last check-in?",
                ["None", "1-2 minor episodes", "Several minor episodes", "1-2 major episodes", "Several major episodes"],
                required=True
            )
            
            add_text_item(
                forms_service,
                form_id,
                "What factors do you think contributed to your mood today?",
                required=False
            )
            
        elif assessment_type == "coping":
            add_multiple_choice_item(
                forms_service,
                form_id,
                "How effectively have you been using your coping skills?",
                ["1 - Not at all", "2 - Slightly", "3 - Moderately", "4 - Very", "5 - Extremely"],
                required=True
            )
            
            add_multiple_choice_item(
                forms_service,
                form_id,
                "Which coping skills have you used recently?",
                ["Mindfulness", "Distress tolerance", "Emotional regulation", "Interpersonal effectiveness", "Cognitive reframing", "Other"],
                "Select all that apply",
                required=True
            )
            
            add_text_item(
                forms_service,
                form_id,
                "Describe a situation where you successfully applied a coping skill:",
                required=False
            )
            
        return form_result
        
    except Exception as e:
        logging.error(f"Error creating recovery assessment form: {str(e)}")
        return {'error': str(e)}

def create_anonymous_sharing_form(forms_service, group_type="support"):
    """
    Create an anonymous sharing form for group therapy
    
    Args:
        forms_service: Authorized Google Forms service
        group_type: Type of group (support, AA, DBT, etc.)
        
    Returns:
        Form ID and URL
    """
    try:
        # Create basic form
        title = f"Anonymous Sharing - {group_type.capitalize()} Group"
        description = "This form allows you to share experiences anonymously with your group. No identifying information will be collected."
        
        form_result = create_form(forms_service, title, description)
        
        if 'error' in form_result:
            return form_result
            
        form_id = form_result['form_id']
        
        # Add sharing questions
        add_text_item(
            forms_service,
            form_id,
            "What would you like to share with the group?",
            "Your response will be shared anonymously during the next session.",
            required=True
        )
        
        add_multiple_choice_item(
            forms_service,
            form_id,
            "Would you like the facilitator to discuss this topic in the next session?",
            ["Yes", "No", "Either way is fine"],
            required=True
        )
        
        add_multiple_choice_item(
            forms_service,
            form_id,
            "How are you feeling about sharing this?",
            ["Nervous", "Relieved", "Uncertain", "Hopeful", "Other"],
            required=False
        )
        
        return form_result
        
    except Exception as e:
        logging.error(f"Error creating anonymous sharing form: {str(e)}")
        return {'error': str(e)}

def create_daily_check_in_form(forms_service, recovery_type="general"):
    """
    Create a daily check-in form for recovery
    
    Args:
        forms_service: Authorized Google Forms service
        recovery_type: Type of recovery program (AA, DBT, etc.)
        
    Returns:
        Form ID and URL
    """
    try:
        # Create basic form
        title = f"Daily Check-In - {recovery_type.capitalize()} Recovery"
        description = "Complete this daily check-in to track your recovery progress."
        
        form_result = create_form(forms_service, title, description)
        
        if 'error' in form_result:
            return form_result
            
        form_id = form_result['form_id']
        
        # Add check-in questions
        add_multiple_choice_item(
            forms_service,
            form_id,
            "How would you rate today overall?",
            ["1 - Very difficult", "2 - Difficult", "3 - Neutral", "4 - Good", "5 - Excellent"],
            required=True
        )
        
        if recovery_type.lower() == "aa":
            add_multiple_choice_item(
                forms_service,
                form_id,
                "Did you maintain sobriety today?",
                ["Yes", "No"],
                "Please answer honestly. This information is confidential.",
                required=True
            )
            
            add_multiple_choice_item(
                forms_service,
                form_id,
                "Did you attend a meeting today?",
                ["Yes", "No"],
                required=True
            )
            
            add_text_item(
                forms_service,
                form_id,
                "What are you grateful for today?",
                required=False
            )
            
        elif recovery_type.lower() == "dbt":
            add_multiple_choice_item(
                forms_service,
                form_id,
                "Did you practice mindfulness today?",
                ["Yes", "No"],
                required=True
            )
            
            add_multiple_choice_item(
                forms_service,
                form_id,
                "Which DBT skills did you use today?",
                ["Mindfulness", "Distress Tolerance", "Emotion Regulation", "Interpersonal Effectiveness", "None"],
                "Select all that apply",
                required=True
            )
            
            add_text_item(
                forms_service,
                form_id,
                "Describe a situation where you used your skills effectively:",
                required=False
            )
        
        add_text_item(
            forms_service,
            form_id,
            "What's your intention for tomorrow?",
            required=False
        )
        
        return form_result
        
    except Exception as e:
        logging.error(f"Error creating daily check-in form: {str(e)}")
        return {'error': str(e)} 