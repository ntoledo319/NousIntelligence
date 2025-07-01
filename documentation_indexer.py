#!/usr/bin/env python3
"""
NOUS Documentation Indexer and Assessment Tool
Comprehensive analysis of all documentation to identify gaps and quality issues
"""

import os
import re
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Set, Optional, Tuple
from dataclasses import dataclass, asdict
import sqlite3


@dataclass
class DocumentationFile:
    """Represents a documentation file and its metadata"""
    path: str
    type: str  # README, API, GUIDE, REFERENCE, etc.
    size_kb: float
    last_modified: str
    word_count: int
    line_count: int
    has_toc: bool
    has_examples: bool
    has_images: bool
    quality_score: float
    issues: List[str]
    sections: List[str]
    links: List[str]
    outdated_references: List[str]


@dataclass
class DocumentationGap:
    """Represents missing or inadequate documentation"""
    category: str
    description: str
    priority: str  # HIGH, MEDIUM, LOW
    suggested_files: List[str]
    reason: str


class DocumentationIndexer:
    """Comprehensive documentation analysis and indexing system"""
    
    def __init__(self):
        self.project_root = Path('.')
        self.docs_files: List[DocumentationFile] = []
        self.gaps: List[DocumentationGap] = []
        self.analysis_results: Dict[str, Any] = {}
        
        # Documentation categories
        self.doc_categories = {
            'README': ['README.md', 'readme.md'],
            'API': ['API_*.md', 'api/*.md', '*_API.md'],
            'GUIDE': ['*_GUIDE.md', 'GUIDE_*.md', 'user-guide/*.md'],
            'REFERENCE': ['*_REFERENCE.md', 'REFERENCE_*.md'],
            'ARCHITECTURE': ['ARCHITECTURE.md', 'DESIGN.md', 'STRUCTURE.md'],
            'DEPLOYMENT': ['DEPLOYMENT*.md', 'INSTALL*.md', 'SETUP*.md'],
            'SECURITY': ['SECURITY*.md', '*_SECURITY.md'],
            'FEATURES': ['FEATURES*.md', '*_FEATURES.md'],
            'CHANGELOG': ['CHANGELOG.md', 'HISTORY.md', 'RELEASES.md'],
            'CONTRIBUTING': ['CONTRIBUTING.md', 'DEVELOPMENT.md'],
            'LICENSE': ['LICENSE', 'LICENSE.md'],
            'CODE_OF_CONDUCT': ['CODE_OF_CONDUCT.md']
        }
        
        # Expected documentation for comprehensive coverage
        self.required_docs = {
            'USER_ONBOARDING': 'Complete user onboarding and first-time setup guide',
            'DRONE_SWARM': 'Autonomous drone swarm system documentation',
            'SEED_ENGINE': 'SEED optimization engine comprehensive guide',
            'AI_SERVICES': 'AI services integration and cost optimization',
            'THERAPEUTIC_FEATURES': 'CBT/DBT/AA therapeutic features documentation',
            'AUTHENTICATION': 'Complete authentication system documentation',
            'DATABASE_SCHEMA': 'Database models and relationships documentation',
            'API_ENDPOINTS': 'Complete API endpoints with examples',
            'DEPLOYMENT_PROD': 'Production deployment comprehensive guide',
            'TROUBLESHOOTING': 'Common issues and troubleshooting guide',
            'DEVELOPER_SETUP': 'Developer environment setup guide',
            'TESTING': 'Testing framework and test execution guide',
            'PERFORMANCE': 'Performance optimization and monitoring',
            'SECURITY_AUDIT': 'Security features and audit procedures',
            'BACKUP_RECOVERY': 'Backup and disaster recovery procedures'
        }
    
    def run_comprehensive_index(self) -> Dict[str, Any]:
        """Run complete documentation indexing and analysis"""
        print("🔍 Starting comprehensive documentation analysis...")
        
        # Step 1: Discover all documentation files
        self._discover_documentation_files()
        
        # Step 2: Analyze each file
        self._analyze_documentation_quality()
        
        # Step 3: Identify gaps
        self._identify_documentation_gaps()
        
        # Step 4: Generate recommendations
        self._generate_recommendations()
        
        # Step 5: Create comprehensive report
        self._create_comprehensive_report()
        
        return self.analysis_results
    
    def _discover_documentation_files(self):
        """Discover all documentation files in the project"""
        print("📁 Discovering documentation files...")
        
        # Common documentation file patterns
        doc_patterns = [
            '*.md', '*.rst', '*.txt', '*.adoc',
            'README*', 'CHANGELOG*', 'LICENSE*',
            'CONTRIBUTING*', 'CODE_OF_CONDUCT*'
        ]
        
        # Search in common documentation directories
        search_dirs = ['.', 'docs', 'documentation', 'guides', 'wiki']
        
        for search_dir in search_dirs:
            if os.path.exists(search_dir):
                for root, dirs, files in os.walk(search_dir):
                    # Skip certain directories
                    dirs[:] = [d for d in dirs if not d.startswith('.') and 
                              d not in ['__pycache__', 'node_modules', 'venv']]
                    
                    for file in files:
                        file_path = os.path.join(root, file)
                        if self._is_documentation_file(file_path):
                            doc_file = self._analyze_file(file_path)
                            if doc_file:
                                self.docs_files.append(doc_file)
        
        print(f"📊 Found {len(self.docs_files)} documentation files")
    
    def _is_documentation_file(self, file_path: str) -> bool:
        """Check if file is a documentation file"""
        file_path = file_path.lower()
        
        # File extensions
        if any(file_path.endswith(ext) for ext in ['.md', '.rst', '.txt', '.adoc']):
            return True
        
        # Special files without extensions
        if any(name in os.path.basename(file_path).lower() for name in 
               ['readme', 'license', 'changelog', 'contributing', 'code_of_conduct']):
            return True
        
        return False
    
    def _analyze_file(self, file_path: str) -> Optional[DocumentationFile]:
        """Analyze a single documentation file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Basic metrics
            stat = os.stat(file_path)
            size_kb = stat.st_size / 1024
            last_modified = datetime.fromtimestamp(stat.st_mtime).isoformat()
            word_count = len(content.split())
            line_count = len(content.splitlines())
            
            # Content analysis
            has_toc = bool(re.search(r'(?i)(table of contents|toc)', content))
            has_examples = bool(re.search(r'(?i)(example|```)', content))
            has_images = bool(re.search(r'!\[.*\]\(.*\)', content))
            
            # Extract sections
            sections = re.findall(r'^#+\s+(.+)$', content, re.MULTILINE)
            
            # Extract links
            links = re.findall(r'\[([^\]]+)\]\(([^)]+)\)', content)
            
            # Quality assessment
            quality_score, issues = self._assess_quality(content, file_path)
            
            # Check for outdated references
            outdated_refs = self._find_outdated_references(content)
            
            # Determine file type
            file_type = self._determine_file_type(file_path)
            
            return DocumentationFile(
                path=file_path,
                type=file_type,
                size_kb=size_kb,
                last_modified=last_modified,
                word_count=word_count,
                line_count=line_count,
                has_toc=has_toc,
                has_examples=has_examples,
                has_images=has_images,
                quality_score=quality_score,
                issues=issues,
                sections=sections,
                links=[link[1] for link in links],
                outdated_references=outdated_refs
            )
        
        except Exception as e:
            print(f"❌ Error analyzing {file_path}: {e}")
            return None
    
    def _assess_quality(self, content: str, file_path: str) -> Tuple[float, List[str]]:
        """Assess documentation quality and identify issues"""
        score = 100.0
        issues = []
        
        # Length checks
        if len(content.strip()) < 100:
            score -= 30
            issues.append("Too short - needs more content")
        
        # Structure checks
        if not re.search(r'^#', content, re.MULTILINE):
            score -= 20
            issues.append("Missing main heading")
        
        # Content checks
        if 'TODO' in content.upper() or 'FIXME' in content.upper():
            score -= 15
            issues.append("Contains TODO/FIXME items")
        
        # Link checks
        broken_links = self._check_broken_links(content)
        if broken_links:
            score -= 10 * len(broken_links)
            issues.extend([f"Broken link: {link}" for link in broken_links])
        
        # Code example checks for API docs
        if 'api' in file_path.lower() and not re.search(r'```', content):
            score -= 25
            issues.append("API documentation missing code examples")
        
        # Recent update check
        if self._is_likely_outdated(content):
            score -= 20
            issues.append("Appears to be outdated")
        
        return max(0, score), issues
    
    def _check_broken_links(self, content: str) -> List[str]:
        """Check for broken internal links"""
        broken_links = []
        
        # Find markdown links
        links = re.findall(r'\[([^\]]+)\]\(([^)]+)\)', content)
        
        for link_text, link_url in links:
            # Check internal links
            if not link_url.startswith(('http', 'https', 'mailto')):
                # Remove anchors
                clean_url = link_url.split('#')[0]
                if clean_url and not os.path.exists(clean_url):
                    broken_links.append(link_url)
        
        return broken_links
    
    def _is_likely_outdated(self, content: str) -> bool:
        """Check if documentation appears outdated"""
        # Look for old dates
        current_year = datetime.now().year
        old_years = [str(year) for year in range(2020, current_year - 1)]
        
        for year in old_years:
            if year in content:
                return True
        
        # Look for deprecated technology references
        deprecated_tech = ['python 2', 'flask 0.', 'jquery 1.']
        for tech in deprecated_tech:
            if tech.lower() in content.lower():
                return True
        
        return False
    
    def _find_outdated_references(self, content: str) -> List[str]:
        """Find potentially outdated references"""
        outdated = []
        
        # Look for old version references
        version_patterns = [
            r'python\s+[12]\.\d+',
            r'flask\s+0\.\d+',
            r'node\s+\d+\.\d+',
        ]
        
        for pattern in version_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            outdated.extend(matches)
        
        return outdated
    
    def _determine_file_type(self, file_path: str) -> str:
        """Determine the type of documentation file"""
        file_name = os.path.basename(file_path).upper()
        
        for doc_type, patterns in self.doc_categories.items():
            for pattern in patterns:
                if pattern.upper().replace('*', '') in file_name:
                    return doc_type
        
        return 'OTHER'
    
    def _analyze_documentation_quality(self):
        """Analyze overall documentation quality"""
        print("📊 Analyzing documentation quality...")
        
        total_files = len(self.docs_files)
        if total_files == 0:
            return
        
        # Calculate aggregate metrics
        total_words = sum(doc.word_count for doc in self.docs_files)
        avg_quality = sum(doc.quality_score for doc in self.docs_files) / total_files
        files_with_issues = len([doc for doc in self.docs_files if doc.issues])
        
        # Categorize by type
        by_type = {}
        for doc in self.docs_files:
            if doc.type not in by_type:
                by_type[doc.type] = []
            by_type[doc.type].append(doc)
        
        self.analysis_results.update({
            'total_files': total_files,
            'total_words': total_words,
            'average_quality_score': avg_quality,
            'files_with_issues': files_with_issues,
            'by_type': {doc_type: len(docs) for doc_type, docs in by_type.items()},
            'quality_distribution': self._get_quality_distribution()
        })
    
    def _get_quality_distribution(self) -> Dict[str, int]:
        """Get distribution of quality scores"""
        distribution = {'excellent': 0, 'good': 0, 'fair': 0, 'poor': 0}
        
        for doc in self.docs_files:
            if doc.quality_score >= 80:
                distribution['excellent'] += 1
            elif doc.quality_score >= 60:
                distribution['good'] += 1
            elif doc.quality_score >= 40:
                distribution['fair'] += 1
            else:
                distribution['poor'] += 1
        
        return distribution
    
    def _identify_documentation_gaps(self):
        """Identify missing or inadequate documentation"""
        print("🔍 Identifying documentation gaps...")
        
        existing_types = set(doc.type for doc in self.docs_files)
        
        # Check for required documentation types
        for req_type, description in self.required_docs.items():
            if not self._has_adequate_coverage(req_type):
                gap = DocumentationGap(
                    category=req_type,
                    description=description,
                    priority=self._get_gap_priority(req_type),
                    suggested_files=self._suggest_files_for_gap(req_type),
                    reason=self._get_gap_reason(req_type)
                )
                self.gaps.append(gap)
        
        # Check for missing standard documentation
        standard_docs = ['README', 'API', 'DEPLOYMENT', 'CONTRIBUTING']
        for standard in standard_docs:
            if standard not in existing_types:
                gap = DocumentationGap(
                    category=standard,
                    description=f"Missing {standard} documentation",
                    priority='HIGH',
                    suggested_files=[f"{standard}.md"],
                    reason=f"Standard {standard} documentation is missing"
                )
                self.gaps.append(gap)
    
    def _has_adequate_coverage(self, doc_type: str) -> bool:
        """Check if documentation type has adequate coverage"""
        # Define minimum requirements for each type
        min_requirements = {
            'USER_ONBOARDING': 500,  # words
            'DRONE_SWARM': 800,
            'SEED_ENGINE': 1000,
            'AI_SERVICES': 600,
            'THERAPEUTIC_FEATURES': 800,
            'AUTHENTICATION': 400,
            'DATABASE_SCHEMA': 300,
            'API_ENDPOINTS': 1000,
            'DEPLOYMENT_PROD': 600,
            'TROUBLESHOOTING': 400,
            'DEVELOPER_SETUP': 300,
            'TESTING': 200,
            'PERFORMANCE': 300,
            'SECURITY_AUDIT': 400,
            'BACKUP_RECOVERY': 200
        }
        
        min_words = min_requirements.get(doc_type, 200)
        
        # Check if we have relevant documentation
        relevant_docs = self._find_relevant_docs(doc_type)
        total_words = sum(doc.word_count for doc in relevant_docs)
        
        return total_words >= min_words and len(relevant_docs) > 0
    
    def _find_relevant_docs(self, doc_type: str) -> List[DocumentationFile]:
        """Find documentation files relevant to a specific type"""
        keywords = {
            'USER_ONBOARDING': ['onboard', 'setup', 'getting', 'started', 'first'],
            'DRONE_SWARM': ['drone', 'swarm', 'autonomous'],
            'SEED_ENGINE': ['seed', 'optimization', 'engine'],
            'AI_SERVICES': ['ai', 'artificial', 'intelligence', 'openai', 'gemini'],
            'THERAPEUTIC_FEATURES': ['cbt', 'dbt', 'therapeutic', 'mental', 'health'],
            'AUTHENTICATION': ['auth', 'login', 'oauth', 'security'],
            'DATABASE_SCHEMA': ['database', 'schema', 'models', 'sql'],
            'API_ENDPOINTS': ['api', 'endpoint', 'rest'],
            'DEPLOYMENT_PROD': ['deploy', 'production', 'server'],
            'TROUBLESHOOTING': ['troubleshoot', 'debug', 'problem', 'issue'],
            'DEVELOPER_SETUP': ['developer', 'development', 'setup'],
            'TESTING': ['test', 'testing', 'pytest'],
            'PERFORMANCE': ['performance', 'optimization', 'speed'],
            'SECURITY_AUDIT': ['security', 'audit', 'vulnerability'],
            'BACKUP_RECOVERY': ['backup', 'recovery', 'restore']
        }
        
        relevant_docs = []
        search_keywords = keywords.get(doc_type, [])
        
        for doc in self.docs_files:
            # Check path and sections for keywords
            doc_text = (doc.path + ' ' + ' '.join(doc.sections)).lower()
            if any(keyword in doc_text for keyword in search_keywords):
                relevant_docs.append(doc)
        
        return relevant_docs
    
    def _get_gap_priority(self, gap_type: str) -> str:
        """Determine priority for documentation gap"""
        high_priority = [
            'USER_ONBOARDING', 'API_ENDPOINTS', 'DEPLOYMENT_PROD',
            'AUTHENTICATION', 'SECURITY_AUDIT'
        ]
        
        medium_priority = [
            'DRONE_SWARM', 'SEED_ENGINE', 'AI_SERVICES',
            'THERAPEUTIC_FEATURES', 'TROUBLESHOOTING'
        ]
        
        if gap_type in high_priority:
            return 'HIGH'
        elif gap_type in medium_priority:
            return 'MEDIUM'
        else:
            return 'LOW'
    
    def _suggest_files_for_gap(self, gap_type: str) -> List[str]:
        """Suggest file names for documentation gaps"""
        suggestions = {
            'USER_ONBOARDING': ['docs/user-guide/onboarding.md', 'docs/getting-started.md'],
            'DRONE_SWARM': ['docs/drone-swarm-guide.md', 'docs/autonomous-agents.md'],
            'SEED_ENGINE': ['docs/seed-optimization-engine.md', 'docs/ai-learning-system.md'],
            'AI_SERVICES': ['docs/ai-integration-guide.md', 'docs/ai-cost-optimization.md'],
            'THERAPEUTIC_FEATURES': ['docs/therapeutic-features.md', 'docs/mental-health-support.md'],
            'AUTHENTICATION': ['docs/authentication-guide.md', 'docs/oauth-setup.md'],
            'DATABASE_SCHEMA': ['docs/database-schema.md', 'docs/data-models.md'],
            'API_ENDPOINTS': ['docs/api/complete-reference.md', 'docs/api-examples.md'],
            'DEPLOYMENT_PROD': ['docs/production-deployment.md', 'docs/server-setup.md'],
            'TROUBLESHOOTING': ['docs/troubleshooting.md', 'docs/common-issues.md'],
            'DEVELOPER_SETUP': ['docs/developer-setup.md', 'docs/development-environment.md'],
            'TESTING': ['docs/testing-guide.md', 'docs/test-framework.md'],
            'PERFORMANCE': ['docs/performance-optimization.md', 'docs/monitoring.md'],
            'SECURITY_AUDIT': ['docs/security-procedures.md', 'docs/security-checklist.md'],
            'BACKUP_RECOVERY': ['docs/backup-procedures.md', 'docs/disaster-recovery.md']
        }
        
        return suggestions.get(gap_type, [f'docs/{gap_type.lower().replace("_", "-")}.md'])
    
    def _get_gap_reason(self, gap_type: str) -> str:
        """Get reason for documentation gap"""
        reasons = {
            'USER_ONBOARDING': 'New users need clear guidance for first-time setup and feature discovery',
            'DRONE_SWARM': 'Autonomous drone system is a key feature but lacks comprehensive documentation',
            'SEED_ENGINE': 'SEED optimization engine needs detailed technical documentation',
            'AI_SERVICES': 'AI integration and cost optimization features need better documentation',
            'THERAPEUTIC_FEATURES': 'Mental health features (CBT/DBT/AA) need comprehensive user guides',
            'AUTHENTICATION': 'Security-critical authentication system needs complete documentation',
            'DATABASE_SCHEMA': 'Database structure and relationships need clear documentation',
            'API_ENDPOINTS': 'API documentation is incomplete and needs examples',
            'DEPLOYMENT_PROD': 'Production deployment procedures need comprehensive guide',
            'TROUBLESHOOTING': 'Common issues and solutions need centralized documentation',
            'DEVELOPER_SETUP': 'Developer onboarding needs streamlined documentation',
            'TESTING': 'Testing procedures and framework need documentation',
            'PERFORMANCE': 'Performance optimization techniques need documentation',
            'SECURITY_AUDIT': 'Security procedures and audit checklists need documentation',
            'BACKUP_RECOVERY': 'Backup and recovery procedures need documentation'
        }
        
        return reasons.get(gap_type, f'{gap_type} documentation is missing or inadequate')
    
    def _generate_recommendations(self):
        """Generate actionable recommendations"""
        print("💡 Generating recommendations...")
        
        recommendations = []
        
        # Priority-based recommendations
        high_priority_gaps = [gap for gap in self.gaps if gap.priority == 'HIGH']
        medium_priority_gaps = [gap for gap in self.gaps if gap.priority == 'MEDIUM']
        
        # Quality improvement recommendations
        poor_quality_docs = [doc for doc in self.docs_files if doc.quality_score < 40]
        
        # Generate specific recommendations
        if high_priority_gaps:
            recommendations.append({
                'type': 'URGENT',
                'action': 'Create missing critical documentation',
                'details': [f"Create {gap.suggested_files[0]} for {gap.description}" 
                           for gap in high_priority_gaps[:5]]
            })
        
        if poor_quality_docs:
            recommendations.append({
                'type': 'QUALITY',
                'action': 'Improve low-quality documentation',
                'details': [f"Improve {doc.path} (Score: {doc.quality_score:.1f})" 
                           for doc in poor_quality_docs[:3]]
            })
        
        if medium_priority_gaps:
            recommendations.append({
                'type': 'ENHANCEMENT',
                'action': 'Add comprehensive feature documentation',
                'details': [f"Create {gap.suggested_files[0]} for {gap.description}" 
                           for gap in medium_priority_gaps[:3]]
            })
        
        self.analysis_results['recommendations'] = recommendations
    
    def _create_comprehensive_report(self):
        """Create comprehensive documentation analysis report"""
        print("📋 Creating comprehensive report...")
        
        # Save detailed results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # JSON report
        report_data = {
            'timestamp': timestamp,
            'analysis_results': self.analysis_results,
            'documentation_files': [asdict(doc) for doc in self.docs_files],
            'gaps': [asdict(gap) for gap in self.gaps]
        }
        
        with open(f'documentation_analysis_{timestamp}.json', 'w') as f:
            json.dump(report_data, f, indent=2)
        
        # Markdown report
        self._create_markdown_report(timestamp)
        
        print(f"📊 Reports created:")
        print(f"  - documentation_analysis_{timestamp}.json")
        print(f"  - DOCUMENTATION_INDEX_REPORT.md")
    
    def _create_markdown_report(self, timestamp: str):
        """Create markdown documentation report"""
        report = f"""# NOUS Documentation Index & Analysis Report

