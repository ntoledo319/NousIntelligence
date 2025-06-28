"""
Forms Helper - Unified Form Processing and Validation
Handles form creation, validation, processing, and data sanitization
"""

import re
import logging
from typing import Dict, Any, List, Optional, Union
from datetime import datetime, timezone
from werkzeug.security import generate_password_hash
import bleach

logger = logging.getLogger(__name__)


class FormValidator:
    """Comprehensive form validation utilities"""
    
    # Common regex patterns
    EMAIL_PATTERN = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    PHONE_PATTERN = re.compile(r'^\+?1?[-.\s]?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})$')
    URL_PATTERN = re.compile(r'^https?://(?:[-\w.])+(?:\:[0-9]+)?(?:/(?:[\w/_.])*(?:\?(?:[\w&=%.])*)?(?:\#(?:[\w.])*)?)?$')
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """Validate email address format"""
        if not email or not isinstance(email, str):
            return False
        return bool(FormValidator.EMAIL_PATTERN.match(email.strip()))
    
    @staticmethod
    def validate_phone(phone: str) -> bool:
        """Validate phone number format"""
        if not phone or not isinstance(phone, str):
            return False
        return bool(FormValidator.PHONE_PATTERN.match(phone.strip()))
    
    @staticmethod
    def validate_url(url: str) -> bool:
        """Validate URL format"""
        if not url or not isinstance(url, str):
            return False
        return bool(FormValidator.URL_PATTERN.match(url.strip()))
    
    @staticmethod
    def validate_required(value: Any) -> bool:
        """Check if required field has value"""
        if value is None:
            return False
        if isinstance(value, str):
            return bool(value.strip())
        return bool(value)
    
    @staticmethod
    def validate_length(value: str, min_length: int = 0, max_length: int = None) -> bool:
        """Validate string length"""
        if not isinstance(value, str):
            return False
        
        length = len(value.strip())
        if length < min_length:
            return False
        
        if max_length is not None and length > max_length:
            return False
        
        return True
    
    @staticmethod
    def validate_password_strength(password: str) -> Dict[str, Any]:
        """Validate password strength"""
        if not password or not isinstance(password, str):
            return {
                'valid': False,
                'score': 0,
                'issues': ['Password is required']
            }
        
        issues = []
        score = 0
        
        # Length check
        if len(password) < 8:
            issues.append('Password must be at least 8 characters long')
        else:
            score += 1
        
        # Uppercase check
        if not re.search(r'[A-Z]', password):
            issues.append('Password must contain at least one uppercase letter')
        else:
            score += 1
        
        # Lowercase check
        if not re.search(r'[a-z]', password):
            issues.append('Password must contain at least one lowercase letter')
        else:
            score += 1
        
        # Number check
        if not re.search(r'\d', password):
            issues.append('Password must contain at least one number')
        else:
            score += 1
        
        # Special character check
        if not re.search(r'[!@#$%^&*()_+\-=\[\]{};:"\\|,.<>\?]', password):
            issues.append('Password must contain at least one special character')
        else:
            score += 1
        
        return {
            'valid': len(issues) == 0,
            'score': score,
            'issues': issues,
            'strength': ['Very Weak', 'Weak', 'Fair', 'Good', 'Strong'][min(score, 4)]
        }
    
    @staticmethod
    def validate_date(date_str: str, date_format: str = '%Y-%m-%d') -> bool:
        """Validate date format"""
        if not date_str or not isinstance(date_str, str):
            return False
        
        try:
            datetime.strptime(date_str.strip(), date_format)
            return True
        except ValueError:
            return False
    
    @staticmethod
    def validate_numeric(value: Union[str, int, float], min_val: float = None, max_val: float = None) -> bool:
        """Validate numeric value"""
        try:
            num_val = float(value)
            
            if min_val is not None and num_val < min_val:
                return False
            
            if max_val is not None and num_val > max_val:
                return False
            
            return True
        except (ValueError, TypeError):
            return False


