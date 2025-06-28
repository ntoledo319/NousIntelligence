"""
NOUS Tech Blockchain Audit Module
Private, permissioned blockchain logging for secure audit trails
"""

import hashlib
import time
import logging
import json
from typing import Dict, Any, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

# Try to import web3, gracefully degrade if not available
try:
    from web3 import Web3
    WEB3_AVAILABLE = True
except ImportError:
    WEB3_AVAILABLE = False
    logger.warning("web3 not available - blockchain audit will use fallback logging")

class BlockchainAudit:
    """Blockchain-based audit logging for secure record keeping"""
    
    def __init__(self, provider_url: str = None, contract_abi: List[Dict] = None, 
                 contract_address: str = None):
        self.provider_url = provider_url
        self.contract_abi = contract_abi
        self.contract_address = contract_address
        self.w3 = None
        self.contract = None
        self.fallback_mode = False
        self.audit_log = []
        
        if WEB3_AVAILABLE and provider_url:
            try:
                self.w3 = Web3(Web3.HTTPProvider(provider_url))
                if contract_abi and contract_address:
                    self.contract = self.w3.eth.contract(
                        address=contract_address,
                        abi=contract_abi
                    )
                logger.info("Blockchain audit system initialized")
            except Exception as e:
                logger.error(f"Failed to initialize blockchain connection: {e}")
                self.fallback_mode = True
        else:
            logger.warning("Blockchain not available, using fallback audit logging")
            self.fallback_mode = True
    
    def log_access(self, user_id: str, record_id: str, action: str, 
                   metadata: Optional[Dict[str, Any]] = None) -> str:
        """Log access to sensitive records with blockchain audit trail"""
        try:
            timestamp = int(time.time())
            
            # Create audit record
            audit_record = {
                'user_id': user_id,
                'record_id': record_id,
                'action': action,
                'timestamp': timestamp,
                'metadata': metadata or {},
                'hash': self._calculate_record_hash(user_id, record_id, action, timestamp)
            }
            
            if not self.fallback_mode and self.contract:
                # Log to blockchain
                transaction_hash = self._log_to_blockchain(audit_record)
                audit_record['blockchain_tx'] = transaction_hash
                logger.info(f"Logged to blockchain: {transaction_hash}")
            else:
                # Fallback to local secure logging
                transaction_hash = self._log_to_fallback(audit_record)
                audit_record['fallback_tx'] = transaction_hash
                logger.info(f"Logged to fallback audit: {transaction_hash}")
            
            return transaction_hash
            
        except Exception as e:
            logger.error(f"Failed to log audit access: {e}")
            # Emergency fallback
            emergency_hash = self._emergency_log(user_id, record_id, action)
            return emergency_hash
    
    def log_phi_access(self, user_id: str, phi_record_id: str, action: str, 
                       phi_type: str = "medical") -> str:
        """Log access to Protected Health Information (PHI)"""
        metadata = {
            'phi_type': phi_type,
            'compliance_framework': 'HIPAA',
            'security_level': 'high',
            'requires_audit': True
        }
        
        return self.log_access(user_id, phi_record_id, action, metadata)
    
    def log_ai_inference(self, user_id: str, model_id: str, input_hash: str, 
                        output_hash: str, security_level: str = "standard") -> str:
        """Log AI inference operations for auditability"""
        metadata = {
            'model_id': model_id,
            'input_hash': input_hash,
            'output_hash': output_hash,
            'security_level': security_level,
            'operation_type': 'ai_inference'
        }
        
        return self.log_access(user_id, f"ai_inference_{int(time.time())}", 
                              "ai_inference", metadata)
    
    def verify_audit_trail(self, transaction_hash: str) -> Dict[str, Any]:
        """Verify the integrity of an audit trail entry"""
        try:
            if not self.fallback_mode and self.contract:
                # Verify on blockchain
                return self._verify_blockchain_record(transaction_hash)
            else:
                # Verify in fallback system
                return self._verify_fallback_record(transaction_hash)
                
        except Exception as e:
            logger.error(f"Failed to verify audit trail: {e}")
            return {'verified': False, 'error': str(e)}
    
    def get_audit_history(self, user_id: str = None, record_id: str = None, 
                         limit: int = 100) -> List[Dict[str, Any]]:
        """Get audit history for a user or record"""
        try:
            if not self.fallback_mode and self.contract:
                return self._get_blockchain_history(user_id, record_id, limit)
            else:
                return self._get_fallback_history(user_id, record_id, limit)
                
        except Exception as e:
            logger.error(f"Failed to get audit history: {e}")
            return []
    
    def _calculate_record_hash(self, user_id: str, record_id: str, action: str, 
                              timestamp: int) -> str:
        """Calculate cryptographic hash for audit record"""
        data = f"{user_id}:{record_id}:{action}:{timestamp}"
        return hashlib.sha256(data.encode()).hexdigest()
    
    def _log_to_blockchain(self, audit_record: Dict[str, Any]) -> str:
        """Log audit record to blockchain"""
        try:
            # Call smart contract function to log audit
            tx_hash = self.contract.functions.logAudit(
                audit_record['user_id'],
                audit_record['record_id'],
                audit_record['action'],
                audit_record['timestamp']
            ).transact()
            
            return tx_hash.hex()
            
        except Exception as e:
            logger.error(f"Blockchain logging failed: {e}")
            # Fallback to local logging
            return self._log_to_fallback(audit_record)
    
    def _log_to_fallback(self, audit_record: Dict[str, Any]) -> str:
        """Log audit record to secure fallback system"""
        try:
            # Add to in-memory audit log
            self.audit_log.append(audit_record)
            
            # Also write to secure audit file
            self._write_to_audit_file(audit_record)
            
            # Return a hash as transaction ID
            record_data = json.dumps(audit_record, sort_keys=True)
            return hashlib.sha256(record_data.encode()).hexdigest()
            
        except Exception as e:
            logger.error(f"Fallback logging failed: {e}")
            return self._emergency_log(
                audit_record.get('user_id', 'unknown'),
                audit_record.get('record_id', 'unknown'),
                audit_record.get('action', 'unknown')
            )
    
    def _write_to_audit_file(self, audit_record: Dict[str, Any]):
        """Write audit record to secure file"""
        try:
            import os
            
            # Ensure audit directory exists
            audit_dir = 'logs/audit'
            os.makedirs(audit_dir, exist_ok=True)
            
            # Write to daily audit file
            date_str = datetime.now().strftime('%Y-%m-%d')
            audit_file = os.path.join(audit_dir, f'blockchain_audit_{date_str}.log')
            
            with open(audit_file, 'a') as f:
                f.write(json.dumps(audit_record) + '\n')
                
        except Exception as e:
            logger.error(f"Failed to write audit file: {e}")
    
    def _emergency_log(self, user_id: str, record_id: str, action: str) -> str:
        """Emergency logging when all other methods fail"""
        try:
            emergency_record = {
                'user_id': user_id,
                'record_id': record_id,
                'action': action,
                'timestamp': int(time.time()),
                'emergency': True
            }
            
            # Log to system logger as last resort
            logger.critical(f"EMERGENCY AUDIT LOG: {json.dumps(emergency_record)}")
            
            return hashlib.sha256(json.dumps(emergency_record).encode()).hexdigest()
            
        except Exception as e:
            logger.critical(f"Emergency logging failed: {e}")
            return "emergency_log_failed"
    
    def _verify_blockchain_record(self, transaction_hash: str) -> Dict[str, Any]:
        """Verify record on blockchain"""
        try:
            # Get transaction from blockchain
            tx = self.w3.eth.get_transaction(transaction_hash)
            receipt = self.w3.eth.get_transaction_receipt(transaction_hash)
            
            return {
                'verified': receipt.status == 1,
                'block_number': receipt.blockNumber,
                'transaction_hash': transaction_hash,
                'verification_time': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Blockchain verification failed: {e}")
            return {'verified': False, 'error': str(e)}
    
    def _verify_fallback_record(self, transaction_hash: str) -> Dict[str, Any]:
        """Verify record in fallback system"""
        try:
            # Search in-memory log
            for record in self.audit_log:
                record_hash = hashlib.sha256(
                    json.dumps(record, sort_keys=True).encode()
                ).hexdigest()
                
                if record_hash == transaction_hash:
                    return {
                        'verified': True,
                        'record_found': True,
                        'verification_time': datetime.now().isoformat()
                    }
            
            return {'verified': False, 'record_found': False}
            
        except Exception as e:
            logger.error(f"Fallback verification failed: {e}")
            return {'verified': False, 'error': str(e)}
    
    def _get_blockchain_history(self, user_id: str, record_id: str, 
                               limit: int) -> List[Dict[str, Any]]:
        """Get audit history from blockchain"""
        # This would query blockchain events/logs
        # For now, return empty list as placeholder
        return []
    
    def _get_fallback_history(self, user_id: str, record_id: str, 
                             limit: int) -> List[Dict[str, Any]]:
        """Get audit history from fallback system"""
        try:
            filtered_records = []
            
            for record in self.audit_log:
                if user_id and record.get('user_id') != user_id:
                    continue
                if record_id and record.get('record_id') != record_id:
                    continue
                    
                filtered_records.append(record)
                
                if len(filtered_records) >= limit:
                    break
            
            return filtered_records
            
        except Exception as e:
            logger.error(f"Failed to get fallback history: {e}")
            return []

# Convenience functions for common audit operations
def log_user_access(user_id: str, resource: str, action: str) -> str:
    """Log user access to a resource"""
    try:
        from flask import current_app
        
        if hasattr(current_app, 'security_audit'):
            return current_app.security_audit.log_access(user_id, resource, action)
        else:
            # Fallback logging
            logger.info(f"User access: {user_id} {action} {resource}")
            return "fallback_logged"
            
    except Exception as e:
        logger.error(f"Failed to log user access: {e}")
        return "logging_failed"

def log_phi_access(user_id: str, phi_record: str, action: str) -> str:
    """Log PHI access for HIPAA compliance"""
    try:
        from flask import current_app
        
        if hasattr(current_app, 'security_audit'):
            return current_app.security_audit.log_phi_access(user_id, phi_record, action)
        else:
            # Fallback logging with high priority
            logger.warning(f"PHI ACCESS: {user_id} {action} {phi_record}")
            return "phi_fallback_logged"
            
    except Exception as e:
        logger.error(f"Failed to log PHI access: {e}")
        return "phi_logging_failed"

def verify_audit_integrity(transaction_hash: str) -> bool:
    """Verify the integrity of an audit record"""
    try:
        from flask import current_app
        
        if hasattr(current_app, 'security_audit'):
            result = current_app.security_audit.verify_audit_trail(transaction_hash)
            return result.get('verified', False)
        else:
            return False
            
    except Exception as e:
        logger.error(f"Failed to verify audit integrity: {e}")
        return False