**Generated:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
**Analysis ID:** {timestamp}

## Executive Summary

- **Total Documentation Files:** {self.analysis_results.get('total_files', 0)}
- **Total Word Count:** {self.analysis_results.get('total_words', 0):,}
- **Average Quality Score:** {self.analysis_results.get('average_quality_score', 0):.1f}/100
- **Files with Issues:** {self.analysis_results.get('files_with_issues', 0)}
- **Documentation Gaps Identified:** {len(self.gaps)}

## Quality Distribution

"""
        
        quality_dist = self.analysis_results.get('quality_distribution', {})
        for level, count in quality_dist.items():
            report += f"- **{level.title()}:** {count} files\n"
        
        report += f"""

## Documentation by Type

"""
        
        by_type = self.analysis_results.get('by_type', {})
        for doc_type, count in sorted(by_type.items()):
            report += f"- **{doc_type}:** {count} files\n"
        
        report += f"""

## Critical Documentation Gaps

"""
        
        high_priority_gaps = [gap for gap in self.gaps if gap.priority == 'HIGH']
        for gap in high_priority_gaps:
            report += f"""
### {gap.category}
**Priority:** {gap.priority}
**Description:** {gap.description}
**Reason:** {gap.reason}
**Suggested Files:**
"""
            for suggested_file in gap.suggested_files:
                report += f"- {suggested_file}\n"
        
        report += f"""

