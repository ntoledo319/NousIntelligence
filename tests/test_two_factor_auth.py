"""
Unit tests for the two-factor authentication module

These tests verify the functionality of two-factor authentication features including:
- TOTP generation and validation
- Backup code generation and verification
- QR code generation
- 2FA session management

@module: test_two_factor_auth
@author: NOUS Development Team
"""
import unittest
import sys
import os
import time
import base64
from unittest.mock import patch, MagicMock
from flask import Flask, session

# Add parent directory to path to import modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.two_factor_auth import (
    generate_totp_secret,
    generate_totp,
    verify_totp,
    get_totp_uri,
    generate_qr_code,
    generate_backup_codes,
    hash_backup_code,
    verify_backup_code,
    setup_2fa_session,
    confirm_2fa_setup,
    TOTPVerificationError,
    TOTP_DIGITS,
    TOTP_INTERVAL
)

class TestTOTPGeneration(unittest.TestCase):
    """Test cases for TOTP generation and verification"""
    
    def test_generate_secret(self):
        """Test generation of TOTP secret"""
        secret = generate_totp_secret()
        
        # Check secret format (base32 encoded)
        self.assertTrue(all(c in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ234567' for c in secret))
        self.assertGreaterEqual(len(secret), 16)  # Should be at least 16 characters
    
    def test_generate_totp(self):
        """Test generation of TOTP code"""
        secret = generate_totp_secret()
        code = generate_totp(secret)
        
        # Check code format
        self.assertTrue(code.isdigit())
        self.assertEqual(len(code), TOTP_DIGITS)
    
    def test_verify_totp(self):
        """Test verification of TOTP code"""
        secret = generate_totp_secret()
        code = generate_totp(secret)
        
        # Code should verify
        self.assertTrue(verify_totp(secret, code))
        
        # Invalid code should fail
        self.assertFalse(verify_totp(secret, '000000'))
        
        # Empty code should fail
        self.assertFalse(verify_totp(secret, ''))
        
        # Non-numeric code should fail
        self.assertFalse(verify_totp(secret, 'ABCDEF'))
    
    def test_totp_window(self):
        """Test TOTP time window functionality"""
        secret = generate_totp_secret()
        
        # Generate code for current time
        current_code = generate_totp(secret)
        
        # Generate code for previous interval
        prev_time = int(time.time()) - TOTP_INTERVAL
        prev_code = generate_totp(secret, prev_time)
        
        # Generate code for next interval
        next_time = int(time.time()) + TOTP_INTERVAL
        next_code = generate_totp(secret, next_time)
        
        # With default window=1, all should verify
        self.assertTrue(verify_totp(secret, current_code))
        self.assertTrue(verify_totp(secret, prev_code))  
        self.assertTrue(verify_totp(secret, next_code))
        
        # With window=0, only current code should verify
        self.assertTrue(verify_totp(secret, current_code, window=0))
        self.assertFalse(verify_totp(secret, prev_code, window=0))
        self.assertFalse(verify_totp(secret, next_code, window=0))

class TestBackupCodes(unittest.TestCase):
    """Test cases for backup code functionality"""
    
    def test_generate_backup_codes(self):
        """Test generation of backup codes"""
        codes = generate_backup_codes()
        
        # Check number of codes
        self.assertEqual(len(codes), 10)  # Default is 10 codes
        
        # Check code format
        for code in codes:
            self.assertEqual(len(code), 8)  # Default length is 8
            self.assertTrue(all(c in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789' for c in code))
    
    def test_hash_and_verify_backup_code(self):
        """Test hashing and verification of backup codes"""
        code = 'ABCD1234'
        
        # Hash the code
        hashed_code = hash_backup_code(code)
        
        # Should be a base64 string
        self.assertTrue(isinstance(hashed_code, str))
        try:
            base64.b64decode(hashed_code)  # Should decode without error
        except Exception:
            self.fail("Hashed code is not valid base64")
        
        # Verification should succeed with correct code
        self.assertTrue(verify_backup_code(code, hashed_code))
        
        # Verification should fail with incorrect code
        self.assertFalse(verify_backup_code('WRONG123', hashed_code))
        
        # Different codes should have different hashes
        another_code = 'EFGH5678'
        another_hash = hash_backup_code(another_code)
        self.assertNotEqual(hashed_code, another_hash)

class TestQRCode(unittest.TestCase):
    """Test cases for QR code generation"""
    
    def test_get_totp_uri(self):
        """Test generation of TOTP URI"""
        secret = 'ABCDEFGHIJKLMNOP'
        account = 'user@example.com'
        
        uri = get_totp_uri(secret, account)
        
        # Check URI format
        self.assertTrue(uri.startswith('otpauth://totp/'))
        self.assertIn(f'secret={secret}', uri)
        self.assertIn('algorithm=SHA1', uri)
        self.assertIn(f'digits={TOTP_DIGITS}', uri)
        self.assertIn(f'period={TOTP_INTERVAL}', uri)
    
    def test_generate_qr_code(self):
        """Test QR code generation"""
        uri = 'otpauth://totp/NOUS:user@example.com?secret=ABCDEFGHIJKLMNOP&issuer=NOUS'
        
        qr_code = generate_qr_code(uri)
        
        # Should return bytes
        self.assertTrue(isinstance(qr_code, bytes))
        
        # Should be a PNG image
        self.assertTrue(qr_code.startswith(b'\x89PNG'))

class TestSessionManagement(unittest.TestCase):
    """Test cases for 2FA session management"""
    
    def setUp(self):
        """Set up test environment"""
        self.app = Flask(__name__)
        self.app.config['SECRET_KEY'] = 'test_secret_key'
        self.app.config['TESTING'] = True
        
        # Create test context
        self.ctx = self.app.test_request_context()
        self.ctx.push()
        
        # Clear session
        with self.app.test_client() as client:
            with client.session_transaction() as sess:
                sess.clear()
    
    def tearDown(self):
        """Clean up after test"""
        self.ctx.pop()
    
    def test_setup_2fa_session(self):
        """Test setting up 2FA session"""
        user_id = 123
        
        with self.app.test_client() as client:
            with client.session_transaction() as sess:
                # Call setup function
                setup_data = setup_2fa_session(user_id)
                
                # Check returned data
                self.assertIn('secret', setup_data)
                self.assertIn('backup_codes', setup_data)
                self.assertEqual(len(setup_data['backup_codes']), 10)
                
                # Check session data
                self.assertIn('2fa_setup', sess)
                self.assertEqual(sess['2fa_setup']['user_id'], user_id)
                self.assertEqual(sess['2fa_setup']['secret'], setup_data['secret'])
                self.assertIn('backup_codes', sess['2fa_setup'])
                self.assertIn('setup_time', sess['2fa_setup'])
    
    @patch('utils.two_factor_auth.verify_totp')
    def test_confirm_2fa_setup(self, mock_verify_totp):
        """Test confirming 2FA setup"""
        # Setup session data
        user_id = 123
        secret = 'ABCDEFGHIJKLMNOP'
        backup_codes = ['code1hash', 'code2hash']
        
        with self.app.test_client() as client:
            with client.session_transaction() as sess:
                sess['2fa_setup'] = {
                    'user_id': user_id,
                    'secret': secret,
                    'backup_codes': backup_codes,
                    'setup_time': int(time.time())
                }
            
            # Case 1: Verification succeeds
            mock_verify_totp.return_value = True
            result = confirm_2fa_setup('123456')
            self.assertTrue(result)
            
            # Case 2: Verification fails
            mock_verify_totp.return_value = False
            with self.assertRaises(TOTPVerificationError):
                confirm_2fa_setup('invalid')
            
            # Case 3: No setup in session
            with client.session_transaction() as sess:
                sess.pop('2fa_setup', None)
            
            with self.assertRaises(TOTPVerificationError):
                confirm_2fa_setup('123456')

if __name__ == '__main__':
    unittest.main() 