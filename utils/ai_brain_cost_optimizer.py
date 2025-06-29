"""
AI Brain Cost Optimizer - Intelligent Cost Reduction System
Integrates AI brain reasoning for maximum cost efficiency
"""

import os
import json
import time
import hashlib
import logging
import sqlite3
import numpy as np
from typing import Dict, List, Any, Optional, Tuple, Union
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import re

logger = logging.getLogger(__name__)

class QueryComplexity(Enum):
    TRIVIAL = "trivial"      # Local templates only
    SIMPLE = "simple"        # Free models sufficient
    MODERATE = "moderate"    # Mid-tier models
    COMPLEX = "complex"      # Premium models
    CRITICAL = "critical"    # Best available models

class UserEmotionalState(Enum):
    CALM = "calm"
    STRESSED = "stressed"
    URGENT = "urgent"
    CASUAL = "casual"
    THERAPEUTIC = "therapeutic"

@dataclass
class QueryAnalysis:
    complexity: QueryComplexity
    emotional_state: UserEmotionalState
    user_familiarity: float  # 0-1 scale
    topic_category: str
    predicted_response_length: int
    cacheable: bool
    batch_candidate: bool
    quality_threshold: float

@dataclass
class CostOptimization:
    use_local: bool
    provider: str
    model: str
    estimated_cost: float
    confidence: float
    reasoning: List[str]