class FormSanitizer:
    """Form data sanitization utilities"""
    
    # Allowed HTML tags for rich text fields
    ALLOWED_TAGS = [
        'p', 'br', 'strong', 'em', 'u', 'ol', 'ul', 'li',
        'a', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6'
    ]
    
    ALLOWED_ATTRIBUTES = {
        'a': ['href', 'title'],
        '*': ['class']
    }
    
    @staticmethod
    def sanitize_html(html_content: str) -> str:
        """Sanitize HTML content"""
        if not html_content or not isinstance(html_content, str):
            return ''
        
        return bleach.clean(
            html_content,
            tags=FormSanitizer.ALLOWED_TAGS,
            attributes=FormSanitizer.ALLOWED_ATTRIBUTES,
            strip=True
        )
    
    @staticmethod
    def sanitize_text(text: str) -> str:
        """Sanitize plain text input"""
        if not text or not isinstance(text, str):
            return ''
        
        # Remove HTML tags and normalize whitespace
        clean_text = bleach.clean(text, tags=[], strip=True)
        return ' '.join(clean_text.split())
    
    @staticmethod
    def sanitize_email(email: str) -> str:
        """Sanitize email address"""
        if not email or not isinstance(email, str):
            return ''
        
        return email.strip().lower()
    
    @staticmethod
    def sanitize_phone(phone: str) -> str:
        """Sanitize phone number"""
        if not phone or not isinstance(phone, str):
            return ''
        
        # Remove all non-digit characters except +
        clean_phone = re.sub(r'[^\d+]', '', phone)
        return clean_phone
    
    @staticmethod
    def sanitize_url(url: str) -> str:
        """Sanitize URL"""
        if not url or not isinstance(url, str):
            return ''
        
        url = url.strip()
        
        # Add protocol if missing
        if url and not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        return url


class FormProcessor:
    """Main form processing class"""
    
    def __init__(self):
        self.validator = FormValidator()
        self.sanitizer = FormSanitizer()
    
    def process_form(self, form_data: Dict[str, Any], form_config: Dict[str, Any]) -> Dict[str, Any]:
        """Process form data with validation and sanitization"""
        result = {
            'valid': True,
            'errors': {},
            'cleaned_data': {},
            'warnings': []
        }
        
        # Process each field according to configuration
        for field_name, field_config in form_config.items():
            if field_name not in form_data:
                if field_config.get('required', False):
                    result['errors'][field_name] = 'This field is required'
                    result['valid'] = False
                continue
            
            field_value = form_data[field_name]
            
            # Sanitize the value
            cleaned_value = self._sanitize_field(field_value, field_config)
            result['cleaned_data'][field_name] = cleaned_value
            
            # Validate the cleaned value
            validation_result = self._validate_field(cleaned_value, field_config)
            
            if not validation_result['valid']:
                result['errors'][field_name] = validation_result['error']
                result['valid'] = False
            
            if validation_result.get('warnings'):
                result['warnings'].extend(validation_result['warnings'])
        
        return result
    
    def _sanitize_field(self, value: Any, config: Dict[str, Any]) -> Any:
        """Sanitize individual field value"""
        field_type = config.get('type', 'text')
        
        if field_type == 'email':
            return self.sanitizer.sanitize_email(value)
        elif field_type == 'phone':
            return self.sanitizer.sanitize_phone(value)
        elif field_type == 'url':
            return self.sanitizer.sanitize_url(value)
        elif field_type == 'html':
            return self.sanitizer.sanitize_html(value)
        elif field_type == 'password':
            return value  # Don't sanitize passwords
        else:
            return self.sanitizer.sanitize_text(value)
    
    def _validate_field(self, value: Any, config: Dict[str, Any]) -> Dict[str, Any]:
        """Validate individual field value"""
        field_type = config.get('type', 'text')
        result = {'valid': True, 'error': None, 'warnings': []}
        
        # Required validation
        if config.get('required', False) and not self.validator.validate_required(value):
            result['valid'] = False
            result['error'] = 'This field is required'
            return result
        
        # Skip other validations if field is empty and not required
        if not value and not config.get('required', False):
            return result
        
        # Type-specific validation
        if field_type == 'email':
            if not self.validator.validate_email(value):
                result['valid'] = False
                result['error'] = 'Please enter a valid email address'
        
        elif field_type == 'phone':
            if not self.validator.validate_phone(value):
                result['valid'] = False
                result['error'] = 'Please enter a valid phone number'
        
        elif field_type == 'url':
            if not self.validator.validate_url(value):
                result['valid'] = False
                result['error'] = 'Please enter a valid URL'
        
        elif field_type == 'password':
            password_result = self.validator.validate_password_strength(value)
            if not password_result['valid']:
                result['valid'] = False
                result['error'] = '; '.join(password_result['issues'])
            elif password_result['score'] < 3:
                result['warnings'].append(f"Password strength: {password_result['strength']}")
        
        elif field_type == 'date':
            date_format = config.get('format', '%Y-%m-%d')
            if not self.validator.validate_date(value, date_format):
                result['valid'] = False
                result['error'] = f'Please enter a valid date in format {date_format}'
        
        elif field_type == 'number':
            min_val = config.get('min')
            max_val = config.get('max')
            if not self.validator.validate_numeric(value, min_val, max_val):
                result['valid'] = False
                if min_val is not None and max_val is not None:
                    result['error'] = f'Please enter a number between {min_val} and {max_val}'
                elif min_val is not None:
                    result['error'] = f'Please enter a number greater than or equal to {min_val}'
                elif max_val is not None:
                    result['error'] = f'Please enter a number less than or equal to {max_val}'
                else:
                    result['error'] = 'Please enter a valid number'
        
        # Length validation
        if field_type in ['text', 'textarea', 'html']:
            min_length = config.get('min_length', 0)
            max_length = config.get('max_length')
            
            if not self.validator.validate_length(value, min_length, max_length):
                result['valid'] = False
                if max_length:
                    result['error'] = f'This field must be between {min_length} and {max_length} characters'
                else:
                    result['error'] = f'This field must be at least {min_length} characters'
        
        return result


