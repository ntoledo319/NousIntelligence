"""
Enhanced Visual Intelligence - GPT-4V Document Analysis and OCR
Implements smart visual processing with cost optimization
"""

import os
import json
import base64
import logging
import requests
import sqlite3
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import hashlib
from io import BytesIO

logger = logging.getLogger(__name__)

class EnhancedVisualIntelligence:
    """Smart visual processing with GPT-4V and fallback OCR"""
    
    def __init__(self):
        self.openai_key = os.environ.get("OPENAI_API_KEY")
        self.cache_db_path = "visual_intelligence_cache.db"
        self.init_cache_database()
        
        # Cost tracking
        self.monthly_visual_cost = 0.0
        self.visual_requests_count = 0
        
        # Free tier limits
        self.monthly_limit = 50  # Conservative limit for GPT-4V
        
        logger.info("Enhanced Visual Intelligence system initialized")

    def init_cache_database(self):
        """Initialize visual analysis cache"""
        try:
            conn = sqlite3.connect(self.cache_db_path)
            conn.execute('''
                CREATE TABLE IF NOT EXISTS visual_cache (
                    id INTEGER PRIMARY KEY,
                    image_hash TEXT UNIQUE,
                    analysis_type TEXT,
                    analysis_result TEXT,
                    provider TEXT,
                    cost REAL,
                    created_at TIMESTAMP,
                    use_count INTEGER DEFAULT 1
                )
            ''')
            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"Failed to initialize visual cache: {e}")

    def analyze_image(self, image_data: bytes, analysis_type: str = "general", 
                     specific_request: str = None) -> Dict[str, Any]:
        """Analyze image with GPT-4V or fallback methods"""
        
        # Generate image hash for caching
        image_hash = hashlib.sha256(image_data).hexdigest()[:16]
        
        # Check cache first
        cached_result = self._get_cached_analysis(image_hash, analysis_type)
        if cached_result:
            return cached_result
        
        try:
            # Use GPT-4V for complex analysis if within budget
            if (self.openai_key and 
                self.visual_requests_count < self.monthly_limit and 
                analysis_type in ["document", "complex", "research"]):
                
                result = self._gpt4v_analysis(image_data, analysis_type, specific_request)
                self.visual_requests_count += 1
                self.monthly_visual_cost += 0.15  # Estimated cost per image
                
            else:
                # Use fallback OCR and basic analysis
                result = self._fallback_visual_analysis(image_data, analysis_type)
            
            # Cache the result
            self._cache_visual_result(image_hash, analysis_type, result)
            return result
            
        except Exception as e:
            logger.error(f"Visual analysis error: {e}")
            return self._fallback_visual_analysis(image_data, analysis_type)

    def _gpt4v_analysis(self, image_data: bytes, analysis_type: str, 
                       specific_request: str = None) -> Dict[str, Any]:
        """GPT-4V image analysis"""
        
        # Encode image to base64
        base64_image = base64.b64encode(image_data).decode('utf-8')
        
        # Create analysis prompt based on type
        prompts = {
            "document": "Analyze this document image. Extract all text, identify the document type, summarize key information, and create actionable tasks based on the content.",
            "research": "Analyze this image for research purposes. Identify any data, charts, graphs, text, or scientific content. Provide detailed analysis and insights.",
            "general": "Describe this image in detail. Identify objects, text, people, and any relevant information.",
            "complex": "Provide a comprehensive analysis of this image, including any text, visual elements, and actionable insights."
        }
        
        prompt = specific_request if specific_request else prompts.get(analysis_type, prompts["general"])
        
        headers = {
            "Authorization": f"Bearer {self.openai_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "gpt-4o",
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}",
                                "detail": "high"
                            }
                        }
                    ]
                }
            ],
            "max_tokens": 1000
        }
        
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=60
        )
        
        if response.status_code == 200:
            data = response.json()
            analysis_text = data["choices"][0]["message"]["content"]
            
            # Extract actionable tasks if it's a document
            tasks = self._extract_tasks_from_analysis(analysis_text) if analysis_type == "document" else []
            
            return {
                "analysis": analysis_text,
                "provider": "gpt-4v",
                "analysis_type": analysis_type,
                "confidence": 0.9,
                "extracted_tasks": tasks,
                "cost": 0.15,
                "success": True
            }
        else:
            raise Exception(f"GPT-4V API error: {response.status_code}")

    def _fallback_visual_analysis(self, image_data: bytes, analysis_type: str) -> Dict[str, Any]:
        """Fallback visual analysis using basic OCR"""
        
        try:
            # Try to use pytesseract for OCR if available
            ocr_text = self._basic_ocr(image_data)
            
            if ocr_text.strip():
                # Basic text analysis
                tasks = self._extract_tasks_from_text(ocr_text) if analysis_type == "document" else []
                
                return {
                    "analysis": f"OCR extracted text: {ocr_text}",
                    "extracted_text": ocr_text,
                    "provider": "fallback_ocr",
                    "analysis_type": analysis_type,
                    "confidence": 0.6,
                    "extracted_tasks": tasks,
                    "cost": 0.0,
                    "success": True
                }
            else:
                return self._no_analysis_fallback(analysis_type)
                
        except Exception as e:
            logger.error(f"Fallback visual analysis error: {e}")
            return self._no_analysis_fallback(analysis_type)

    def _basic_ocr(self, image_data: bytes) -> str:
        """Basic OCR using pytesseract if available"""
        try:
            import pytesseract
            from PIL import Image
            
            # Convert bytes to PIL Image
            image = Image.open(BytesIO(image_data))
            
            # Extract text
            text = pytesseract.image_to_string(image)
            return text.strip()
            
        except ImportError:
            logger.warning("pytesseract not available for OCR")
            return ""
        except Exception as e:
            logger.error(f"OCR error: {e}")
            return ""

    def _no_analysis_fallback(self, analysis_type: str) -> Dict[str, Any]:
        """Fallback when no analysis is possible"""
        fallback_messages = {
            "document": "Document analysis requires GPT-4V or OCR capabilities. Please ensure image is clear and API keys are configured.",
            "research": "Research image analysis requires GPT-4V. Basic analysis not available.",
            "general": "Image analysis capabilities are limited. Describe what you need analyzed for text-based assistance.",
            "complex": "Complex visual analysis requires advanced AI models. Please describe the image content."
        }
        
        return {
            "analysis": fallback_messages.get(analysis_type, "Visual analysis not available"),
            "provider": "fallback",
            "analysis_type": analysis_type,
            "confidence": 0.1,
            "extracted_tasks": [],
            "cost": 0.0,
            "success": False,
            "message": "Visual analysis requires API key or OCR libraries"
        }

    def _extract_tasks_from_analysis(self, analysis_text: str) -> List[Dict[str, Any]]:
        """Extract actionable tasks from GPT-4V analysis"""
        tasks = []
        
        # Look for task indicators in the analysis
        task_indicators = [
            "action required", "follow up", "deadline", "due date",
            "contact", "call", "email", "schedule", "meeting",
            "review", "complete", "submit", "sign", "approve"
        ]
        
        sentences = analysis_text.split('.')
        
        for sentence in sentences:
            sentence_lower = sentence.lower().strip()
            if any(indicator in sentence_lower for indicator in task_indicators):
                tasks.append({
                    "task": sentence.strip(),
                    "priority": "medium",
                    "source": "document_analysis",
                    "created_at": datetime.now().isoformat()
                })
        
        return tasks[:5]  # Limit to 5 tasks

    def _extract_tasks_from_text(self, text: str) -> List[Dict[str, Any]]:
        """Extract tasks from OCR text"""
        tasks = []
        
        # Simple task extraction from text
        lines = text.split('\n')
        for line in lines:
            line_lower = line.lower().strip()
            if any(word in line_lower for word in ['todo', 'task', 'action', 'deadline', 'due']):
                tasks.append({
                    "task": line.strip(),
                    "priority": "low",
                    "source": "ocr_extraction",
                    "created_at": datetime.now().isoformat()
                })
        
        return tasks[:3]  # Limit to 3 tasks

    def _get_cached_analysis(self, image_hash: str, analysis_type: str) -> Optional[Dict[str, Any]]:
        """Get cached visual analysis"""
        try:
            conn = sqlite3.connect(self.cache_db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT analysis_result, provider, cost 
                FROM visual_cache 
                WHERE image_hash = ? AND analysis_type = ?
                ORDER BY created_at DESC LIMIT 1
            ''', (image_hash, analysis_type))
            
            result = cursor.fetchone()
            
            if result:
                cursor.execute('''
                    UPDATE visual_cache 
                    SET use_count = use_count + 1 
                    WHERE image_hash = ?
                ''', (image_hash,))
                conn.commit()
                
                analysis_data = json.loads(result[0])
                analysis_data["cached"] = True
                conn.close()
                logger.info(f"Cache hit for visual analysis: {analysis_type}")
                return analysis_data
                
            conn.close()
            return None
            
        except Exception as e:
            logger.error(f"Visual cache retrieval error: {e}")
            return None

    def _cache_visual_result(self, image_hash: str, analysis_type: str, result: Dict[str, Any]):
        """Cache visual analysis result"""
        try:
            conn = sqlite3.connect(self.cache_db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO visual_cache 
                (image_hash, analysis_type, analysis_result, provider, cost, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                image_hash,
                analysis_type,
                json.dumps(result),
                result.get("provider", "unknown"),
                result.get("cost", 0.0),
                datetime.now()
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Visual cache storage error: {e}")

    def analyze_document(self, image_data: bytes, document_type: str = None) -> Dict[str, Any]:
        """Specialized document analysis"""
        specific_request = None
        if document_type:
            specific_request = f"Analyze this {document_type} document. Extract all relevant information and suggest actionable tasks."
        
        return self.analyze_image(image_data, "document", specific_request)

    def research_image_analysis(self, image_data: bytes, research_question: str = None) -> Dict[str, Any]:
        """Research-focused image analysis"""
        specific_request = research_question if research_question else None
        return self.analyze_image(image_data, "research", specific_request)

    def get_visual_cost_report(self) -> Dict[str, Any]:
        """Get visual processing cost report"""
        return {
            "monthly_cost": self.monthly_visual_cost,
            "requests_made": self.visual_requests_count,
            "requests_remaining": max(0, self.monthly_limit - self.visual_requests_count),
            "cost_per_request": 0.15,
            "budget_status": "under_budget" if self.visual_requests_count < self.monthly_limit else "over_budget"
        }

# Global instance
enhanced_visual = EnhancedVisualIntelligence()

# Convenience functions
def analyze_image(image_data: bytes, analysis_type: str = "general") -> Dict[str, Any]:
    """Analyze image with enhanced visual intelligence"""
    return enhanced_visual.analyze_image(image_data, analysis_type)

def analyze_document(image_data: bytes, document_type: str = None) -> Dict[str, Any]:
    """Analyze document image"""
    return enhanced_visual.analyze_document(image_data, document_type)

def research_image_analysis(image_data: bytes, research_question: str = None) -> Dict[str, Any]:
    """Research-focused image analysis"""
    return enhanced_visual.research_image_analysis(image_data, research_question)

def get_visual_cost_report() -> Dict[str, Any]:
    """Get visual processing cost report"""
    return enhanced_visual.get_visual_cost_report()