class AIBrainCostOptimizer:
    """AI Brain-powered cost optimization system"""
    
    def __init__(self):
        self.cache_db_path = "ai_brain_optimizer.db"
        self.init_database()
        
        # Learning patterns
        self.user_patterns = {}
        self.conversation_flows = {}
        self.success_rates = {}
        self.cost_history = []
        
        # Local templates
        self.local_templates = self._init_smart_templates()
        self.pattern_cache = {}
        self.batch_queue = []
        
        # Performance tracking
        self.total_savings = 0.0
        self.local_response_rate = 0.0
        self.cache_hit_rate = 0.0
        
        logger.info("AI Brain Cost Optimizer initialized")

    def init_database(self):
        """Initialize comprehensive optimization database"""
        try:
            conn = sqlite3.connect(self.cache_db_path)
            
            # Query analysis history
            conn.execute('''
                CREATE TABLE IF NOT EXISTS query_analysis (
                    id INTEGER PRIMARY KEY,
                    query_hash TEXT,
                    complexity TEXT,
                    emotional_state TEXT,
                    user_id TEXT,
                    topic_category TEXT,
                    response_length INTEGER,
                    provider_used TEXT,
                    cost REAL,
                    satisfaction_score REAL,
                    created_at TIMESTAMP
                )
            ''')
            
            # Pattern recognition
            conn.execute('''
                CREATE TABLE IF NOT EXISTS conversation_patterns (
                    id INTEGER PRIMARY KEY,
                    pattern_type TEXT,
                    pattern_data TEXT,
                    frequency INTEGER DEFAULT 1,
                    success_rate REAL,
                    last_seen TIMESTAMP
                )
            ''')
            
            # User learning profiles
            conn.execute('''
                CREATE TABLE IF NOT EXISTS user_profiles (
                    user_id TEXT PRIMARY KEY,
                    preferred_complexity TEXT,
                    avg_satisfaction REAL,
                    topic_preferences TEXT,
                    response_style TEXT,
                    total_interactions INTEGER DEFAULT 0,
                    last_updated TIMESTAMP
                )
            ''')
            
            # Cost savings tracking
            conn.execute('''
                CREATE TABLE IF NOT EXISTS cost_savings (
                    id INTEGER PRIMARY KEY,
                    optimization_type TEXT,
                    original_cost REAL,
                    optimized_cost REAL,
                    savings REAL,
                    timestamp TIMESTAMP
                )
            ''')
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Database initialization failed: {e}")

    def _init_smart_templates(self) -> Dict[str, Dict[str, str]]:
        """Initialize intelligent local response templates"""
        return {
            "greetings": {
                "patterns": ["hello", "hi", "hey", "good morning", "good afternoon"],
                "responses": [
                    "Hello! I'm here to help you today. What can I assist you with?",
                    "Hi there! How can I support you?",
                    "Good to see you! What would you like to work on?",
                    "Hello! I'm ready to help. What's on your mind?"
                ]
            },
            "gratitude": {
                "patterns": ["thank you", "thanks", "appreciate", "grateful"],
                "responses": [
                    "You're very welcome! I'm glad I could help.",
                    "Happy to assist! Is there anything else you need?",
                    "My pleasure! Feel free to ask if you have more questions.",
                    "You're welcome! I'm here whenever you need support."
                ]
            },
            "simple_questions": {
                "patterns": ["what is", "define", "meaning of", "explain"],
                "context_required": True
            },
            "status_checks": {
                "patterns": ["how are you", "are you working", "status", "online"],
                "responses": [
                    "I'm working perfectly and ready to help! What can I do for you?",
                    "All systems running smoothly! How can I assist you today?",
                    "I'm here and ready to help with whatever you need."
                ]
            },
            "therapeutic_check_ins": {
                "patterns": ["feeling", "mood", "anxious", "stressed", "worried", "sad"],
                "responses": [
                    "I hear you sharing about your feelings. That takes courage. Would you like to talk more about what you're experiencing?",
                    "Thank you for being open about how you're feeling. I'm here to support you. What would be most helpful right now?",
                    "It sounds like you're going through something difficult. I'm here to listen and help however I can."
                ]
            }
        }

    def analyze_query(self, query: str, user_id: str = None, context: Dict[str, Any] = None) -> QueryAnalysis:
        """AI brain-powered query analysis"""
        
        # Complexity analysis using multiple signals
        complexity = self._assess_complexity(query, context)
        
        # Emotional state detection
        emotional_state = self._detect_emotional_state(query)
        
        # User familiarity assessment
        user_familiarity = self._assess_user_familiarity(user_id, query)
        
        # Topic categorization
        topic_category = self._categorize_topic(query)
        
        # Response length prediction
        predicted_length = self._predict_response_length(query, complexity)
        
        # Cacheability assessment
        cacheable = self._assess_cacheability(query, topic_category)
        
        # Batch processing candidate
        batch_candidate = self._assess_batch_potential(query)
        
        # Quality threshold based on context
        quality_threshold = self._determine_quality_threshold(
            complexity, emotional_state, topic_category
        )
        
        return QueryAnalysis(
            complexity=complexity,
            emotional_state=emotional_state,
            user_familiarity=user_familiarity,
            topic_category=topic_category,
            predicted_response_length=predicted_length,
            cacheable=cacheable,
            batch_candidate=batch_candidate,
            quality_threshold=quality_threshold
        )

    def _assess_complexity(self, query: str, context: Dict[str, Any] = None) -> QueryComplexity:
        """Assess query complexity using AI brain reasoning"""
        
        # Length and structure analysis
        word_count = len(query.split())
        has_complex_syntax = bool(re.search(r'[;,].*[;,]', query))
        
        # Keyword-based complexity signals
        complex_keywords = [
            'analyze', 'compare', 'evaluate', 'research', 'investigate',
            'comprehensive', 'detailed', 'in-depth', 'systematic'
        ]
        
        moderate_keywords = [
            'explain', 'describe', 'summarize', 'outline', 'list'
        ]
        
        simple_keywords = [
            'what is', 'how to', 'when', 'where', 'who'
        ]
        
        trivial_keywords = [
            'hello', 'hi', 'thanks', 'status', 'are you'
        ]
        
        query_lower = query.lower()
        
        # Complexity scoring
        complexity_score = 0
        
        if any(keyword in query_lower for keyword in complex_keywords):
            complexity_score += 3
        elif any(keyword in query_lower for keyword in moderate_keywords):
            complexity_score += 2
        elif any(keyword in query_lower for keyword in simple_keywords):
            complexity_score += 1
        elif any(keyword in query_lower for keyword in trivial_keywords):
            complexity_score = 0
        
        # Adjust based on length and structure
        if word_count > 50:
            complexity_score += 1
        if has_complex_syntax:
            complexity_score += 1
        
        # Context-based adjustments
        if context:
            if context.get('requires_reasoning', False):
                complexity_score += 2
            if context.get('multi_step', False):
                complexity_score += 1
        
        # Map to complexity enum
        if complexity_score >= 5:
            return QueryComplexity.CRITICAL
        elif complexity_score >= 3:
            return QueryComplexity.COMPLEX
        elif complexity_score >= 2:
            return QueryComplexity.MODERATE
        elif complexity_score >= 1:
            return QueryComplexity.SIMPLE
        else:
            return QueryComplexity.TRIVIAL

    def _detect_emotional_state(self, query: str) -> UserEmotionalState:
        """Detect user emotional state from query"""
        query_lower = query.lower()
        
        stress_indicators = ['urgent', 'asap', 'emergency', 'help me', 'stressed', 'panic']
        therapeutic_indicators = ['anxious', 'depressed', 'sad', 'worried', 'therapy', 'counseling']
        casual_indicators = ['just wondering', 'curious', 'by the way', 'randomly']
        
        if any(indicator in query_lower for indicator in stress_indicators):
            return UserEmotionalState.STRESSED
        elif any(indicator in query_lower for indicator in therapeutic_indicators):
            return UserEmotionalState.THERAPEUTIC
        elif any(indicator in query_lower for indicator in casual_indicators):
            return UserEmotionalState.CASUAL
        elif '!' in query or query.isupper():
            return UserEmotionalState.URGENT
        else:
            return UserEmotionalState.CALM

    def _assess_user_familiarity(self, user_id: str, query: str) -> float:
        """Assess user familiarity with topic based on history"""
        if not user_id:
            return 0.5  # Default for anonymous users
        
        try:
            conn = sqlite3.connect(self.cache_db_path)
            cursor = conn.cursor()
            
            # Get user interaction history for similar topics
            cursor.execute('''
                SELECT COUNT(*), AVG(satisfaction_score)
                FROM query_analysis 
                WHERE user_id = ? AND topic_category = ?
            ''', (user_id, self._categorize_topic(query)))
            
            result = cursor.fetchone()
            conn.close()
            
            if result and result[0] > 0:
                interaction_count, avg_satisfaction = result
                # Higher familiarity = more interactions + higher satisfaction
                familiarity = min(1.0, (interaction_count / 10) * (avg_satisfaction or 0.5))
                return familiarity
            
        except Exception as e:
            logger.error(f"Error assessing user familiarity: {e}")
        
        return 0.3  # Low familiarity for new topics

    def _categorize_topic(self, query: str) -> str:
        """Categorize query topic for pattern matching"""
        query_lower = query.lower()
        
        categories = {
            'technical': ['code', 'programming', 'api', 'database', 'server', 'bug', 'error'],
            'therapeutic': ['therapy', 'mental health', 'depression', 'anxiety', 'stress', 'coping'],
            'research': ['research', 'study', 'analyze', 'data', 'statistics', 'scientific'],
            'personal': ['feeling', 'relationship', 'family', 'work', 'career', 'life'],
            'creative': ['write', 'design', 'art', 'music', 'creative', 'story'],
            'business': ['business', 'finance', 'money', 'investment', 'startup', 'marketing'],
            'health': ['health', 'exercise', 'diet', 'medical', 'wellness', 'fitness'],
            'education': ['learn', 'study', 'school', 'course', 'education', 'tutorial']
        }
        
        for category, keywords in categories.items():
            if any(keyword in query_lower for keyword in keywords):
                return category
        
        return 'general'

    def _predict_response_length(self, query: str, complexity: QueryComplexity) -> int:
        """Predict optimal response length"""
        base_lengths = {
            QueryComplexity.TRIVIAL: 50,
            QueryComplexity.SIMPLE: 150,
            QueryComplexity.MODERATE: 300,
            QueryComplexity.COMPLEX: 600,
            QueryComplexity.CRITICAL: 1000
        }
        
        base_length = base_lengths[complexity]
        
        # Adjust based on query characteristics
        if '?' in query:
            base_length += 100  # Questions need more detail
        if 'explain' in query.lower():
            base_length += 200  # Explanations are longer
        if 'list' in query.lower():
            base_length += 150  # Lists need structure
        
        return base_length

    def _assess_cacheability(self, query: str, topic_category: str) -> bool:
        """Assess if query response should be cached"""
        
        # Non-cacheable patterns
        non_cacheable = [
            'current', 'today', 'now', 'latest', 'recent',
            'my', 'personal', 'i am', 'i feel'
        ]
        
        # Highly cacheable patterns
        cacheable = [
            'what is', 'define', 'explain', 'how to',
            'meaning of', 'difference between'
        ]
        
        query_lower = query.lower()
        
        if any(pattern in query_lower for pattern in non_cacheable):
            return False
        
        if any(pattern in query_lower for pattern in cacheable):
            return True
        
        # Topic-based cacheability
        if topic_category in ['research', 'education', 'technical']:
            return True
        
        return False

    def _assess_batch_potential(self, query: str) -> bool:
        """Assess if query could be batched with others"""
        
        # Queries that benefit from batching
        batch_patterns = [
            'compare', 'difference between', 'pros and cons',
            'list of', 'examples of', 'types of'
        ]
        
        query_lower = query.lower()
        return any(pattern in query_lower for pattern in batch_patterns)

    def _determine_quality_threshold(self, complexity: QueryComplexity, 
                                   emotional_state: UserEmotionalState, 
                                   topic_category: str) -> float:
        """Determine quality threshold based on context"""
        
        base_thresholds = {
            QueryComplexity.TRIVIAL: 0.3,
            QueryComplexity.SIMPLE: 0.5,
            QueryComplexity.MODERATE: 0.7,
            QueryComplexity.COMPLEX: 0.8,
            QueryComplexity.CRITICAL: 0.9
        }
        
        threshold = base_thresholds[complexity]
        
        # Adjust for emotional state
        if emotional_state == UserEmotionalState.THERAPEUTIC:
            threshold += 0.1  # Higher quality for therapeutic
        elif emotional_state == UserEmotionalState.STRESSED:
            threshold += 0.05  # Slightly higher for stressed users
        elif emotional_state == UserEmotionalState.CASUAL:
            threshold -= 0.1  # Lower quality acceptable for casual
        
        # Adjust for topic
        if topic_category in ['therapeutic', 'health', 'research']:
            threshold += 0.1  # Higher quality for important topics
        
        return min(0.95, max(0.2, threshold))

    def optimize_request(self, query: str, user_id: str = None, 
                        context: Dict[str, Any] = None) -> CostOptimization:
        """AI brain-powered request optimization"""
        
        analysis = self.analyze_query(query, user_id, context)
        
        # Check for local template match first
        local_match = self._check_local_templates(query, analysis)
        if local_match:
            return CostOptimization(
                use_local=True,
                provider="local",
                model="template",
                estimated_cost=0.0,
                confidence=0.9,
                reasoning=["Matched local template", "Zero cost", "Instant response"]
            )
        
        # Check enhanced cache
        cache_result = self._check_intelligent_cache(query, analysis)
        if cache_result:
            return cache_result
        
        # Predictive response generation
        predictive_result = self._check_predictive_cache(query, analysis, user_id)
        if predictive_result:
            return predictive_result
        
        # Optimal provider selection
        return self._select_optimal_provider(analysis)

    def _check_local_templates(self, query: str, analysis: QueryAnalysis) -> Optional[CostOptimization]:
        """Check if query matches local templates"""
        
        if analysis.complexity != QueryComplexity.TRIVIAL:
            return None
        
        query_lower = query.lower()
        
        for template_type, template_data in self.local_templates.items():
            patterns = template_data.get('patterns', [])
            
            for pattern in patterns:
                if pattern in query_lower:
                    return CostOptimization(
                        use_local=True,
                        provider="local",
                        model=f"template_{template_type}",
                        estimated_cost=0.0,
                        confidence=0.85,
                        reasoning=[f"Matched {template_type} template", "Zero cost", "Instant response"]
                    )
        
        return None

    def _check_intelligent_cache(self, query: str, analysis: QueryAnalysis) -> Optional[CostOptimization]:
        """Check intelligent cache with similarity matching"""
        
        if not analysis.cacheable:
            return None
        
        try:
            conn = sqlite3.connect(self.cache_db_path)
            cursor = conn.cursor()
            
            # Look for similar cached queries
            cursor.execute('''
                SELECT query_hash, complexity, provider_used, cost, satisfaction_score
                FROM query_analysis 
                WHERE topic_category = ? AND satisfaction_score > ?
                ORDER BY satisfaction_score DESC, created_at DESC
                LIMIT 10
            ''', (analysis.topic_category, analysis.quality_threshold))
            
            results = cursor.fetchall()
            conn.close()
            
            if results:
                # Simple similarity check (could be enhanced with embeddings)
                for result in results:
                    if self._calculate_similarity(query, result[0]) > 0.8:
                        return CostOptimization(
                            use_local=True,
                            provider="cache",
                            model="cached_response",
                            estimated_cost=0.0,
                            confidence=0.8,
                            reasoning=["High similarity cache hit", "Zero cost", "Proven quality"]
                        )
            
        except Exception as e:
            logger.error(f"Cache check failed: {e}")
        
        return None

    def _check_predictive_cache(self, query: str, analysis: QueryAnalysis, 
                               user_id: str) -> Optional[CostOptimization]:
        """Check predictive cache based on conversation patterns"""
        
        if not user_id:
            return None
        
        try:
            # Look for conversation patterns
            pattern_key = f"{user_id}_{analysis.topic_category}"
            
            if pattern_key in self.conversation_flows:
                flow = self.conversation_flows[pattern_key]
                
                # Check if this query matches expected next question
                if self._matches_predicted_flow(query, flow):
                    return CostOptimization(
                        use_local=True,
                        provider="predictive",
                        model="conversation_flow",
                        estimated_cost=0.0,
                        confidence=0.75,
                        reasoning=["Predicted conversation flow", "Zero cost", "Pattern-based response"]
                    )
            
        except Exception as e:
            logger.error(f"Predictive cache check failed: {e}")
        
        return None

    def _select_optimal_provider(self, analysis: QueryAnalysis) -> CostOptimization:
        """Select optimal provider based on analysis"""
        
        # Provider selection logic based on complexity and requirements
        if analysis.complexity == QueryComplexity.CRITICAL:
            if analysis.topic_category == 'research':
                return CostOptimization(
                    use_local=False,
                    provider="openai",
                    model="gpt-4o",
                    estimated_cost=0.075,
                    confidence=0.95,
                    reasoning=["Critical research query", "Premium accuracy required"]
                )
            else:
                return CostOptimization(
                    use_local=False,
                    provider="openai",
                    model="gpt-4o-mini",
                    estimated_cost=0.002,
                    confidence=0.9,
                    reasoning=["Critical query", "Cost-effective premium model"]
                )
        
        elif analysis.complexity == QueryComplexity.COMPLEX:
            if analysis.emotional_state == UserEmotionalState.THERAPEUTIC:
                return CostOptimization(
                    use_local=False,
                    provider="gemini",
                    model="gemini-pro",
                    estimated_cost=0.0,
                    confidence=0.85,
                    reasoning=["Complex therapeutic query", "Free premium model"]
                )
            else:
                return CostOptimization(
                    use_local=False,
                    provider="openrouter",
                    model="meta-llama/llama-3.1-8b-instruct:free",
                    estimated_cost=0.0,
                    confidence=0.8,
                    reasoning=["Complex query", "Free capable model"]
                )
        
        elif analysis.complexity == QueryComplexity.MODERATE:
            return CostOptimization(
                use_local=False,
                provider="openrouter",
                model="meta-llama/llama-3.1-8b-instruct:free",
                estimated_cost=0.0,
                confidence=0.75,
                reasoning=["Moderate complexity", "Free model sufficient"]
            )
        
        else:  # SIMPLE
            return CostOptimization(
                use_local=False,
                provider="gemini",
                model="gemini-pro",
                estimated_cost=0.0,
                confidence=0.7,
                reasoning=["Simple query", "Free model adequate"]
            )

    def _calculate_similarity(self, query1: str, query2: str) -> float:
        """Calculate similarity between queries (simplified)"""
        # Simple word overlap similarity (could use embeddings for better results)
        words1 = set(query1.lower().split())
        words2 = set(query2.lower().split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union)

    def _matches_predicted_flow(self, query: str, flow: Dict[str, Any]) -> bool:
        """Check if query matches predicted conversation flow"""
        # Simplified pattern matching
        expected_patterns = flow.get('next_patterns', [])
        query_lower = query.lower()
        
        return any(pattern in query_lower for pattern in expected_patterns)

    def record_interaction(self, query: str, analysis: QueryAnalysis, 
                          optimization: CostOptimization, response: str,
                          user_satisfaction: float, user_id: str = None):
        """Record interaction for learning"""
        
        try:
            conn = sqlite3.connect(self.cache_db_path)
            cursor = conn.cursor()
            
            query_hash = hashlib.sha256(query.encode()).hexdigest()
            
            cursor.execute('''
                INSERT INTO query_analysis 
                (query_hash, complexity, emotional_state, user_id, topic_category,
                 response_length, provider_used, cost, satisfaction_score, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                query_hash,
                analysis.complexity.value,
                analysis.emotional_state.value,
                user_id,
                analysis.topic_category,
                len(response),
                optimization.provider,
                optimization.estimated_cost,
                user_satisfaction,
                datetime.now()
            ))
            
            # Record cost savings
            if optimization.use_local or optimization.estimated_cost == 0.0:
                original_cost = self._estimate_baseline_cost(analysis.complexity)
                savings = original_cost - optimization.estimated_cost
                
                cursor.execute('''
                    INSERT INTO cost_savings 
                    (optimization_type, original_cost, optimized_cost, savings, timestamp)
                    VALUES (?, ?, ?, ?, ?)
                ''', (
                    "ai_brain_optimization",
                    original_cost,
                    optimization.estimated_cost,
                    savings,
                    datetime.now()
                ))
                
                self.total_savings += savings
            
            conn.commit()
            conn.close()
            
            # Update performance metrics
            if optimization.use_local:
                self.local_response_rate = (self.local_response_rate * 0.9) + (1.0 * 0.1)
            
        except Exception as e:
            logger.error(f"Failed to record interaction: {e}")

    def _estimate_baseline_cost(self, complexity: QueryComplexity) -> float:
        """Estimate what this query would cost without optimization"""
        baseline_costs = {
            QueryComplexity.TRIVIAL: 0.001,
            QueryComplexity.SIMPLE: 0.002,
            QueryComplexity.MODERATE: 0.005,
            QueryComplexity.COMPLEX: 0.02,
            QueryComplexity.CRITICAL: 0.075
        }
        return baseline_costs[complexity]

    def get_optimization_report(self) -> Dict[str, Any]:
        """Get comprehensive optimization report"""
        
        try:
            conn = sqlite3.connect(self.cache_db_path)
            cursor = conn.cursor()
            
            # Total savings
            cursor.execute('SELECT SUM(savings) FROM cost_savings WHERE timestamp > ?', 
                         (datetime.now() - timedelta(days=30),))
            monthly_savings = cursor.fetchone()[0] or 0.0
            
            # Optimization breakdown
            cursor.execute('''
                SELECT optimization_type, COUNT(*), SUM(savings) 
                FROM cost_savings 
                WHERE timestamp > ?
                GROUP BY optimization_type
            ''', (datetime.now() - timedelta(days=30),))
            
            optimization_breakdown = {row[0]: {"count": row[1], "savings": row[2]} 
                                    for row in cursor.fetchall()}
            
            # Provider usage
            cursor.execute('''
                SELECT provider_used, COUNT(*), AVG(satisfaction_score)
                FROM query_analysis 
                WHERE created_at > ?
                GROUP BY provider_used
            ''', (datetime.now() - timedelta(days=30),))
            
            provider_stats = {row[0]: {"usage": row[1], "satisfaction": row[2]} 
                            for row in cursor.fetchall()}
            
            conn.close()
            
            return {
                "monthly_savings": monthly_savings,
                "optimization_breakdown": optimization_breakdown,
                "provider_stats": provider_stats,
                "local_response_rate": self.local_response_rate,
                "cache_hit_rate": self.cache_hit_rate,
                "total_lifetime_savings": self.total_savings
            }
            
        except Exception as e:
            logger.error(f"Failed to generate optimization report: {e}")
            return {"error": "Report generation failed"}

# Global instance
ai_brain_optimizer = AIBrainCostOptimizer()

# Convenience functions
def optimize_ai_request(query: str, user_id: str = None, context: Dict[str, Any] = None) -> CostOptimization:
    """Optimize AI request using brain intelligence"""
    return ai_brain_optimizer.optimize_request(query, user_id, context)

def record_ai_interaction(query: str, response: str, cost: float, satisfaction: float, user_id: str = None):
    """Record AI interaction for learning"""
    analysis = ai_brain_optimizer.analyze_query(query, user_id)
    optimization = CostOptimization(
        use_local=cost == 0.0,
        provider="recorded",
        model="unknown",
        estimated_cost=cost,
        confidence=satisfaction / 5.0,  # Convert 1-5 scale to 0-1
        reasoning=["Recorded interaction"]
    )
    ai_brain_optimizer.record_interaction(query, analysis, optimization, response, satisfaction, user_id)

def get_ai_optimization_report() -> Dict[str, Any]:
    """Get AI optimization report"""
    return ai_brain_optimizer.get_optimization_report()