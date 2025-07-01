#!/usr/bin/env python3
"""
Master Verification Script
Runs all security and quality checks to ensure 100% compliance
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List, bool

class MasterVerification:
    """Orchestrates all verification checks"""
    
    def __init__(self):
        self.verification_dir = Path(__file__).parent
        self.project_root = self.verification_dir.parent
        self.results = {}
        self.overall_status = True
        
    def run_all_verifications(self) -> Dict:
        """Run all verification scripts and compile results"""
        print("🔍 Starting comprehensive security and quality verification...")
        print(f"Project root: {self.project_root}")
        print("=" * 60)
        
        verifications = [
            ("Hardcoded Secrets", "verify_no_secrets.py"),
            ("SQL Security", "verify_sql_security.py"),
            ("Authentication", "verify_authentication.py"),
            ("Input Validation", "verify_input_validation.py"),
            ("Error Handling", "verify_error_handling.py"),
            ("Dangerous Functions", "verify_no_dangerous_functions.py"),
        ]
        
        for name, script in verifications:
            print(f"\n🔍 Running {name} verification...")
            try:
                result = self._run_verification(script)
                self.results[name] = result
                
                if result['status'] != 'PASS':
                    self.overall_status = False
                    print(f"❌ {name}: {result['summary']}")
                else:
                    print(f"✅ {name}: PASSED")
                    
            except Exception as e:
                print(f"❌ {name}: ERROR - {e}")
                self.results[name] = {
                    'status': 'ERROR',
                    'error': str(e),
                    'summary': f"Verification failed: {e}"
                }
                self.overall_status = False
        
        # Generate master report
        self._generate_master_report()
        
        return self.results
    
    def _run_verification(self, script_name: str) -> Dict:
        """Run a single verification script"""
        script_path = self.verification_dir / script_name
        
        if not script_path.exists():
            return {
                'status': 'SKIP',
                'summary': f"Verification script {script_name} not found"
            }
        
        try:
            # Run the verification script
            result = subprocess.run(
                [sys.executable, str(script_path)],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=120  # 2 minute timeout
            )
            
            # Parse results from the script's output
            if result.returncode == 0:
                status = 'PASS'
                summary = "All checks passed"
            else:
                status = 'FAIL'
                summary = self._extract_summary_from_output(result.stdout)
            
            return {
                'status': status,
                'return_code': result.returncode,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'summary': summary
            }
            
        except subprocess.TimeoutExpired:
            return {
                'status': 'TIMEOUT',
                'summary': "Verification timed out after 2 minutes"
            }
        except Exception as e:
            return {
                'status': 'ERROR',
                'summary': f"Execution error: {e}"
            }
    
    def _extract_summary_from_output(self, output: str) -> str:
        """Extract key summary information from verification output"""
        lines = output.split('\n')
        
        # Look for summary lines
        summary_lines = []
        for line in lines:
            if any(keyword in line for keyword in ['Total', 'Status:', 'CRITICAL', 'violations', 'vulnerabilities']):
                summary_lines.append(line.strip())
        
        if summary_lines:
            return ' | '.join(summary_lines[:3])  # Top 3 most important lines
        else:
            return "Check failed - see full output"
    
    def _generate_master_report(self):
        """Generate comprehensive master verification report"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'project_root': str(self.project_root),
            'overall_status': 'PASS' if self.overall_status else 'FAIL',
            'verification_results': self.results,
            'summary': self._generate_summary(),
            'recommendations': self._generate_recommendations()
        }
        
        # Save master report
        report_path = self.verification_dir / 'master_verification_report.json'
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\n📊 Master Verification Report saved to: {report_path}")
    
    def _generate_summary(self) -> Dict:
        """Generate summary statistics"""
        total_checks = len(self.results)
        passed_checks = sum(1 for r in self.results.values() if r['status'] == 'PASS')
        failed_checks = sum(1 for r in self.results.values() if r['status'] == 'FAIL')
        error_checks = sum(1 for r in self.results.values() if r['status'] == 'ERROR')
        
        return {
            'total_verifications': total_checks,
            'passed': passed_checks,
            'failed': failed_checks,
            'errors': error_checks,
            'success_rate': f"{(passed_checks/total_checks*100):.1f}%" if total_checks > 0 else "0%"
        }
    
    def _generate_recommendations(self) -> List[str]:
        """Generate actionable recommendations based on results"""
        recommendations = []
        
        for name, result in self.results.items():
            if result['status'] == 'FAIL':
                if 'secrets' in name.lower():
                    recommendations.append("Remove all hardcoded secrets and use environment variables")
                elif 'sql' in name.lower():
                    recommendations.append("Replace string concatenation with parameterized queries")
                elif 'auth' in name.lower():
                    recommendations.append("Fix authentication system and secure all endpoints")
                elif 'input' in name.lower():
                    recommendations.append("Implement input validation on all API endpoints")
                elif 'error' in name.lower():
                    recommendations.append("Replace bare except clauses with specific exception handling")
                elif 'dangerous' in name.lower():
                    recommendations.append("Remove unsafe functions like eval(), exec(), and subprocess calls")
        
        if not recommendations:
            recommendations.append("All security checks passed - maintain current security practices")
        
        return recommendations[:10]  # Top 10 recommendations

def main():
    """Run master verification"""
    verifier = MasterVerification()
    results = verifier.run_all_verifications()
    
    print("\n" + "=" * 60)
    print("📊 MASTER VERIFICATION RESULTS")
    print("=" * 60)
    
    summary = verifier._generate_summary()
    print(f"Total verifications: {summary['total_verifications']}")
    print(f"Passed: {summary['passed']}")
    print(f"Failed: {summary['failed']}")
    print(f"Errors: {summary['errors']}")
    print(f"Success rate: {summary['success_rate']}")
    
    print(f"\nOverall status: {'✅ PASS' if verifier.overall_status else '❌ FAIL'}")
    
    if not verifier.overall_status:
        print("\n🚨 CRITICAL ISSUES FOUND:")
        recommendations = verifier._generate_recommendations()
        for i, rec in enumerate(recommendations[:5], 1):
            print(f"{i}. {rec}")
    
    return verifier.overall_status

if __name__ == '__main__':
    success = main()
    exit(0 if success else 1)