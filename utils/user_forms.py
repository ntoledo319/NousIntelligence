"""
Comprehensive User Forms and Validation
Handles all user-related forms, validation, and data processing
"""

from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
import re
import logging
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, EmailField, SelectField, BooleanField, TextAreaField, FieldList, FormField
from wtforms.validators import DataRequired, Length, Email, EqualTo, Optional as OptionalValidator, ValidationError
from wtforms.widgets import TextArea, Select
from models.user import User
from models.setup_models import UserPreferences

logger = logging.getLogger(__name__)

class CustomValidators:
    """Custom validation functions for user forms"""
    
    @staticmethod
    def validate_username(form, field):
        """Validate username format and uniqueness"""
        username = field.data
        if not username:
            return
        
        # Check format
        if not re.match(r'^[a-zA-Z0-9_-]+$', username):
            raise ValidationError('Username can only contain letters, numbers, hyphens, and underscores')
        
        # Check length
        if len(username) < 2:
            raise ValidationError('Username must be at least 2 characters long')
        if len(username) > 80:
            raise ValidationError('Username must be less than 80 characters')
        
        # Check uniqueness (exclude current user if editing)
        existing_user = User.query.filter_by(username=username).first()
        if existing_user and str(existing_user.id) != str(getattr(form, '_user_id', None)):
            raise ValidationError('This username is already taken')
    
    @staticmethod
    def validate_email_unique(form, field):
        """Validate email uniqueness"""
        email = field.data
        if not email:
            return
        
        # Check uniqueness (exclude current user if editing)
        existing_user = User.query.filter_by(email=email).first()
        if existing_user and str(existing_user.id) != str(getattr(form, '_user_id', None)):
            raise ValidationError('This email address is already registered')
    
    @staticmethod
    def validate_strong_password(form, field):
        """Validate password strength"""
        password = field.data
        if not password:
            return
        
        errors = []
        
        if len(password) < 8:
            errors.append('Password must be at least 8 characters long')
        
        if not re.search(r'[A-Z]', password):
            errors.append('Password must contain at least one uppercase letter')
        
        if not re.search(r'[a-z]', password):
            errors.append('Password must contain at least one lowercase letter')
        
        if not re.search(r'\d', password):
            errors.append('Password must contain at least one number')
        
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            errors.append('Password must contain at least one special character')
        
        if errors:
            raise ValidationError(' '.join(errors))
    
    @staticmethod
    def validate_language_code(form, field):
        """Validate language code format"""
        language_code = field.data
        if not language_code:
            return
        
        valid_codes = [
            'en-US', 'en-GB', 'es-ES', 'es-MX', 'fr-FR', 'de-DE', 
            'it-IT', 'pt-BR', 'pt-PT', 'ja-JP', 'ko-KR', 'zh-CN', 
            'zh-TW', 'ru-RU', 'ar-SA', 'hi-IN'
        ]
        
        if language_code not in valid_codes:
            raise ValidationError('Invalid language code')

class UserRegistrationForm(FlaskForm):
    """User registration form with comprehensive validation"""
    
    username = StringField('Username', 
        validators=[DataRequired(), Length(min=2, max=80), CustomValidators.validate_username])
    
    email = EmailField('Email Address', 
        validators=[DataRequired(), Email(), CustomValidators.validate_email_unique])
    
    password = PasswordField('Password', 
        validators=[DataRequired(), CustomValidators.validate_strong_password])
    
    confirm_password = PasswordField('Confirm Password', 
        validators=[DataRequired(), EqualTo('password', message='Passwords must match')])
    
    agree_terms = BooleanField('I agree to the Terms of Service and Privacy Policy', 
        validators=[DataRequired()])
    
    newsletter_opt_in = BooleanField('Subscribe to wellness tips and updates', default=True)

