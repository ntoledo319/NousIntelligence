"""
Enhanced Therapeutic AI - Real CBT/DBT/AA Support with AI Integration
Implements personalized therapeutic responses using Gemini Pro and intelligent fallbacks
"""

import os
import json
import logging
import requests
import sqlite3
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
import hashlib

logger = logging.getLogger(__name__)

class EnhancedTherapeuticAI:
    """Real AI-powered therapeutic support system"""
    
    def __init__(self):
        self.gemini_key = os.environ.get("GOOGLE_API_KEY")
        self.openai_key = os.environ.get("OPENAI_API_KEY")
        self.cache_db_path = "therapeutic_ai_cache.db"
        self.init_cache_database()
        
        # Therapeutic frameworks
        self.frameworks = ["CBT", "DBT", "AA", "general"]
        
        # Usage tracking
        self.monthly_therapeutic_cost = 0.0
        self.therapeutic_sessions = 0
        
        # Evidence-based interventions
        self.coping_skills = self._init_coping_skills()
        
        logger.info("Enhanced Therapeutic AI system initialized")

    def init_cache_database(self):
        """Initialize therapeutic session cache"""
        try:
            conn = sqlite3.connect(self.cache_db_path)
            conn.execute('''
                CREATE TABLE IF NOT EXISTS therapeutic_cache (
                    id INTEGER PRIMARY KEY,
                    input_hash TEXT UNIQUE,
                    framework TEXT,
                    response_text TEXT,
                    skills_recommended TEXT,
                    provider TEXT,
                    effectiveness_score REAL,
                    created_at TIMESTAMP,
                    use_count INTEGER DEFAULT 1
                )
            ''')
            conn.execute('''
                CREATE TABLE IF NOT EXISTS user_progress (
                    id INTEGER PRIMARY KEY,
                    user_id TEXT,
                    framework TEXT,
                    skill_name TEXT,
                    effectiveness_rating REAL,
                    usage_count INTEGER DEFAULT 1,
                    last_used TIMESTAMP,
                    notes TEXT
                )
            ''')
            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"Failed to initialize therapeutic cache: {e}")

    def _init_coping_skills(self) -> Dict[str, List[Dict[str, Any]]]:
        """Initialize evidence-based coping skills database"""
        return {
            "CBT": [
                {
                    "name": "Thought Challenging",
                    "description": "Identify and challenge negative thought patterns",
                    "technique": "Ask: Is this thought realistic? What evidence supports/contradicts it?",
                    "effectiveness": 0.85
                },
                {
                    "name": "Behavioral Activation",
                    "description": "Engage in meaningful activities to improve mood",
                    "technique": "Schedule pleasant and meaningful activities daily",
                    "effectiveness": 0.80
                },
                {
                    "name": "Cognitive Restructuring",
                    "description": "Reframe negative thoughts into balanced perspectives",
                    "technique": "Replace all-or-nothing thinking with balanced thoughts",
                    "effectiveness": 0.83
                }
            ],
            "DBT": [
                {
                    "name": "TIPP (Temperature, Intense Exercise, Paced Breathing, Paired Muscle Relaxation)",
                    "description": "Crisis survival technique for intense emotions",
                    "technique": "Cold water on face, exercise, slow breathing, tense and relax muscles",
                    "effectiveness": 0.90
                },
                {
                    "name": "PLEASE Skills",
                    "description": "Reduce vulnerability to negative emotions",
                    "technique": "Treat Physical illness, balance Eating, avoid mood-Altering substances, balance Sleep, Exercise",
                    "effectiveness": 0.78
                },
                {
                    "name": "Wise Mind",
                    "description": "Balance emotional and rational thinking",
                    "technique": "Consider both your emotions and logic before acting",
                    "effectiveness": 0.82
                }
            ],
            "AA": [
                {
                    "name": "HALT Check",
                    "description": "Check if you're Hungry, Angry, Lonely, or Tired",
                    "technique": "Address basic needs before making decisions",
                    "effectiveness": 0.75
                },
                {
                    "name": "Sponsor Contact",
                    "description": "Reach out to sponsor or support person",
                    "technique": "Call sponsor when feeling urges or struggling",
                    "effectiveness": 0.88
                },
                {
                    "name": "Meeting Attendance",
                    "description": "Attend AA meetings for support and accountability",
                    "technique": "Go to a meeting, especially when you don't want to",
                    "effectiveness": 0.85
                }
            ],
            "general": [
                {
                    "name": "Deep Breathing",
                    "description": "Controlled breathing to reduce anxiety and stress",
                    "technique": "4-7-8 breathing: Inhale 4, hold 7, exhale 8",
                    "effectiveness": 0.70
                },
                {
                    "name": "Progressive Muscle Relaxation",
                    "description": "Systematic tension and relaxation of muscle groups",
                    "technique": "Tense muscle groups for 5 seconds, then relax",
                    "effectiveness": 0.72
                },
                {
                    "name": "Mindfulness Meditation",
                    "description": "Present-moment awareness without judgment",
                    "technique": "Focus on breath, notice thoughts without engaging",
                    "effectiveness": 0.78
                }
            ]
        }

    def get_therapeutic_response(self, user_input: str, framework: str = "general", 
                               user_id: str = None, session_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get AI-enhanced therapeutic response"""
        
        # Check cache first
        cached_response = self._get_cached_response(user_input, framework)
        if cached_response:
            return cached_response
        
        try:
            # Use AI for personalized therapeutic response
            if self.gemini_key:
                response = self._gemini_therapeutic_response(user_input, framework, session_context)
                self.therapeutic_sessions += 1
            else:
                response = self._fallback_therapeutic_response(user_input, framework)
            
            # Add recommended coping skills
            response["recommended_skills"] = self._recommend_skills(user_input, framework, user_id)
            
            # Cache the response
            self._cache_therapeutic_response(user_input, framework, response)
            
            return response
            
        except Exception as e:
            logger.error(f"Therapeutic response error: {e}")
            return self._fallback_therapeutic_response(user_input, framework)

    def _gemini_therapeutic_response(self, user_input: str, framework: str, 
                                   session_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Generate therapeutic response using Gemini Pro"""
        
        # Create therapeutic prompt
        framework_context = {
            "CBT": "You are a CBT therapist. Focus on identifying thought patterns, cognitive distortions, and behavioral changes. Use evidence-based CBT techniques.",
            "DBT": "You are a DBT therapist. Focus on emotion regulation, distress tolerance, interpersonal effectiveness, and mindfulness skills.",
            "AA": "You are supporting someone in addiction recovery. Focus on 12-step principles, sobriety maintenance, and recovery strategies.",
            "general": "You are a supportive mental health assistant. Provide empathetic, evidence-based guidance."
        }
        
        context = session_context or {}
        previous_sessions = context.get("previous_sessions", "No previous context")
        
        prompt = f"""
        {framework_context.get(framework, framework_context["general"])}
        
        Previous session context: {previous_sessions}
        
        User says: "{user_input}"
        
        Provide a therapeutic response that:
        1. Shows empathy and understanding
        2. Uses {framework} techniques appropriately
        3. Suggests specific coping skills or interventions
        4. Encourages positive behavioral changes
        5. Maintains appropriate therapeutic boundaries
        
        Keep the response supportive, professional, and actionable.
        """
        
        try:
            import google.generativeai as genai
            genai.configure(api_key=self.gemini_key)
            # Use latest Gemini 2.5 Flash for better therapeutic responses
            model_name = os.environ.get('GEMINI_MODEL', 'gemini-2.5-flash')
            model = genai.GenerativeModel(model_name)

            response = model.generate_content(prompt)
            
            return {
                "response": response.text,
                "framework": framework,
                "provider": "gemini",
                "confidence": 0.85,
                "ai_generated": True,
                "cost": 0.0,  # Free tier
                "success": True
            }
            
        except ImportError:
            raise Exception("Google Generative AI library not available")
        except Exception as e:
            raise Exception(f"Gemini therapeutic response error: {e}")

    def _fallback_therapeutic_response(self, user_input: str, framework: str) -> Dict[str, Any]:
        """Fallback therapeutic response using rule-based system"""
        
        user_lower = user_input.lower()
        
        # Detect emotional state and concerns
        if any(word in user_lower for word in ["anxious", "anxiety", "worried", "nervous"]):
            emotion = "anxiety"
        elif any(word in user_lower for word in ["sad", "depressed", "down", "hopeless"]):
            emotion = "sadness"
        elif any(word in user_lower for word in ["angry", "mad", "frustrated", "irritated"]):
            emotion = "anger"
        elif any(word in user_lower for word in ["stressed", "overwhelmed", "pressure"]):
            emotion = "stress"
        elif any(word in user_lower for word in ["urge", "craving", "tempted", "relapse"]):
            emotion = "craving"
        else:
            emotion = "general"
        
        # Framework-specific responses
        responses = {
            "CBT": {
                "anxiety": "I hear that you're feeling anxious. Let's try some thought challenging - what specific thoughts are contributing to your anxiety? Are these thoughts based on facts or fears?",
                "sadness": "It sounds like you're experiencing sadness. CBT teaches us that our thoughts influence our feelings. What thoughts have been going through your mind?",
                "anger": "I can see you're feeling angry. Let's explore what thoughts might be fueling this anger. What story are you telling yourself about the situation?",
                "stress": "Stress often comes from our interpretation of events. What thoughts about your situation might be making the stress worse?",
                "general": "Thank you for sharing. In CBT, we often look at the connection between thoughts, feelings, and behaviors. What patterns do you notice?"
            },
            "DBT": {
                "anxiety": "I understand you're feeling anxious. Let's use some DBT skills - try the TIPP technique: splash cold water on your face or hold ice cubes to activate your parasympathetic nervous system.",
                "sadness": "I hear your pain. When we're in emotional distress, DBT teaches us to practice radical acceptance - acknowledging the feeling without trying to immediately change it.",
                "anger": "Anger is a valid emotion. DBT's distress tolerance skills can help - try the STOP technique: Stop, Take a breath, Observe, Proceed with awareness.",
                "stress": "When feeling overwhelmed, DBT suggests using PLEASE skills to reduce vulnerability - check if you need food, sleep, or exercise.",
                "craving": "Cravings are temporary. Try urge surfing - notice the urge without acting, knowing it will pass like a wave.",
                "general": "DBT teaches us that all emotions are temporary. What would help you get through this moment?"
            },
            "AA": {
                "craving": "Thank you for reaching out instead of acting on the urge. That's working your program. Have you contacted your sponsor? Consider attending a meeting today.",
                "stress": "Stress can be a trigger. Remember HALT - are you Hungry, Angry, Lonely, or Tired? Address these basic needs first.",
                "anxiety": "Anxiety about recovery is normal. 'One day at a time' - focus only on staying sober today. You don't have to handle forever right now.",
                "general": "Recovery is a daily practice. What step work or meeting attendance would help you today? Remember: progress, not perfection."
            },
            "general": {
                "anxiety": "I hear that you're feeling anxious. Try the 5-4-3-2-1 grounding technique: name 5 things you can see, 4 you can touch, 3 you can hear, 2 you can smell, 1 you can taste.",
                "sadness": "It's okay to feel sad. Emotions are temporary visitors. What's one small thing that usually brings you comfort?",
                "anger": "Anger often signals that something important to you is threatened. What boundary or value feels challenged right now?",
                "stress": "When stressed, our bodies need care. Try deep breathing: inhale for 4 counts, hold for 4, exhale for 6.",
                "general": "Thank you for sharing how you're feeling. That takes courage. What kind of support would be most helpful right now?"
            }
        }
        
        response_text = responses.get(framework, responses["general"]).get(emotion, responses[framework]["general"])
        
        return {
            "response": response_text,
            "framework": framework,
            "provider": "rule_based",
            "confidence": 0.65,
            "ai_generated": False,
            "cost": 0.0,
            "success": True,
            "detected_emotion": emotion
        }

    def _recommend_skills(self, user_input: str, framework: str, user_id: str = None) -> List[Dict[str, Any]]:
        """Recommend specific coping skills based on input and user history"""
        
        # Get user's effective skills if user_id provided
        user_effective_skills = self._get_user_effective_skills(user_id) if user_id else []
        
        # Get framework-specific skills
        available_skills = self.coping_skills.get(framework, self.coping_skills["general"])
        
        # Filter and rank skills
        user_lower = user_input.lower()
        
        # Emotional state-based skill recommendations
        if any(word in user_lower for word in ["anxious", "panic", "nervous"]):
            priority_skills = ["Deep Breathing", "Progressive Muscle Relaxation", "TIPP"]
        elif any(word in user_lower for word in ["sad", "depressed", "hopeless"]):
            priority_skills = ["Behavioral Activation", "Thought Challenging", "Mindfulness Meditation"]
        elif any(word in user_lower for word in ["angry", "frustrated", "mad"]):
            priority_skills = ["TIPP", "STOP Technique", "Progressive Muscle Relaxation"]
        elif any(word in user_lower for word in ["urge", "craving", "tempted"]):
            priority_skills = ["HALT Check", "Sponsor Contact", "Urge Surfing"]
        else:
            priority_skills = ["Mindfulness Meditation", "Deep Breathing", "Wise Mind"]
        
        # Combine user effective skills with priority skills
        recommended = []
        
        # Add user's historically effective skills first
        for skill in user_effective_skills[:2]:  # Top 2 effective skills
            recommended.append(skill)
        
        # Add priority skills that aren't already included
        for skill in available_skills:
            if (skill["name"] in priority_skills and 
                skill["name"] not in [r["name"] for r in recommended]):
                recommended.append(skill)
                
            if len(recommended) >= 3:  # Limit to 3 recommendations
                break
        
        # Fill remaining slots with high-effectiveness skills
        if len(recommended) < 3:
            remaining_skills = [s for s in available_skills 
                             if s["name"] not in [r["name"] for r in recommended]]
            remaining_skills.sort(key=lambda x: x["effectiveness"], reverse=True)
            
            for skill in remaining_skills:
                recommended.append(skill)
                if len(recommended) >= 3:
                    break
        
        return recommended[:3]

    def _get_user_effective_skills(self, user_id: str) -> List[Dict[str, Any]]:
        """Get user's most effective skills based on history"""
        try:
            conn = sqlite3.connect(self.cache_db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT skill_name, AVG(effectiveness_rating) as avg_rating, SUM(usage_count) as total_usage
                FROM user_progress 
                WHERE user_id = ? 
                GROUP BY skill_name 
                HAVING avg_rating >= 3.0 
                ORDER BY avg_rating DESC, total_usage DESC
                LIMIT 5
            ''', (user_id,))
            
            results = cursor.fetchall()
            conn.close()
            
            effective_skills = []
            for skill_name, avg_rating, usage_count in results:
                # Find skill details
                for framework_skills in self.coping_skills.values():
                    for skill in framework_skills:
                        if skill["name"] == skill_name:
                            skill_copy = skill.copy()
                            skill_copy["user_rating"] = avg_rating
                            skill_copy["user_usage"] = usage_count
                            effective_skills.append(skill_copy)
                            break
            
            return effective_skills
            
        except Exception as e:
            logger.error(f"Error getting user effective skills: {e}")
            return []

    def record_skill_effectiveness(self, user_id: str, skill_name: str, 
                                 effectiveness_rating: float, notes: str = None):
        """Record how effective a skill was for the user"""
        try:
            conn = sqlite3.connect(self.cache_db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO user_progress 
                (user_id, skill_name, effectiveness_rating, usage_count, last_used, notes)
                VALUES (?, ?, ?, 
                    COALESCE((SELECT usage_count FROM user_progress WHERE user_id = ? AND skill_name = ?), 0) + 1,
                    ?, ?)
            ''', (user_id, skill_name, effectiveness_rating, user_id, skill_name, datetime.now(), notes))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Error recording skill effectiveness: {e}")

    def _get_cached_response(self, user_input: str, framework: str) -> Optional[Dict[str, Any]]:
        """Get cached therapeutic response"""
        try:
            input_hash = hashlib.sha256(f"{user_input}_{framework}".encode()).hexdigest()
            
            conn = sqlite3.connect(self.cache_db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT response_text, skills_recommended, provider, effectiveness_score 
                FROM therapeutic_cache 
                WHERE input_hash = ? AND framework = ?
                ORDER BY created_at DESC LIMIT 1
            ''', (input_hash, framework))
            
            result = cursor.fetchone()
            
            if result:
                cursor.execute('''
                    UPDATE therapeutic_cache 
                    SET use_count = use_count + 1 
                    WHERE input_hash = ?
                ''', (input_hash,))
                conn.commit()
                
                skills = json.loads(result[1]) if result[1] else []
                
                response = {
                    "response": result[0],
                    "framework": framework,
                    "provider": result[2],
                    "recommended_skills": skills,
                    "effectiveness_score": result[3],
                    "cached": True,
                    "success": True
                }
                
                conn.close()
                logger.info(f"Cache hit for therapeutic response: {framework}")
                return response
                
            conn.close()
            return None
            
        except Exception as e:
            logger.error(f"Therapeutic cache retrieval error: {e}")
            return None

    def _cache_therapeutic_response(self, user_input: str, framework: str, response: Dict[str, Any]):
        """Cache therapeutic response"""
        try:
            input_hash = hashlib.sha256(f"{user_input}_{framework}".encode()).hexdigest()
            
            conn = sqlite3.connect(self.cache_db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO therapeutic_cache 
                (input_hash, framework, response_text, skills_recommended, provider, effectiveness_score, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                input_hash,
                framework,
                response.get("response", ""),
                json.dumps(response.get("recommended_skills", [])),
                response.get("provider", "unknown"),
                response.get("confidence", 0.5),
                datetime.now()
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Therapeutic cache storage error: {e}")

    def get_therapeutic_cost_report(self) -> Dict[str, Any]:
        """Get therapeutic AI cost and usage report"""
        return {
            "monthly_cost": self.monthly_therapeutic_cost,
            "sessions_completed": self.therapeutic_sessions,
            "frameworks_available": self.frameworks,
            "total_skills_available": sum(len(skills) for skills in self.coping_skills.values()),
            "cost_per_session": 0.0,  # Using free Gemini
            "effectiveness": "high"
        }

# Global instance
enhanced_therapeutic = EnhancedTherapeuticAI()

# Convenience functions
def get_therapeutic_response(user_input: str, framework: str = "general") -> Dict[str, Any]:
    """Get therapeutic AI response"""
    return enhanced_therapeutic.get_therapeutic_response(user_input, framework)

def get_cbt_response(user_input: str) -> str:
    """Get CBT-focused response"""
    response = enhanced_therapeutic.get_therapeutic_response(user_input, "CBT")
    return response.get("response", "CBT response not available")

def get_dbt_response(user_input: str) -> str:
    """Get DBT-focused response"""
    response = enhanced_therapeutic.get_therapeutic_response(user_input, "DBT")
    return response.get("response", "DBT response not available")

def get_aa_response(user_input: str) -> str:
    """Get AA recovery-focused response"""
    response = enhanced_therapeutic.get_therapeutic_response(user_input, "AA")
    return response.get("response", "AA response not available")

def record_skill_effectiveness(user_id: str, skill_name: str, rating: float):
    """Record how effective a coping skill was"""
    enhanced_therapeutic.record_skill_effectiveness(user_id, skill_name, rating)

def get_therapeutic_cost_report() -> Dict[str, Any]:
    """Get therapeutic cost report"""
    return enhanced_therapeutic.get_therapeutic_cost_report()