#!/usr/bin/env python3
"""
Final Verification Sweep - Ensure No Features Missed
Multi-layered search to verify complete feature coverage
"""

import os
import re
import json
import ast
from pathlib import Path
from datetime import datetime

class FinalVerificationSweep:
    """Final comprehensive verification of all features"""
    
    def __init__(self):
        self.date_str = datetime.now().strftime("%Y-%m-%d")
        self.missed_features = {}
        self.verification_patterns = []
        
    def perform_comprehensive_verification(self):
        """Perform multi-layered verification to find any missed features"""
        print("🔍 Final Verification Sweep - Ensuring Complete Coverage...")
        
        # Load existing discovered features
        discovery_file = f'docs/ultimate_feature_discovery_{self.date_str}.json'
        existing_features = set()
        
        if os.path.exists(discovery_file):
            with open(discovery_file, 'r') as f:
                existing_data = json.load(f)
                existing_features = set(existing_data.keys())
                print(f"📊 Existing features: {len(existing_features)}")
        
        # Multi-layered search patterns
        self._search_by_file_patterns()
        self._search_by_function_patterns()
        self._search_by_route_patterns()
        self._search_by_import_patterns()
        self._search_by_comment_patterns()
        self._search_by_template_patterns()
        self._search_by_config_patterns()
        self._search_by_database_patterns()
        
        # Check for missed features
        new_features = set(self.missed_features.keys()) - existing_features
        
        if new_features:
            print(f"⚠️  Found {len(new_features)} potentially missed features!")
            for feature in sorted(new_features):
                print(f"   - {feature}")
        else:
            print("✅ No additional features found - verification complete")
            
        return self.missed_features
        
    def _search_by_file_patterns(self):
        """Search for features by analyzing file names and structures"""
        print("🔍 Searching by file patterns...")
        
        # File pattern mappings that might indicate features
        file_patterns = {
            'integration': 'Third-Party Integration',
            'connector': 'External Service Connector',
            'adapter': 'Service Adapter',
            'client': 'Client Interface',
            'manager': 'Resource Manager',
            'controller': 'System Controller',
            'processor': 'Data Processor',
            'analyzer': 'Analysis Engine',
            'generator': 'Content Generator',
            'optimizer': 'Performance Optimizer',
            'monitor': 'Monitoring System',
            'tracker': 'Tracking System',
            'scheduler': 'Scheduling System',
            'notifier': 'Notification System',
            'validator': 'Validation System',
            'transformer': 'Data Transformer',
            'resolver': 'Dependency Resolver',
            'factory': 'Object Factory',
            'builder': 'Builder Pattern',
            'proxy': 'Proxy Interface',
            'wrapper': 'Wrapper Interface',
            'bridge': 'Bridge Pattern',
            'facade': 'Facade Interface'
        }
        
        for root, dirs, files in os.walk('.'):
            # Skip cache and backup directories
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['__pycache__', 'node_modules']]
            
            for file in files:
                if file.endswith('.py'):
                    file_lower = file.lower()
                    for pattern, feature_type in file_patterns.items():
                        if pattern in file_lower:
                            file_path = os.path.join(root, file)
                            feature_name = f"{file.replace('.py', '').title()} {feature_type}"
                            self._add_potential_feature(feature_name, file_path, 'File Pattern Analysis')
                            
    def _search_by_function_patterns(self):
        """Search for features by analyzing function names and patterns"""
        print("🔍 Searching by function patterns...")
        
        function_patterns = {
            'sync_': 'Data Synchronization',
            'backup_': 'Backup System',
            'restore_': 'Restore System',
            'migrate_': 'Migration Tool',
            'convert_': 'Data Conversion',
            'transform_': 'Data Transformation',
            'parse_': 'Parsing System',
            'validate_': 'Validation System',
            'sanitize_': 'Data Sanitization',
            'encrypt_': 'Encryption System',
            'decrypt_': 'Decryption System',
            'compress_': 'Compression System',
            'decompress_': 'Decompression System',
            'hash_': 'Hashing System',
            'sign_': 'Digital Signature',
            'verify_': 'Verification System',
            'authenticate_': 'Authentication System',
            'authorize_': 'Authorization System',
            'filter_': 'Filtering System',
            'sort_': 'Sorting System',
            'search_': 'Search System',
            'index_': 'Indexing System',
            'cache_': 'Caching System',
            'queue_': 'Queue Management',
            'schedule_': 'Scheduling System',
            'monitor_': 'Monitoring System',
            'alert_': 'Alert System',
            'notify_': 'Notification System',
            'log_': 'Logging System',
            'audit_': 'Audit System',
            'track_': 'Tracking System',
            'measure_': 'Measurement System',
            'calculate_': 'Calculation Engine',
            'compute_': 'Computation Engine',
            'process_': 'Processing Engine',
            'generate_': 'Generation System',
            'create_': 'Creation System',
            'build_': 'Builder System',
            'compile_': 'Compilation System',
            'render_': 'Rendering System',
            'format_': 'Formatting System',
            'clean_': 'Cleanup System',
            'optimize_': 'Optimization System',
            'enhance_': 'Enhancement System',
            'improve_': 'Improvement System',
            'repair_': 'Repair System',
            'fix_': 'Fix System',
            'debug_': 'Debug System',
            'test_': 'Testing System',
            'check_': 'Checking System',
            'scan_': 'Scanning System',
            'detect_': 'Detection System',
            'recognize_': 'Recognition System',
            'classify_': 'Classification System',
            'categorize_': 'Categorization System',
            'tag_': 'Tagging System',
            'label_': 'Labeling System',
            'annotate_': 'Annotation System',
            'mark_': 'Marking System',
            'flag_': 'Flagging System',
            'toggle_': 'Toggle System',
            'switch_': 'Switch System',
            'enable_': 'Enable System',
            'disable_': 'Disable System',
            'activate_': 'Activation System',
            'deactivate_': 'Deactivation System',
            'start_': 'Start System',
            'stop_': 'Stop System',
            'pause_': 'Pause System',
            'resume_': 'Resume System',
            'restart_': 'Restart System',
            'reload_': 'Reload System',
            'refresh_': 'Refresh System',
            'update_': 'Update System',
            'upgrade_': 'Upgrade System',
            'downgrade_': 'Downgrade System',
            'install_': 'Installation System',
            'uninstall_': 'Uninstallation System',
            'deploy_': 'Deployment System',
            'undeploy_': 'Undeployment System',
            'publish_': 'Publishing System',
            'unpublish_': 'Unpublishing System',
            'subscribe_': 'Subscription System',
            'unsubscribe_': 'Unsubscription System',
            'connect_': 'Connection System',
            'disconnect_': 'Disconnection System',
            'bind_': 'Binding System',
            'unbind_': 'Unbinding System',
            'attach_': 'Attachment System',
            'detach_': 'Detachment System',
            'link_': 'Linking System',
            'unlink_': 'Unlinking System',
            'join_': 'Join System',
            'leave_': 'Leave System',
            'enter_': 'Entry System',
            'exit_': 'Exit System',
            'open_': 'Opening System',
            'close_': 'Closing System',
            'lock_': 'Locking System',
            'unlock_': 'Unlocking System',
            'secure_': 'Security System',
            'protect_': 'Protection System',
            'guard_': 'Guard System',
            'shield_': 'Shield System',
            'defend_': 'Defense System',
            'attack_': 'Attack System',
            'counter_': 'Counter System',
            'block_': 'Blocking System',
            'allow_': 'Allow System',
            'deny_': 'Deny System',
            'grant_': 'Grant System',
            'revoke_': 'Revoke System',
            'approve_': 'Approval System',
            'reject_': 'Rejection System',
            'accept_': 'Acceptance System',
            'decline_': 'Decline System'
        }
        
        # Search through all Python files
        for root, dirs, files in os.walk('.'):
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['__pycache__', 'node_modules']]
            
            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                            
                        # Extract function names
                        functions = re.findall(r'def\s+(\w+)\s*\(', content)
                        
                        for func_name in functions:
                            func_lower = func_name.lower()
                            for pattern, system_type in function_patterns.items():
                                if func_name.startswith(pattern) or pattern in func_lower:
                                    feature_name = f"{func_name.title()} {system_type}"
                                    self._add_potential_feature(feature_name, file_path, 'Function Pattern Analysis')
                                    
                    except Exception as e:
                        continue
                        
    def _search_by_route_patterns(self):
        """Search for features by analyzing route patterns"""
        print("🔍 Searching by route patterns...")
        
        route_patterns = {
            '/webhook': 'Webhook Handler',
            '/callback': 'Callback Handler',
            '/redirect': 'Redirect Handler',
            '/proxy': 'Proxy Handler',
            '/stream': 'Streaming Handler',
            '/download': 'Download Handler',
            '/upload': 'Upload Handler',
            '/export': 'Export Handler',
            '/import': 'Import Handler',
            '/sync': 'Sync Handler',
            '/backup': 'Backup Handler',
            '/restore': 'Restore Handler',
            '/migrate': 'Migration Handler',
            '/test': 'Test Handler',
            '/debug': 'Debug Handler',
            '/admin': 'Admin Handler',
            '/api/v': 'Versioned API',
            '/status': 'Status Handler',
            '/ping': 'Ping Handler',
            '/metrics': 'Metrics Handler',
            '/analytics': 'Analytics Handler',
            '/reports': 'Reports Handler',
            '/dashboard': 'Dashboard Handler',
            '/config': 'Configuration Handler',
            '/settings': 'Settings Handler',
            '/preferences': 'Preferences Handler',
            '/profile': 'Profile Handler',
            '/account': 'Account Handler',
            '/billing': 'Billing Handler',
            '/payment': 'Payment Handler',
            '/subscription': 'Subscription Handler',
            '/notification': 'Notification Handler',
            '/alert': 'Alert Handler',
            '/message': 'Message Handler',
            '/chat': 'Chat Handler',
            '/search': 'Search Handler',
            '/filter': 'Filter Handler',
            '/sort': 'Sort Handler',
            '/validate': 'Validation Handler',
            '/verify': 'Verification Handler',
            '/authenticate': 'Authentication Handler',
            '/authorize': 'Authorization Handler',
            '/permission': 'Permission Handler',
            '/role': 'Role Handler',
            '/group': 'Group Handler',
            '/team': 'Team Handler',
            '/organization': 'Organization Handler',
            '/workspace': 'Workspace Handler',
            '/project': 'Project Handler',
            '/task': 'Task Handler',
            '/event': 'Event Handler',
            '/schedule': 'Schedule Handler',
            '/calendar': 'Calendar Handler',
            '/appointment': 'Appointment Handler',
            '/booking': 'Booking Handler',
            '/reservation': 'Reservation Handler',
            '/order': 'Order Handler',
            '/cart': 'Cart Handler',
            '/checkout': 'Checkout Handler',
            '/invoice': 'Invoice Handler',
            '/receipt': 'Receipt Handler',
            '/ticket': 'Ticket Handler',
            '/support': 'Support Handler',
            '/help': 'Help Handler',
            '/faq': 'FAQ Handler',
            '/guide': 'Guide Handler',
            '/tutorial': 'Tutorial Handler',
            '/documentation': 'Documentation Handler',
            '/reference': 'Reference Handler',
            '/manual': 'Manual Handler',
            '/glossary': 'Glossary Handler',
            '/terms': 'Terms Handler',
            '/privacy': 'Privacy Handler',
            '/policy': 'Policy Handler',
            '/agreement': 'Agreement Handler',
            '/license': 'License Handler',
            '/copyright': 'Copyright Handler',
            '/trademark': 'Trademark Handler',
            '/patent': 'Patent Handler',
            '/legal': 'Legal Handler',
            '/compliance': 'Compliance Handler',
            '/security': 'Security Handler',
            '/safety': 'Safety Handler',
            '/emergency': 'Emergency Handler',
            '/crisis': 'Crisis Handler',
            '/incident': 'Incident Handler',
            '/recovery': 'Recovery Handler',
            '/backup': 'Backup Handler',
            '/restore': 'Restore Handler'
        }
        
        # Search through all Python files for route definitions
        for root, dirs, files in os.walk('.'):
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['__pycache__', 'node_modules']]
            
            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                            
                        # Find route definitions
                        routes = re.findall(r'@\w*\.route\(["\']([^"\']+)["\']', content)
                        
                        for route in routes:
                            route_lower = route.lower()
                            for pattern, handler_type in route_patterns.items():
                                if pattern in route_lower:
                                    feature_name = f"{route.title()} {handler_type}"
                                    self._add_potential_feature(feature_name, file_path, 'Route Pattern Analysis')
                                    
                    except Exception as e:
                        continue
                        
    def _search_by_import_patterns(self):
        """Search for features by analyzing import patterns"""
        print("🔍 Searching by import patterns...")
        
        import_patterns = {
            'requests': 'HTTP Client Integration',
            'urllib': 'URL Processing System',
            'json': 'JSON Processing System',
            'xml': 'XML Processing System',
            'csv': 'CSV Processing System',
            'pandas': 'Data Analysis System',
            'numpy': 'Numerical Computing System',
            'scipy': 'Scientific Computing System',
            'matplotlib': 'Data Visualization System',
            'plotly': 'Interactive Visualization System',
            'seaborn': 'Statistical Visualization System',
            'sklearn': 'Machine Learning System',
            'tensorflow': 'Deep Learning System',
            'torch': 'PyTorch Deep Learning System',
            'keras': 'Neural Network System',
            'opencv': 'Computer Vision System',
            'pillow': 'Image Processing System',
            'pil': 'Image Processing System',
            'boto3': 'AWS Integration System',
            'azure': 'Azure Integration System',
            'google': 'Google Services Integration',
            'stripe': 'Payment Processing System',
            'paypal': 'PayPal Integration System',
            'twilio': 'SMS/Voice Integration System',
            'sendgrid': 'Email Service Integration',
            'celery': 'Task Queue System',
            'redis': 'Caching System',
            'memcached': 'Memory Caching System',
            'elasticsearch': 'Search Engine System',
            'solr': 'Search Platform System',
            'kafka': 'Message Streaming System',
            'rabbitmq': 'Message Queue System',
            'mqtt': 'IoT Messaging System',
            'websocket': 'WebSocket Communication System',
            'socketio': 'Real-time Communication System',
            'encryption': 'Encryption System',
            'cryptography': 'Cryptographic System',
            'hashlib': 'Hashing System',
            'base64': 'Encoding System',
            'jwt': 'Token Authentication System',
            'oauth': 'OAuth Authentication System',
            'ldap': 'LDAP Authentication System',
            'saml': 'SAML Authentication System',
            'kerberos': 'Kerberos Authentication System',
            'docker': 'Container System',
            'kubernetes': 'Orchestration System',
            'terraform': 'Infrastructure System',
            'ansible': 'Configuration Management System',
            'puppet': 'Configuration Management System',
            'chef': 'Configuration Management System',
            'vagrant': 'Development Environment System',
            'git': 'Version Control System',
            'svn': 'Version Control System',
            'mercurial': 'Version Control System',
            'pytest': 'Testing Framework',
            'unittest': 'Unit Testing System',
            'nose': 'Testing System',
            'coverage': 'Code Coverage System',
            'lint': 'Code Quality System',
            'black': 'Code Formatting System',
            'isort': 'Import Sorting System',
            'mypy': 'Type Checking System',
            'bandit': 'Security Analysis System',
            'safety': 'Dependency Security System',
            'sentry': 'Error Monitoring System',
            'logging': 'Logging System',
            'loguru': 'Advanced Logging System',
            'prometheus': 'Metrics System',
            'grafana': 'Monitoring Dashboard System',
            'datadog': 'Monitoring System',
            'newrelic': 'Performance Monitoring System',
            'elastic': 'Elastic Stack System',
            'kibana': 'Data Visualization System',
            'logstash': 'Log Processing System',
            'beats': 'Data Collection System',
            'zipkin': 'Distributed Tracing System',
            'jaeger': 'Tracing System',
            'opentelemetry': 'Observability System'
        }
        
        # Search through all Python files for imports
        for root, dirs, files in os.walk('.'):
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['__pycache__', 'node_modules']]
            
            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                            
                        # Find import statements
                        imports = re.findall(r'(?:import|from)\s+(\w+)', content)
                        
                        for imp in imports:
                            imp_lower = imp.lower()
                            for pattern, system_type in import_patterns.items():
                                if pattern in imp_lower:
                                    feature_name = f"{imp.title()} {system_type}"
                                    self._add_potential_feature(feature_name, file_path, 'Import Pattern Analysis')
                                    
                    except Exception as e:
                        continue
                        
    def _search_by_comment_patterns(self):
        """Search for features by analyzing comments and docstrings"""
        print("🔍 Searching by comment patterns...")
        
        comment_patterns = [
            r'#\s*TODO[:\s]+([^#\n]+)',
            r'#\s*FIXME[:\s]+([^#\n]+)',
            r'#\s*NOTE[:\s]+([^#\n]+)',
            r'#\s*HACK[:\s]+([^#\n]+)',
            r'#\s*XXX[:\s]+([^#\n]+)',
            r'#\s*FEATURE[:\s]+([^#\n]+)',
            r'#\s*ENHANCEMENT[:\s]+([^#\n]+)',
            r'#\s*IMPROVEMENT[:\s]+([^#\n]+)',
            r'#\s*OPTIMIZATION[:\s]+([^#\n]+)',
            r'#\s*REFACTOR[:\s]+([^#\n]+)',
            r'#\s*CLEANUP[:\s]+([^#\n]+)',
            r'#\s*DEPRECATED[:\s]+([^#\n]+)',
            r'#\s*OBSOLETE[:\s]+([^#\n]+)',
            r'#\s*LEGACY[:\s]+([^#\n]+)',
            r'#\s*EXPERIMENTAL[:\s]+([^#\n]+)',
            r'#\s*BETA[:\s]+([^#\n]+)',
            r'#\s*ALPHA[:\s]+([^#\n]+)',
            r'#\s*PROTOTYPE[:\s]+([^#\n]+)',
            r'#\s*DRAFT[:\s]+([^#\n]+)',
            r'#\s*WIP[:\s]+([^#\n]+)',
            r'#\s*WORK IN PROGRESS[:\s]+([^#\n]+)'
        ]
        
        # Search through all files for comments
        for root, dirs, files in os.walk('.'):
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['__pycache__', 'node_modules']]
            
            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                            
                        for pattern in comment_patterns:
                            matches = re.findall(pattern, content, re.IGNORECASE)
                            for match in matches:
                                feature_name = f"Planned Feature: {match.strip()[:50]}"
                                self._add_potential_feature(feature_name, file_path, 'Comment Analysis')
                                
                    except Exception as e:
                        continue
                        
    def _search_by_template_patterns(self):
        """Search for features by analyzing HTML templates"""
        print("🔍 Searching by template patterns...")
        
        # Search for HTML templates and forms
        for root, dirs, files in os.walk('.'):
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['__pycache__', 'node_modules']]
            
            for file in files:
                if file.endswith('.html'):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                            
                        # Look for forms
                        forms = re.findall(r'<form[^>]*action=["\']([^"\']*)["\']', content, re.IGNORECASE)
                        for form_action in forms:
                            feature_name = f"Form Handler: {form_action}"
                            self._add_potential_feature(feature_name, file_path, 'Template Analysis')
                            
                        # Look for JavaScript functions
                        js_functions = re.findall(r'function\s+(\w+)\s*\(', content)
                        for func in js_functions:
                            feature_name = f"JavaScript Function: {func}"
                            self._add_potential_feature(feature_name, file_path, 'Template Analysis')
                            
                        # Look for API calls
                        api_calls = re.findall(r'fetch\(["\']([^"\']*)["\']', content)
                        for api_call in api_calls:
                            feature_name = f"Frontend API Call: {api_call}"
                            self._add_potential_feature(feature_name, file_path, 'Template Analysis')
                            
                    except Exception as e:
                        continue
                        
    def _search_by_config_patterns(self):
        """Search for features by analyzing configuration files"""
        print("🔍 Searching by configuration patterns...")
        
        config_files = [
            'requirements.txt', 'requirements_dev.txt', 'pyproject.toml', 'setup.py',
            'package.json', 'yarn.lock', 'package-lock.json',
            'Dockerfile', 'docker-compose.yml', 'docker-compose.yaml',
            'replit.toml', 'replit.nix', '.replit',
            'manifest.json', 'sw.js'
        ]
        
        for config_file in config_files:
            if os.path.exists(config_file):
                try:
                    with open(config_file, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        
                    # Analyze dependencies
                    if 'requirements' in config_file or 'package.json' in config_file:
                        dependencies = re.findall(r'^([a-zA-Z0-9\-_]+)', content, re.MULTILINE)
                        for dep in dependencies:
                            if dep and not dep.startswith('#'):
                                feature_name = f"Dependency: {dep.title()} Integration"
                                self._add_potential_feature(feature_name, config_file, 'Configuration Analysis')
                                
                    # Analyze manifest.json for PWA features
                    elif config_file == 'manifest.json':
                        feature_name = "Progressive Web App Manifest"
                        self._add_potential_feature(feature_name, config_file, 'Configuration Analysis')
                        
                    # Analyze service worker
                    elif config_file == 'sw.js':
                        feature_name = "Service Worker Offline Support"
                        self._add_potential_feature(feature_name, config_file, 'Configuration Analysis')
                        
                except Exception as e:
                    continue
                    
    def _search_by_database_patterns(self):
        """Search for features by analyzing database patterns"""
        print("🔍 Searching by database patterns...")
        
        # Look for SQL files
        for root, dirs, files in os.walk('.'):
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['__pycache__', 'node_modules']]
            
            for file in files:
                if file.endswith('.sql'):
                    file_path = os.path.join(root, file)
                    feature_name = f"SQL Script: {file.replace('.sql', '').title()}"
                    self._add_potential_feature(feature_name, file_path, 'Database Analysis')
                    
        # Look for database migration files
        migration_patterns = ['migration', 'migrate', 'schema', 'alembic']
        for pattern in migration_patterns:
            for root, dirs, files in os.walk('.'):
                if pattern in root.lower():
                    feature_name = f"Database Migration System"
                    self._add_potential_feature(feature_name, root, 'Database Analysis')
                    break
                    
    def _add_potential_feature(self, feature_name, file_path, analysis_type):
        """Add a potentially missed feature"""
        if feature_name not in self.missed_features:
            self.missed_features[feature_name] = {
                'description': f'Feature discovered through {analysis_type}',
                'files': set(),
                'analysis_type': analysis_type,
                'category': 'Verification Discovered'
            }
            
        self.missed_features[feature_name]['files'].add(file_path)
        
    def generate_verification_report(self):
        """Generate verification report"""
        features = self.perform_comprehensive_verification()
        
        if not features:
            print("✅ VERIFICATION COMPLETE: No additional features found")
            return True
            
        # Clean up features data for JSON serialization
        cleaned_features = {}
        for name, data in features.items():
            cleaned_data = dict(data)
            cleaned_data['files'] = list(data['files'])
            cleaned_features[name] = cleaned_data
            
        # Save verification report
        with open(f'docs/verification_report_{self.date_str}.json', 'w') as f:
            json.dump(cleaned_features, f, indent=2)
            
        # Create markdown report
        markdown_report = f"""# Final Verification Report
*Generated: {datetime.now().strftime('%B %d, %Y')}*

## Verification Summary

Found {len(features)} additional potential features through comprehensive verification.

## Additional Features Discovered

"""
        
        for feature_name, feature_data in sorted(features.items()):
            files_list = list(feature_data['files'])[:3]
            files_str = ', '.join(files_list)
            if len(feature_data['files']) > 3:
                files_str += f" (+{len(feature_data['files']) - 3} more)"
                
            markdown_report += f"**{feature_name}**\n"
            markdown_report += f"- **Analysis Type**: {feature_data['analysis_type']}\n"
            markdown_report += f"- **Description**: {feature_data['description']}\n"
            markdown_report += f"- **Files**: {files_str}\n\n"
            
        with open(f'docs/verification_report_{self.date_str}.md', 'w') as f:
            f.write(markdown_report)
            
        print(f"📋 Verification report saved with {len(features)} additional features")
        return features

if __name__ == "__main__":
    verifier = FinalVerificationSweep()
    verifier.generate_verification_report()