class UserProfileForm(FlaskForm):
    """User profile editing form"""
    
    username = StringField('Username', 
        validators=[DataRequired(), Length(min=2, max=80), CustomValidators.validate_username])
    
    email = EmailField('Email Address', 
        validators=[DataRequired(), Email(), CustomValidators.validate_email_unique])
    
    display_name = StringField('Display Name', 
        validators=[OptionalValidator(), Length(max=100)])
    
    bio = TextAreaField('Bio', 
        validators=[OptionalValidator(), Length(max=500)],
        render_kw={"rows": 4, "placeholder": "Tell us a bit about yourself..."})
    
    def __init__(self, user_id=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._user_id = user_id

class UserPreferencesForm(FlaskForm):
    """Comprehensive user preferences form"""
    
    # Language preferences
    primary_language = SelectField('Primary Language', 
        choices=[
            ('en-US', 'English (US)'),
            ('en-GB', 'English (UK)'),
            ('es-ES', 'Spanish (Spain)'),
            ('es-MX', 'Spanish (Mexico)'),
            ('fr-FR', 'French'),
            ('de-DE', 'German'),
            ('it-IT', 'Italian'),
            ('pt-BR', 'Portuguese (Brazil)'),
            ('ja-JP', 'Japanese'),
            ('ko-KR', 'Korean'),
            ('zh-CN', 'Chinese (Simplified)'),
            ('ru-RU', 'Russian'),
            ('ar-SA', 'Arabic'),
            ('hi-IN', 'Hindi')
        ],
        default='en-US',
        validators=[DataRequired(), CustomValidators.validate_language_code])
    
    secondary_languages = SelectField('Secondary Languages', 
        choices=[
            ('', 'None'),
            ('en-US', 'English (US)'),
            ('es-ES', 'Spanish'),
            ('fr-FR', 'French'),
            ('de-DE', 'German'),
            ('it-IT', 'Italian'),
            ('pt-BR', 'Portuguese'),
            ('ja-JP', 'Japanese'),
            ('zh-CN', 'Chinese'),
            ('ru-RU', 'Russian')
        ],
        validators=[OptionalValidator()])
    
    # Accessibility and neurodivergent support
    is_neurodivergent = BooleanField('I identify as neurodivergent')
    
    neurodivergent_conditions = SelectField('Neurodivergent Conditions', 
        choices=[
            ('', 'None/Prefer not to say'),
            ('adhd', 'ADHD'),
            ('autism', 'Autism Spectrum'),
            ('dyslexia', 'Dyslexia'),
            ('dyspraxia', 'Dyspraxia'),
            ('tourettes', 'Tourette Syndrome'),
            ('other', 'Other')
        ],
        validators=[OptionalValidator()])
    
    # Theme and interface preferences
    theme_preference = SelectField('Theme Preference', 
        choices=[
            ('auto', 'Auto (system)'),
            ('light', 'Light'),
            ('dark', 'Dark'),
            ('high-contrast', 'High Contrast')
        ],
        default='auto',
        validators=[DataRequired()])
    
    color_scheme = SelectField('Color Scheme', 
        choices=[
            ('blue', 'Blue'),
            ('green', 'Green'),
            ('purple', 'Purple'),
            ('orange', 'Orange'),
            ('red', 'Red'),
            ('neutral', 'Neutral')
        ],
        default='blue',
        validators=[DataRequired()])
    
    font_size = SelectField('Font Size', 
        choices=[
            ('small', 'Small'),
            ('medium', 'Medium'),
            ('large', 'Large'),
            ('extra-large', 'Extra Large')
        ],
        default='medium',
        validators=[DataRequired()])
    
    high_contrast = BooleanField('Enable high contrast mode')
    
    # Mental health and therapeutic preferences
    therapeutic_approach = SelectField('Therapeutic Approach', 
        choices=[
            ('integrated', 'Integrated (DBT + CBT + AA)'),
            ('dbt', 'DBT (Dialectical Behavior Therapy)'),
            ('cbt', 'CBT (Cognitive Behavioral Therapy)'),
            ('aa', 'AA (Alcoholics Anonymous) Recovery'),
            ('custom', 'Custom Approach')
        ],
        default='integrated',
        validators=[DataRequired()])
    
    mental_health_goals = TextAreaField('Mental Health Goals', 
        validators=[OptionalValidator(), Length(max=1000)],
        render_kw={"rows": 3, "placeholder": "What are your mental health and wellness goals?"})
    
    crisis_support_enabled = BooleanField('Enable crisis support resources', default=True)
    
    # AI Assistant preferences
    assistant_personality = SelectField('AI Assistant Personality', 
        choices=[
            ('empathetic', 'Empathetic and Supportive'),
            ('professional', 'Professional and Clinical'),
            ('casual', 'Casual and Friendly'),
            ('motivational', 'Motivational and Encouraging'),
            ('analytical', 'Analytical and Objective')
        ],
        default='empathetic',
        validators=[DataRequired()])
    
    assistant_tone = SelectField('AI Assistant Tone', 
        choices=[
            ('compassionate', 'Compassionate'),
            ('encouraging', 'Encouraging'),
            ('neutral', 'Neutral'),
            ('direct', 'Direct'),
            ('gentle', 'Gentle')
        ],
        default='compassionate',
        validators=[DataRequired()])
    
    communication_style = SelectField('Communication Style', 
        choices=[
            ('balanced', 'Balanced'),
            ('detailed', 'Detailed explanations'),
            ('concise', 'Brief and concise'),
            ('interactive', 'Interactive and engaging'),
            ('structured', 'Structured and organized')
        ],
        default='balanced',
        validators=[DataRequired()])
    
    ai_assistance_level = SelectField('AI Assistance Level', 
        choices=[
            ('minimal', 'Minimal - Basic responses only'),
            ('responsive', 'Responsive - Answer when asked'),
            ('proactive', 'Proactive - Offer suggestions'),
            ('comprehensive', 'Comprehensive - Full guidance')
        ],
        default='responsive',
        validators=[DataRequired()])
    
    # Health and wellness preferences
    health_tracking_interests = TextAreaField('Health Tracking Interests', 
        validators=[OptionalValidator(), Length(max=500)],
        render_kw={"rows": 2, "placeholder": "What health metrics would you like to track?"})
    
    wellness_goals = TextAreaField('Wellness Goals', 
        validators=[OptionalValidator(), Length(max=500)],
        render_kw={"rows": 2, "placeholder": "What are your wellness and self-care goals?"})
    
    # Notification preferences
    notification_frequency = SelectField('Notification Frequency', 
        choices=[
            ('none', 'None'),
            ('low', 'Low (critical only)'),
            ('medium', 'Medium (daily summaries)'),
            ('high', 'High (real-time updates)')
        ],
        default='medium',
        validators=[DataRequired()])
    
    # Privacy preferences
    data_privacy_level = SelectField('Data Privacy Level', 
        choices=[
            ('minimal', 'Minimal - Basic functionality only'),
            ('standard', 'Standard - Normal features'),
            ('full', 'Full - All features enabled'),
            ('maximum', 'Maximum - Enhanced analytics')
        ],
        default='full',
        validators=[DataRequired()])
    
    # Voice interface preferences
    voice_interface_enabled = BooleanField('Enable voice interface', default=True)
    
    voice_interface_mode = SelectField('Voice Interface Mode', 
        choices=[
            ('push-to-talk', 'Push to talk'),
            ('voice-activation', 'Voice activation'),
            ('continuous', 'Continuous listening'),
            ('disabled', 'Disabled')
        ],
        default='push-to-talk',
        validators=[DataRequired()])
    
    # Emergency and safety
    emergency_contacts = TextAreaField('Emergency Contacts', 
        validators=[OptionalValidator(), Length(max=1000)],
        render_kw={"rows": 3, "placeholder": "Emergency contact information (names, phone numbers, relationships)"})
    
    safety_planning_enabled = BooleanField('Enable safety planning features', default=True)
    location_services_enabled = BooleanField('Enable location services for emergency support')
    
    # Integration preferences
    google_services_enabled = BooleanField('Enable Google services integration', default=True)
    spotify_integration_enabled = BooleanField('Enable Spotify integration', default=True)
    
    # Collaboration preferences
    family_features_enabled = BooleanField('Enable family/group features')
    collaboration_level = SelectField('Collaboration Level', 
        choices=[
            ('private', 'Private - Individual use only'),
            ('family', 'Family - Share with family members'),
            ('group', 'Group - Share with support group'),
            ('community', 'Community - Participate in community features')
        ],
        default='private',
        validators=[DataRequired()])

class EmergencyContactForm(FlaskForm):
    """Emergency contact information form"""
    
    name = StringField('Name', 
        validators=[DataRequired(), Length(min=2, max=100)])
    
    relationship = SelectField('Relationship', 
        choices=[
            ('family', 'Family Member'),
            ('friend', 'Friend'),
            ('partner', 'Partner/Spouse'),
            ('therapist', 'Therapist/Counselor'),
            ('doctor', 'Doctor'),
            ('emergency', 'Emergency Contact'),
            ('other', 'Other')
        ],
        validators=[DataRequired()])
    
    phone = StringField('Phone Number', 
        validators=[DataRequired(), Length(min=10, max=20)])
    
    email = EmailField('Email', 
        validators=[OptionalValidator(), Email()])
    
    notes = TextAreaField('Notes', 
        validators=[OptionalValidator(), Length(max=500)],
        render_kw={"rows": 2, "placeholder": "Additional notes about this contact"})
    
    is_primary = BooleanField('Primary emergency contact')
    is_crisis_contact = BooleanField('Crisis intervention contact')

class PasswordChangeForm(FlaskForm):
    """Password change form"""
    
    current_password = PasswordField('Current Password', 
        validators=[DataRequired()])
    
    new_password = PasswordField('New Password', 
        validators=[DataRequired(), CustomValidators.validate_strong_password])
    
    confirm_new_password = PasswordField('Confirm New Password', 
        validators=[DataRequired(), EqualTo('new_password', message='Passwords must match')])

class UserDeleteForm(FlaskForm):
    """User account deletion form"""
    
    confirmation = StringField('Type "DELETE_MY_ACCOUNT" to confirm', 
        validators=[DataRequired()])
    
    reason = SelectField('Reason for deletion', 
        choices=[
            ('', 'Prefer not to say'),
            ('not_helpful', 'Not helpful for my needs'),
            ('privacy_concerns', 'Privacy concerns'),
            ('too_complex', 'Too complex to use'),
            ('found_alternative', 'Found alternative solution'),
            ('temporary_break', 'Taking a temporary break'),
            ('other', 'Other reason')
        ],
        validators=[OptionalValidator()])
    
    feedback = TextAreaField('Additional feedback', 
        validators=[OptionalValidator(), Length(max=1000)],
        render_kw={"rows": 4, "placeholder": "Any feedback to help us improve?"})
    
    def validate_confirmation(self, field):
        if field.data != 'DELETE_MY_ACCOUNT':
            raise ValidationError('You must type "DELETE_MY_ACCOUNT" exactly to confirm account deletion')

class UserSearchForm(FlaskForm):
    """User search and filtering form"""
    
    search_query = StringField('Search', 
        validators=[OptionalValidator(), Length(max=100)],
        render_kw={"placeholder": "Search users..."})
    
    filter_active = SelectField('Status', 
        choices=[
            ('', 'All Users'),
            ('active', 'Active Users'),
            ('inactive', 'Inactive Users')
        ],
        validators=[OptionalValidator()])
    
    filter_joined_date = SelectField('Joined', 
        choices=[
            ('', 'Any time'),
            ('today', 'Today'),
            ('week', 'This week'),
            ('month', 'This month'),
            ('year', 'This year')
        ],
        validators=[OptionalValidator()])
    
    sort_by = SelectField('Sort by', 
        choices=[
            ('created_at_desc', 'Newest first'),
            ('created_at_asc', 'Oldest first'),
            ('username_asc', 'Username A-Z'),
            ('username_desc', 'Username Z-A'),
            ('last_login_desc', 'Recently active'),
            ('last_login_asc', 'Least active')
        ],
        default='created_at_desc',
        validators=[DataRequired()])

class FormProcessor:
    """Process and validate user forms"""
    
    @staticmethod
    def process_registration_form(form: UserRegistrationForm) -> Tuple[bool, Dict[str, Any], List[str]]:
        """Process user registration form"""
        if not form.validate():
            return False, {}, FormProcessor._extract_form_errors(form)
        
        user_data = {
            'username': form.username.data.strip(),
            'email': form.email.data.strip().lower(),
            'password': form.password.data,
            'newsletter_opt_in': form.newsletter_opt_in.data,
            'agreed_to_terms': form.agree_terms.data,
            'registration_date': datetime.utcnow().isoformat()
        }
        
        return True, user_data, []
    
    @staticmethod
    def process_profile_form(form: UserProfileForm) -> Tuple[bool, Dict[str, Any], List[str]]:
        """Process user profile form"""
        if not form.validate():
            return False, {}, FormProcessor._extract_form_errors(form)
        
        profile_data = {
            'username': form.username.data.strip(),
            'email': form.email.data.strip().lower(),
            'display_name': form.display_name.data.strip() if form.display_name.data else None,
            'bio': form.bio.data.strip() if form.bio.data else None,
            'updated_at': datetime.utcnow().isoformat()
        }
        
        return True, profile_data, []
    
    @staticmethod
    def process_preferences_form(form: UserPreferencesForm) -> Tuple[bool, Dict[str, Any], List[str]]:
        """Process user preferences form"""
        if not form.validate():
            return False, {}, FormProcessor._extract_form_errors(form)
        
        preferences_data = {
            # Language preferences
            'primary_language': form.primary_language.data,
            'secondary_languages': [form.secondary_languages.data] if form.secondary_languages.data else [],
            
            # Accessibility
            'is_neurodivergent': form.is_neurodivergent.data,
            'neurodivergent_conditions': [form.neurodivergent_conditions.data] if form.neurodivergent_conditions.data else [],
            
            # Interface preferences
            'theme_preference': form.theme_preference.data,
            'color_scheme': form.color_scheme.data,
            'font_size': form.font_size.data,
            'high_contrast': form.high_contrast.data,
            
            # Therapeutic preferences
            'therapeutic_approach': form.therapeutic_approach.data,
            'mental_health_goals': [goal.strip() for goal in form.mental_health_goals.data.split('\n') if goal.strip()] if form.mental_health_goals.data else [],
            'crisis_support_enabled': form.crisis_support_enabled.data,
            
            # AI Assistant preferences
            'assistant_personality': form.assistant_personality.data,
            'assistant_tone': form.assistant_tone.data,
            'communication_style': form.communication_style.data,
            'ai_assistance_level': form.ai_assistance_level.data,
            
            # Health and wellness
            'health_tracking_interests': [interest.strip() for interest in form.health_tracking_interests.data.split('\n') if interest.strip()] if form.health_tracking_interests.data else [],
            'wellness_goals': [goal.strip() for goal in form.wellness_goals.data.split('\n') if goal.strip()] if form.wellness_goals.data else [],
            
            # Notifications and privacy
            'notification_frequency': form.notification_frequency.data,
            'data_privacy_level': form.data_privacy_level.data,
            
            # Voice interface
            'voice_interface_enabled': form.voice_interface_enabled.data,
            'voice_interface_mode': form.voice_interface_mode.data,
            
            # Emergency and safety
            'emergency_contacts': FormProcessor._parse_emergency_contacts(form.emergency_contacts.data),
            'safety_planning_enabled': form.safety_planning_enabled.data,
            'location_services_enabled': form.location_services_enabled.data,
            
            # Integrations
            'google_services_integration': {'enabled': form.google_services_enabled.data},
            'spotify_integration_enabled': form.spotify_integration_enabled.data,
            
            # Collaboration
            'family_features_enabled': form.family_features_enabled.data,
            'collaboration_level': form.collaboration_level.data,
            
            'updated_at': datetime.utcnow().isoformat()
        }
        
        return True, preferences_data, []
    
    @staticmethod
    def process_emergency_contact_form(form: EmergencyContactForm) -> Tuple[bool, Dict[str, Any], List[str]]:
        """Process emergency contact form"""
        if not form.validate():
            return False, {}, FormProcessor._extract_form_errors(form)
        
        contact_data = {
            'name': form.name.data.strip(),
            'relationship': form.relationship.data,
            'phone': form.phone.data.strip(),
            'email': form.email.data.strip().lower() if form.email.data else None,
            'notes': form.notes.data.strip() if form.notes.data else None,
            'is_primary': form.is_primary.data,
            'is_crisis_contact': form.is_crisis_contact.data,
            'created_at': datetime.utcnow().isoformat()
        }
        
        return True, contact_data, []
    
    @staticmethod
    def _extract_form_errors(form: FlaskForm) -> List[str]:
        """Extract all form validation errors"""
        errors = []
        for field_name, field_errors in form.errors.items():
            for error in field_errors:
                errors.append(f"{field_name}: {error}")
        return errors
    
    @staticmethod
    def _parse_emergency_contacts(contacts_text: str) -> List[Dict[str, str]]:
        """Parse emergency contacts from text area"""
        if not contacts_text:
            return []
        
        contacts = []
        lines = [line.strip() for line in contacts_text.split('\n') if line.strip()]
        
        for line in lines:
            # Simple parsing - each line should be "Name: Phone (Relationship)"
            parts = line.split(':')
            if len(parts) >= 2:
                name = parts[0].strip()
                rest = ':'.join(parts[1:]).strip()
                
                # Extract phone number
                phone_match = re.search(r'[\d\-\(\)\+\s]+', rest)
                phone = phone_match.group().strip() if phone_match else ''
                
                # Extract relationship (in parentheses)
                relationship_match = re.search(r'\(([^)]+)\)', rest)
                relationship = relationship_match.group(1).strip() if relationship_match else 'emergency'
                
                if name and phone:
                    contacts.append({
                        'name': name,
                        'phone': phone,
                        'relationship': relationship
                    })
        
        return contacts