# Common form configurations
CONTACT_FORM_CONFIG = {
    'name': {'type': 'text', 'required': True, 'max_length': 100},
    'email': {'type': 'email', 'required': True},
    'phone': {'type': 'phone', 'required': False},
    'subject': {'type': 'text', 'required': True, 'max_length': 200},
    'message': {'type': 'textarea', 'required': True, 'min_length': 10, 'max_length': 1000}
}

USER_REGISTRATION_CONFIG = {
    'username': {'type': 'text', 'required': True, 'min_length': 3, 'max_length': 50},
    'email': {'type': 'email', 'required': True},
    'password': {'type': 'password', 'required': True},
    'confirm_password': {'type': 'password', 'required': True},
    'first_name': {'type': 'text', 'required': True, 'max_length': 50},
    'last_name': {'type': 'text', 'required': True, 'max_length': 50},
    'phone': {'type': 'phone', 'required': False},
    'birthdate': {'type': 'date', 'required': False}
}

PROFILE_UPDATE_CONFIG = {
    'first_name': {'type': 'text', 'required': True, 'max_length': 50},
    'last_name': {'type': 'text', 'required': True, 'max_length': 50},
    'email': {'type': 'email', 'required': True},
    'phone': {'type': 'phone', 'required': False},
    'bio': {'type': 'textarea', 'required': False, 'max_length': 500},
    'website': {'type': 'url', 'required': False}
}


# Global form processor instance
form_processor = FormProcessor()


# Helper functions for backward compatibility
def validate_form(form_data: Dict[str, Any], config: Dict[str, Any]) -> Dict[str, Any]:
    """Validate form data using configuration"""
    return form_processor.process_form(form_data, config)


def sanitize_input(value: str, input_type: str = 'text') -> str:
    """Sanitize input value"""
    config = {'type': input_type}
    return form_processor._sanitize_field(value, config)


def validate_email_format(email: str) -> bool:
    """Check if email format is valid"""
    return FormValidator.validate_email(email)


def validate_password_security(password: str) -> Dict[str, Any]:
    """Check password security requirements"""
    return FormValidator.validate_password_strength(password)


class FormsHelper:
    """Legacy compatibility class"""
    
    def __init__(self):
        self.processor = form_processor
        self.validator = FormValidator()
        self.sanitizer = FormSanitizer()
    
    def process_contact_form(self, form_data):
        """Process contact form submission"""
        return self.processor.process_form(form_data, CONTACT_FORM_CONFIG)
    
    def process_registration_form(self, form_data):
        """Process user registration form"""
        result = self.processor.process_form(form_data, USER_REGISTRATION_CONFIG)
        
        # Additional validation for password confirmation
        if result['valid'] and 'password' in result['cleaned_data'] and 'confirm_password' in result['cleaned_data']:
            if result['cleaned_data']['password'] != result['cleaned_data']['confirm_password']:
                result['valid'] = False
                result['errors']['confirm_password'] = 'Passwords do not match'
        
        return result
    
    def process_profile_form(self, form_data):
        """Process profile update form"""
        return self.processor.process_form(form_data, PROFILE_UPDATE_CONFIG)


# Initialize forms helper
forms_helper = FormsHelper()