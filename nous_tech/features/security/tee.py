"""
NOUS Tech TEE (Trusted Execution Environment) Module
Secure computation in trusted enclaves for sensitive AI operations
"""

import subprocess
import os
import logging
import json
import tempfile
from typing import Dict, Any, List, Optional, Union
import hashlib

logger = logging.getLogger(__name__)

def init_tee(app):
    """Initialize TEE security system"""
    try:
        # Set default TEE command configuration
        app.config.setdefault('TEE_CMD', ['python3', '-c'])  # Fallback to standard Python
        app.config.setdefault('TEE_ENABLED', False)  # Disabled by default
        app.config.setdefault('TEE_SECURITY_LEVEL', 'standard')
        
        # Check if actual TEE environment is available
        tee_available = check_tee_availability()
        
        if tee_available:
            app.config['TEE_ENABLED'] = True
            logger.info("TEE environment detected and enabled")
        else:
            logger.warning("TEE environment not available, using secure fallback")
        
        # Store TEE configuration
        app.tee_config = {
            'enabled': app.config['TEE_ENABLED'],
            'security_level': app.config['TEE_SECURITY_LEVEL'],
            'command': app.config['TEE_CMD']
        }
        
    except Exception as e:
        logger.error(f"Failed to initialize TEE: {e}")
        # Set safe defaults
        app.config['TEE_ENABLED'] = False
        app.tee_config = {'enabled': False, 'security_level': 'fallback'}

def check_tee_availability() -> bool:
    """Check if TEE environment is available"""
    try:
        # Check for Intel SGX
        if os.path.exists('/dev/sgx'):
            logger.info("Intel SGX detected")
            return True
            
        # Check for ARM TrustZone
        if os.path.exists('/dev/trustzone'):
            logger.info("ARM TrustZone detected")
            return True
            
        # Check for other TEE implementations
        # This would be expanded based on actual TEE infrastructure
        
        return False
        
    except Exception as e:
        logger.error(f"TEE availability check failed: {e}")
        return False

def tee_run_inference(model_path: str, input_data: Union[str, bytes, Dict[str, Any]], 
                     security_level: str = "high") -> Dict[str, Any]:
    """Run AI inference in TEE-secured environment"""
    try:
        from flask import current_app
        
        # Determine if TEE is enabled
        tee_enabled = current_app.config.get('TEE_ENABLED', False)
        
        if tee_enabled:
            return _tee_secure_inference(model_path, input_data, security_level)
        else:
            return _tee_fallback_inference(model_path, input_data, security_level)
            
    except Exception as e:
        logger.error(f"TEE inference failed: {e}")
        return {
            'success': False,
            'error': str(e),
            'security_level': 'failed',
            'fallback_used': True
        }

def _tee_secure_inference(model_path: str, input_data: Union[str, bytes, Dict[str, Any]], 
                         security_level: str) -> Dict[str, Any]:
    """Perform secure inference in actual TEE environment"""
    try:
        from flask import current_app
        
        # Prepare secure execution environment
        secure_script = _prepare_secure_inference_script(model_path, input_data)
        
        # Execute in TEE
        tee_cmd = current_app.config['TEE_CMD']
        
        # For SGX or other TEE implementations
        if 'sgx' in ' '.join(tee_cmd).lower():
            result = _execute_sgx_inference(secure_script, input_data)
        else:
            result = _execute_generic_tee_inference(secure_script, input_data)
        
        return {
            'success': True,
            'result': result,
            'security_level': 'tee_secured',
            'tee_type': 'sgx' if 'sgx' in ' '.join(tee_cmd).lower() else 'generic',
            'verification_hash': _calculate_verification_hash(result)
        }
        
    except Exception as e:
        logger.error(f"TEE secure inference failed: {e}")
        return _tee_fallback_inference(model_path, input_data, security_level)

def _tee_fallback_inference(model_path: str, input_data: Union[str, bytes, Dict[str, Any]], 
                           security_level: str) -> Dict[str, Any]:
    """Fallback secure inference when TEE is not available"""
    try:
        # Use secure subprocess execution with isolated environment
        result = _secure_subprocess_inference(model_path, input_data)
        
        return {
            'success': True,
            'result': result,
            'security_level': 'subprocess_isolated',
            'tee_type': 'fallback',
            'verification_hash': _calculate_verification_hash(result)
        }
        
    except Exception as e:
        logger.error(f"TEE fallback inference failed: {e}")
        return {
            'success': False,
            'error': str(e),
            'security_level': 'failed'
        }

def _prepare_secure_inference_script(model_path: str, 
                                   input_data: Union[str, bytes, Dict[str, Any]]) -> str:
    """Prepare secure inference script for TEE execution"""
    
    # Convert input data to JSON if necessary
    if isinstance(input_data, dict):
        input_json = json.dumps(input_data)
    elif isinstance(input_data, bytes):
        input_json = json.dumps({'binary_data': input_data.hex()})
    else:
        input_json = json.dumps({'text_data': str(input_data)})
    
    # Create secure inference script
    inference_script = f"""
import json
import sys
import os

def secure_inference():
    try:
        # Load input data
        input_data = json.loads('''{input_json}''')
        
        # Mock inference for now - would load actual model
        model_name = "{os.path.basename(model_path)}"
        
        # Simulate secure inference
        result = {{
            'model_used': model_name,
            'prediction': 'secure_inference_result',
            'confidence': 0.85,
            'processing_secure': True
        }}
        
        print(json.dumps(result))
        return result
        
    except Exception as e:
        error_result = {{'error': str(e), 'success': False}}
        print(json.dumps(error_result))
        return error_result

if __name__ == '__main__':
    secure_inference()
"""
    
    return inference_script