## Quality Issues by File

"""
        
        issues_files = [doc for doc in self.docs_files if doc.issues]
        for doc in sorted(issues_files, key=lambda x: x.quality_score):
            report += f"""
### {doc.path}
**Quality Score:** {doc.quality_score:.1f}/100
**Issues:**
"""
            for issue in doc.issues:
                report += f"- {issue}\n"
        
        report += f"""

## Recommendations

"""
        
        recommendations = self.analysis_results.get('recommendations', [])
        for i, rec in enumerate(recommendations, 1):
            report += f"""
### {i}. {rec['action']} ({rec['type']})
"""
            for detail in rec['details']:
                report += f"- {detail}\n"
        
        report += f"""

## Drone Swarm Action Plan

The following actions will be executed by the documentation drone swarm:

### Phase 1: Critical Gap Resolution (HIGH Priority)
"""
        for gap in high_priority_gaps:
            report += f"- Create comprehensive {gap.suggested_files[0]}\n"
        
        report += f"""

### Phase 2: Quality Improvement
"""
        poor_docs = [doc for doc in self.docs_files if doc.quality_score < 60][:5]
        for doc in poor_docs:
            report += f"- Improve {doc.path} (Current score: {doc.quality_score:.1f})\n"
        
        report += f"""

### Phase 3: Enhancement Documentation
"""
        medium_gaps = [gap for gap in self.gaps if gap.priority == 'MEDIUM'][:3]
        for gap in medium_gaps:
            report += f"- Create {gap.suggested_files[0]}\n"
        
        report += f"""

