"""
Test messaging status functionality
Ensures SMS requests are properly handled with clear error messages
"""

import unittest
import json
from utils.messaging_status import (
    check_messaging_capability,
    get_sms_error_response,
    handle_text_message_request,
    validate_notification_method,
    get_alternative_notification_methods
)

class TestMessagingStatus(unittest.TestCase):
    """Test messaging status utility functions"""
    
    def test_sms_not_available(self):
        """Test that SMS is correctly marked as unavailable"""
        self.assertFalse(check_messaging_capability('sms'))
        self.assertFalse(check_messaging_capability('text_message'))
        self.assertFalse(check_messaging_capability('phone_notification'))
        
    def test_email_available(self):
        """Test that email is correctly marked as available"""
        self.assertTrue(check_messaging_capability('email'))
        self.assertTrue(check_messaging_capability('app_notification'))
        
    def test_sms_error_response(self):
        """Test SMS error response structure"""
        response = get_sms_error_response()
        
        self.assertFalse(response['success'])
        self.assertEqual(response['error'], 'SMS_NOT_AVAILABLE')
        self.assertIn('not currently available', response['message'])
        self.assertIn('alternatives', response)
        self.assertIn('available_methods', response)
        
    def test_handle_text_message_request(self):
        """Test handling of text message requests"""
        response = handle_text_message_request('+1234567890', 'Test message')
        
        self.assertFalse(response['success'])
        self.assertEqual(response['error'], 'SMS_NOT_AVAILABLE')
        
    def test_notification_method_validation(self):
        """Test notification method validation"""
        # SMS methods should be invalid
        self.assertFalse(validate_notification_method('sms'))
        self.assertFalse(validate_notification_method('text'))
        self.assertFalse(validate_notification_method('phone'))
        
        # Available methods should be valid
        self.assertTrue(validate_notification_method('email'))
        self.assertTrue(validate_notification_method('app'))
        self.assertTrue(validate_notification_method('web'))
        
    def test_alternative_methods(self):
        """Test that alternative notification methods are provided"""
        alternatives = get_alternative_notification_methods()
        
        self.assertIsInstance(alternatives, list)
        self.assertIn('email', alternatives)
        self.assertIn('app_notification', alternatives)
        self.assertIn('web_dashboard', alternatives)
        
    def test_capability_case_insensitive(self):
        """Test that capability checking is case insensitive"""
        self.assertFalse(check_messaging_capability('SMS'))
        self.assertFalse(check_messaging_capability('Text_Message'))
        self.assertTrue(check_messaging_capability('EMAIL'))

if __name__ == '__main__':
    unittest.main()