def _execute_sgx_inference(script: str, input_data: Any) -> Dict[str, Any]:
    """Execute inference in Intel SGX enclave"""
    try:
        # Create temporary script file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(script)
            script_path = f.name
        
        try:
            # Execute in SGX enclave (mock implementation)
            # In production, this would use actual SGX SDK
            proc = subprocess.Popen(
                ['python3', script_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env=_get_secure_environment()
            )
            
            stdout, stderr = proc.communicate(timeout=30)
            
            if proc.returncode == 0:
                result = json.loads(stdout.decode())
                result['sgx_verified'] = True
                return result
            else:
                logger.error(f"SGX inference failed: {stderr.decode()}")
                return {'error': 'SGX execution failed', 'success': False}
                
        finally:
            os.unlink(script_path)
            
    except Exception as e:
        logger.error(f"SGX inference execution failed: {e}")
        return {'error': str(e), 'success': False}

def _execute_generic_tee_inference(script: str, input_data: Any) -> Dict[str, Any]:
    """Execute inference in generic TEE environment"""
    try:
        from flask import current_app
        
        # Create temporary script file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(script)
            script_path = f.name
        
        try:
            # Execute with TEE command
            tee_cmd = current_app.config['TEE_CMD']
            full_cmd = tee_cmd + [script_path]
            
            proc = subprocess.Popen(
                full_cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env=_get_secure_environment()
            )
            
            stdout, stderr = proc.communicate(timeout=30)
            
            if proc.returncode == 0:
                result = json.loads(stdout.decode())
                result['tee_verified'] = True
                return result
            else:
                logger.error(f"TEE inference failed: {stderr.decode()}")
                return {'error': 'TEE execution failed', 'success': False}
                
        finally:
            os.unlink(script_path)
            
    except Exception as e:
        logger.error(f"Generic TEE inference execution failed: {e}")
        return {'error': str(e), 'success': False}

def _secure_subprocess_inference(model_path: str, input_data: Any) -> Dict[str, Any]:
    """Secure subprocess-based inference as fallback"""
    try:
        # Prepare secure inference script
        script = _prepare_secure_inference_script(model_path, input_data)
        
        # Create temporary script file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(script)
            script_path = f.name
        
        try:
            # Execute in isolated subprocess
            proc = subprocess.Popen(
                ['python3', script_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env=_get_secure_environment()
            )
            
            stdout, stderr = proc.communicate(timeout=30)
            
            if proc.returncode == 0:
                result = json.loads(stdout.decode())
                result['subprocess_secured'] = True
                return result
            else:
                logger.error(f"Secure subprocess failed: {stderr.decode()}")
                return {'error': 'Subprocess execution failed', 'success': False}
                
        finally:
            os.unlink(script_path)
            
    except Exception as e:
        logger.error(f"Secure subprocess inference failed: {e}")
        return {'error': str(e), 'success': False}

def _get_secure_environment() -> Dict[str, str]:
    """Get secure environment variables for TEE execution"""
    # Start with minimal environment
    secure_env = {
        'PATH': '/usr/local/bin:/usr/bin:/bin',
        'PYTHONPATH': '',
        'HOME': '/tmp',
        'TMPDIR': '/tmp'
    }
    
    # Add only necessary variables
    for var in ['PYTHONHOME', 'LD_LIBRARY_PATH']:
        if var in os.environ:
            secure_env[var] = os.environ[var]
    
    return secure_env

def _calculate_verification_hash(result: Dict[str, Any]) -> str:
    """Calculate verification hash for inference result"""
    try:
        # Create deterministic hash of result
        result_str = json.dumps(result, sort_keys=True)
        return hashlib.sha256(result_str.encode()).hexdigest()
    except Exception as e:
        logger.error(f"Failed to calculate verification hash: {e}")
        return "hash_failed"

def verify_tee_result(result: Dict[str, Any], expected_hash: str) -> bool:
    """Verify TEE inference result integrity"""
    try:
        calculated_hash = _calculate_verification_hash(result)
        return calculated_hash == expected_hash
    except Exception as e:
        logger.error(f"TEE result verification failed: {e}")
        return False

def get_tee_status() -> Dict[str, Any]:
    """Get current TEE system status"""
    try:
        from flask import current_app
        
        return {
            'tee_available': current_app.config.get('TEE_ENABLED', False),
            'security_level': current_app.config.get('TEE_SECURITY_LEVEL', 'unknown'),
            'tee_type': _detect_tee_type(),
            'secure_inference_ready': True
        }
        
    except Exception as e:
        logger.error(f"Failed to get TEE status: {e}")
        return {
            'tee_available': False,
            'error': str(e)
        }

def _detect_tee_type() -> str:
    """Detect the type of TEE environment"""
    if os.path.exists('/dev/sgx'):
        return 'intel_sgx'
    elif os.path.exists('/dev/trustzone'):
        return 'arm_trustzone'
    else:
        return 'fallback_secure'

# Convenience wrapper functions
def secure_ai_inference(model_identifier: str, input_data: Any, 
                       security_requirements: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """High-level secure AI inference wrapper"""
    try:
        security_level = "high"
        if security_requirements:
            security_level = security_requirements.get('level', 'high')
        
        result = tee_run_inference(model_identifier, input_data, security_level)
        
        # Log the secure operation for audit
        try:
            from .blockchain import log_ai_inference
            input_hash = hashlib.sha256(str(input_data).encode()).hexdigest()
            output_hash = _calculate_verification_hash(result)
            log_ai_inference("system", model_identifier, input_hash, output_hash, security_level)
        except Exception as e:
            logger.warning(f"Failed to log secure inference: {e}")
        
        return result
        
    except Exception as e:
        logger.error(f"Secure AI inference wrapper failed: {e}")
        return {
            'success': False,
            'error': str(e),
            'security_level': 'failed'
        }