---
*This report was generated by the NOUS Documentation Indexer*
*Use the drone swarm system to automatically implement these improvements*
"""
        
        with open('DOCUMENTATION_INDEX_REPORT.md', 'w') as f:
            f.write(report)
    
    def create_drone_swarm_tasks(self) -> List[Dict[str, Any]]:
        """Create tasks for the drone swarm to execute"""
        tasks = []
        
        # High priority documentation creation tasks
        high_priority_gaps = [gap for gap in self.gaps if gap.priority == 'HIGH']
        for gap in high_priority_gaps:
            for suggested_file in gap.suggested_files:
                tasks.append({
                    'type': 'CREATE_DOCUMENTATION',
                    'priority': 'HIGH',
                    'target_file': suggested_file,
                    'category': gap.category,
                    'description': gap.description,
                    'template_type': self._get_template_type(gap.category),
                    'estimated_effort': 'HIGH'
                })
        
        # Quality improvement tasks
        poor_quality_docs = [doc for doc in self.docs_files if doc.quality_score < 60]
        for doc in poor_quality_docs:
            tasks.append({
                'type': 'IMPROVE_DOCUMENTATION',
                'priority': 'MEDIUM',
                'target_file': doc.path,
                'current_score': doc.quality_score,
                'issues': doc.issues,
                'estimated_effort': 'MEDIUM'
            })
        
        return tasks
    
    def _get_template_type(self, category: str) -> str:
        """Get template type for documentation category"""
        template_map = {
            'USER_ONBOARDING': 'user_guide',
            'API_ENDPOINTS': 'api_reference',
            'DEPLOYMENT_PROD': 'deployment_guide',
            'DRONE_SWARM': 'technical_guide',
            'SEED_ENGINE': 'technical_guide',
            'AI_SERVICES': 'integration_guide',
            'THERAPEUTIC_FEATURES': 'user_guide',
            'AUTHENTICATION': 'technical_guide',
            'DATABASE_SCHEMA': 'reference',
            'TROUBLESHOOTING': 'troubleshooting_guide',
            'DEVELOPER_SETUP': 'setup_guide',
            'TESTING': 'technical_guide',
            'PERFORMANCE': 'optimization_guide',
            'SECURITY_AUDIT': 'security_guide',
            'BACKUP_RECOVERY': 'procedures_guide'
        }
        
        return template_map.get(category, 'general_guide')


def main():
    """Main execution function"""
    print("🚀 NOUS Documentation Indexer - Comprehensive Analysis")
    print("=" * 60)
    
    indexer = DocumentationIndexer()
    results = indexer.run_comprehensive_index()
    
    print("\n✅ Documentation analysis complete!")
    print(f"📊 {results.get('total_files', 0)} files analyzed")
    print(f"🔍 {len(indexer.gaps)} gaps identified")
    print(f"📈 Average quality score: {results.get('average_quality_score', 0):.1f}/100")
    
    # Create drone swarm tasks
    tasks = indexer.create_drone_swarm_tasks()
    
    print(f"\n🤖 {len(tasks)} tasks created for drone swarm execution")
    print("📋 See DOCUMENTATION_INDEX_REPORT.md for detailed analysis")
    
    return indexer, tasks


if __name__ == "__main__":
    main()