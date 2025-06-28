"""
Visual Intelligence Integration
Leverages existing image processing routes + AI service + analytics
for document processing, receipt scanning, image analysis, and visual task creation
"""

import base64
import json
import logging
import cv2
import numpy as np
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
import re
import pytesseract
from PIL import Image, ImageEnhance
import io

from utils.unified_ai_service import UnifiedAIService
from utils.image_helper import ImageHelper
from services.predictive_analytics import predictive_engine

logger = logging.getLogger(__name__)

class DocumentProcessor:
    """Advanced document processing and analysis"""
    
    def __init__(self):
        """Initialize document processor"""
        self.ai_service = UnifiedAIService()
        self.image_helper = ImageHelper()
        
        # Document type patterns
        self.document_patterns = {
            'receipt': [
                r'total[:\s]*\$?(\d+\.?\d*)',
                r'subtotal[:\s]*\$?(\d+\.?\d*)',
                r'tax[:\s]*\$?(\d+\.?\d*)',
                r'(\d{2}/\d{2}/\d{4}|\d{4}-\d{2}-\d{2})',  # dates
                r'(visa|mastercard|amex|discover)',  # payment methods
            ],
            'invoice': [
                r'invoice[:\s#]*(\w+)',
                r'due[:\s]*(\d{2}/\d{2}/\d{4})',
                r'amount[:\s]*\$?(\d+\.?\d*)',
                r'bill[:\s]*to[:\s]*([^\n]+)',
            ],
            'business_card': [
                r'([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})',  # email
                r'(\+?1?[-.\s]?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4})',  # phone
                r'(ceo|manager|director|president)',  # titles
            ],
            'form': [
                r'name[:\s]*([^\n]+)',
                r'address[:\s]*([^\n]+)',
                r'signature[:\s]*',
                r'date[:\s]*(\d{2}/\d{2}/\d{4})',
            ]
        }
        
        logger.info("Document Processor initialized")
    
    def process_document_image(self, image_data: bytes, document_type: str = None) -> Dict[str, Any]:
        """Process document image with OCR and AI analysis"""
        try:
            # Convert image data to PIL Image
            image = Image.open(io.BytesIO(image_data))
            
            # Enhance image for better OCR
            enhanced_image = self._enhance_image_for_ocr(image)
            
            # Extract text using OCR
            extracted_text = pytesseract.image_to_string(enhanced_image)
            
            # Detect document type if not provided
            if not document_type:
                document_type = self._detect_document_type(extracted_text)
            
            # Extract structured data based on document type
            structured_data = self._extract_structured_data(extracted_text, document_type)
            
            # Use AI for advanced analysis
            ai_analysis = self._ai_analyze_document(extracted_text, document_type)
            
            return {
                'document_type': document_type,
                'extracted_text': extracted_text,
                'structured_data': structured_data,
                'ai_analysis': ai_analysis,
                'confidence': self._calculate_confidence(structured_data),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error processing document image: {e}")
            return {'error': str(e)}
    
    def _enhance_image_for_ocr(self, image: Image.Image) -> Image.Image:
        """Enhance image quality for better OCR results"""
        try:
            # Convert to grayscale
            if image.mode != 'L':
                image = image.convert('L')
            
            # Enhance contrast
            enhancer = ImageEnhance.Contrast(image)
            image = enhancer.enhance(2.0)
            
            # Enhance sharpness
            enhancer = ImageEnhance.Sharpness(image)
            image = enhancer.enhance(2.0)
            
            # Convert to numpy array for OpenCV processing
            img_array = np.array(image)
            
            # Apply noise reduction
            img_array = cv2.fastNlMeansDenoising(img_array)
            
            # Apply morphological operations to clean up text
            kernel = np.ones((1, 1), np.uint8)
            img_array = cv2.morphologyEx(img_array, cv2.MORPH_CLOSE, kernel)
            
            # Convert back to PIL Image
            return Image.fromarray(img_array)
            
        except Exception as e:
            logger.error(f"Error enhancing image: {e}")
            return image
    
    def _detect_document_type(self, text: str) -> str:
        """Automatically detect document type from text content"""
        text_lower = text.lower()
        
        # Score each document type based on pattern matches
        type_scores = {}
        
        for doc_type, patterns in self.document_patterns.items():
            score = 0
            for pattern in patterns:
                matches = re.findall(pattern, text_lower, re.IGNORECASE)
                score += len(matches)
            type_scores[doc_type] = score
        
        # Return type with highest score, or 'unknown' if no good matches
        if type_scores:
            best_type = max(type_scores.items(), key=lambda x: x[1])
            return best_type[0] if best_type[1] > 0 else 'unknown'
        
        return 'unknown'
    
    def _extract_structured_data(self, text: str, document_type: str) -> Dict[str, Any]:
        """Extract structured data based on document type"""
        structured_data = {}
        
        if document_type == 'receipt':
            structured_data = self._extract_receipt_data(text)
        elif document_type == 'invoice':
            structured_data = self._extract_invoice_data(text)
        elif document_type == 'business_card':
            structured_data = self._extract_business_card_data(text)
        elif document_type == 'form':
            structured_data = self._extract_form_data(text)
        
        return structured_data
    
    def _extract_receipt_data(self, text: str) -> Dict[str, Any]:
        """Extract receipt-specific data"""
        data = {}
        
        # Extract total amount
        total_matches = re.findall(r'total[:\s]*\$?(\d+\.?\d*)', text, re.IGNORECASE)
        if total_matches:
            data['total'] = float(total_matches[-1])  # Take last match (usually final total)
        
        # Extract date
        date_matches = re.findall(r'(\d{1,2}/\d{1,2}/\d{4}|\d{4}-\d{2}-\d{2})', text)
        if date_matches:
            data['date'] = date_matches[0]
        
        # Extract merchant name (usually first line or after specific keywords)
        lines = text.split('\n')
        for line in lines[:5]:  # Check first 5 lines
            if len(line.strip()) > 3 and not re.search(r'\d', line):
                data['merchant'] = line.strip()
                break
        
        # Extract items
        items = self._extract_receipt_items(text)
        if items:
            data['items'] = items
        
        # Extract payment method
        payment_matches = re.findall(r'(visa|mastercard|amex|discover|cash)', text, re.IGNORECASE)
        if payment_matches:
            data['payment_method'] = payment_matches[0]
        
        return data
    
    def _extract_receipt_items(self, text: str) -> List[Dict[str, Any]]:
        """Extract individual items from receipt"""
        items = []
        lines = text.split('\n')
        
        for line in lines:
            # Look for lines with item name and price
            price_match = re.search(r'\$?(\d+\.?\d*)\s*$', line.strip())
            if price_match and len(line.strip()) > 10:
                item_name = re.sub(r'\$?\d+\.?\d*\s*$', '', line.strip()).strip()
                if item_name and not re.search(r'(total|subtotal|tax|change)', item_name, re.IGNORECASE):
                    items.append({
                        'name': item_name,
                        'price': float(price_match.group(1))
                    })
        
        return items
    
    def _extract_invoice_data(self, text: str) -> Dict[str, Any]:
        """Extract invoice-specific data"""
        data = {}
        
        # Extract invoice number
        invoice_matches = re.findall(r'invoice[:\s#]*(\w+)', text, re.IGNORECASE)
        if invoice_matches:
            data['invoice_number'] = invoice_matches[0]
        
        # Extract due date
        due_matches = re.findall(r'due[:\s]*(\d{1,2}/\d{1,2}/\d{4})', text, re.IGNORECASE)
        if due_matches:
            data['due_date'] = due_matches[0]
        
        # Extract amount
        amount_matches = re.findall(r'amount[:\s]*\$?(\d+\.?\d*)', text, re.IGNORECASE)
        if amount_matches:
            data['amount'] = float(amount_matches[-1])
        
        return data
    
    def _extract_business_card_data(self, text: str) -> Dict[str, Any]:
        """Extract business card data"""
        data = {}
        
        # Extract email
        email_matches = re.findall(r'([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})', text)
        if email_matches:
            data['email'] = email_matches[0]
        
        # Extract phone
        phone_matches = re.findall(r'(\+?1?[-.\s]?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4})', text)
        if phone_matches:
            data['phone'] = phone_matches[0]
        
        # Extract name (usually first substantial line)
        lines = text.split('\n')
        for line in lines:
            if len(line.strip()) > 5 and not re.search(r'@|\.com|\d{3}', line):
                data['name'] = line.strip()
                break
        
        return data
    
    def _extract_form_data(self, text: str) -> Dict[str, Any]:
        """Extract form data"""
        data = {}
        
        # Extract name
        name_matches = re.findall(r'name[:\s]*([^\n]+)', text, re.IGNORECASE)
        if name_matches:
            data['name'] = name_matches[0].strip()
        
        # Extract address
        address_matches = re.findall(r'address[:\s]*([^\n]+)', text, re.IGNORECASE)
        if address_matches:
            data['address'] = address_matches[0].strip()
        
        # Extract date
        date_matches = re.findall(r'date[:\s]*(\d{1,2}/\d{1,2}/\d{4})', text, re.IGNORECASE)
        if date_matches:
            data['date'] = date_matches[0]
        
        return data
    
    def _ai_analyze_document(self, text: str, document_type: str) -> Dict[str, Any]:
        """Use AI for advanced document analysis"""
        try:
            prompt = f"""
            Analyze this {document_type} document and provide insights:
            
            Text content:
            {text}
            
            Please provide:
            1. Key information summary
            2. Potential action items
            3. Category/classification
            4. Any anomalies or concerns
            5. Suggested next steps
            
            Respond in JSON format.
            """
            
            ai_response = self.ai_service.chat_completion([
                {"role": "user", "content": prompt}
            ])
            
            # Try to parse AI response as JSON
            try:
                return json.loads(ai_response.get('content', '{}'))
            except:
                return {'summary': ai_response.get('content', 'AI analysis unavailable')}
                
        except Exception as e:
            logger.error(f"Error in AI document analysis: {e}")
            return {'error': 'AI analysis failed'}
    
    def _calculate_confidence(self, structured_data: Dict[str, Any]) -> float:
        """Calculate confidence score for extracted data"""
        if not structured_data:
            return 0.0
        
        # Simple confidence calculation based on amount of extracted data
        total_fields = len(structured_data)
        populated_fields = sum(1 for v in structured_data.values() if v)
        
        return min(1.0, populated_fields / max(1, total_fields))

class VisualTaskCreator:
    """Create tasks from visual content analysis"""
    
    def __init__(self):
        self.ai_service = UnifiedAIService()
        self.document_processor = DocumentProcessor()
        
    def create_tasks_from_image(self, image_data: bytes, user_id: str) -> List[Dict[str, Any]]:
        """Create tasks based on image analysis"""
        try:
            # Process the image
            document_analysis = self.document_processor.process_document_image(image_data)
            
            # Generate tasks based on document type
            tasks = []
            
            if document_analysis.get('document_type') == 'receipt':
                tasks.extend(self._create_receipt_tasks(document_analysis, user_id))
            elif document_analysis.get('document_type') == 'invoice':
                tasks.extend(self._create_invoice_tasks(document_analysis, user_id))
            elif document_analysis.get('document_type') == 'business_card':
                tasks.extend(self._create_business_card_tasks(document_analysis, user_id))
            else:
                tasks.extend(self._create_general_tasks(document_analysis, user_id))
            
            return tasks
            
        except Exception as e:
            logger.error(f"Error creating tasks from image: {e}")
            return []
    
    def _create_receipt_tasks(self, analysis: Dict[str, Any], user_id: str) -> List[Dict[str, Any]]:
        """Create tasks from receipt analysis"""
        tasks = []
        structured_data = analysis.get('structured_data', {})
        
        if 'total' in structured_data:
            # Create expense tracking task
            tasks.append({
                'title': f"Log expense: {structured_data.get('merchant', 'Unknown merchant')}",
                'description': f"Log ${structured_data['total']} expense from receipt",
                'category': 'financial',
                'priority': 'medium',
                'auto_data': structured_data,
                'user_id': user_id
            })
        
        # Create budget review task for large expenses
        if structured_data.get('total', 0) > 100:
            tasks.append({
                'title': "Review budget impact",
                'description': f"Large expense of ${structured_data['total']} detected",
                'category': 'financial',
                'priority': 'high',
                'user_id': user_id
            })
        
        return tasks
    
    def _create_invoice_tasks(self, analysis: Dict[str, Any], user_id: str) -> List[Dict[str, Any]]:
        """Create tasks from invoice analysis"""
        tasks = []
        structured_data = analysis.get('structured_data', {})
        
        if 'due_date' in structured_data:
            # Create payment reminder task
            tasks.append({
                'title': f"Pay invoice #{structured_data.get('invoice_number', 'Unknown')}",
                'description': f"Invoice due on {structured_data['due_date']}",
                'category': 'financial',
                'priority': 'high',
                'due_date': structured_data['due_date'],
                'user_id': user_id
            })
        
        return tasks
    
    def _create_business_card_tasks(self, analysis: Dict[str, Any], user_id: str) -> List[Dict[str, Any]]:
        """Create tasks from business card analysis"""
        tasks = []
        structured_data = analysis.get('structured_data', {})
        
        if 'name' in structured_data:
            # Create contact follow-up task
            tasks.append({
                'title': f"Follow up with {structured_data['name']}",
                'description': "Add to contacts and schedule follow-up",
                'category': 'networking',
                'priority': 'medium',
                'contact_data': structured_data,
                'user_id': user_id
            })
        
        return tasks
    
    def _create_general_tasks(self, analysis: Dict[str, Any], user_id: str) -> List[Dict[str, Any]]:
        """Create general tasks from any document"""
        tasks = []
        
        # Use AI to suggest tasks based on document content
        ai_analysis = analysis.get('ai_analysis', {})
        
        if 'suggested_next_steps' in ai_analysis:
            for step in ai_analysis['suggested_next_steps']:
                tasks.append({
                    'title': f"Document action: {step}",
                    'description': "Action suggested from document analysis",
                    'category': 'general',
                    'priority': 'low',
                    'user_id': user_id
                })
        
        return tasks

class ImageAnalytics:
    """Advanced image analytics and insights"""
    
    def __init__(self):
        self.ai_service = UnifiedAIService()
        
    def analyze_image_collection(self, image_paths: List[str], user_id: str) -> Dict[str, Any]:
        """Analyze collection of images for patterns and insights"""
        try:
            analytics = {
                'total_images': len(image_paths),
                'categories': {},
                'patterns': [],
                'insights': [],
                'trends': {}
            }
            
            # Process each image
            for image_path in image_paths:
                image_analysis = self._analyze_single_image(image_path)
                
                # Categorize
                category = image_analysis.get('category', 'uncategorized')
                analytics['categories'][category] = analytics['categories'].get(category, 0) + 1
            
            # Generate insights
            analytics['insights'] = self._generate_image_insights(analytics)
            
            return analytics
            
        except Exception as e:
            logger.error(f"Error analyzing image collection: {e}")
            return {}
    
    def _analyze_single_image(self, image_path: str) -> Dict[str, Any]:
        """Analyze single image for content and metadata"""
        try:
            # Basic image analysis (in production, you'd use more sophisticated CV models)
            return {
                'category': 'document',  # Simplified categorization
                'confidence': 0.8,
                'metadata': {
                    'analyzed_at': datetime.now().isoformat()
                }
            }
        except Exception as e:
            logger.error(f"Error analyzing image {image_path}: {e}")
            return {}
    
    def _generate_image_insights(self, analytics: Dict[str, Any]) -> List[str]:
        """Generate insights from image analytics"""
        insights = []
        
        categories = analytics.get('categories', {})
        total_images = analytics.get('total_images', 0)
        
        if total_images > 10:
            insights.append(f"You've processed {total_images} images - that's quite active!")
        
        # Find dominant category
        if categories:
            dominant_category = max(categories.items(), key=lambda x: x[1])
            insights.append(f"Most of your images are {dominant_category[0]} ({dominant_category[1]} images)")
        
        return insights

class VisualIntelligenceService:
    """Main visual intelligence service integrating all components"""
    
    def __init__(self):
        """Initialize visual intelligence service"""
        self.document_processor = DocumentProcessor()
        self.task_creator = VisualTaskCreator()
        self.image_analytics = ImageAnalytics()
        
        logger.info("Visual Intelligence Service initialized")
    
    def process_image_upload(self, image_data: bytes, user_id: str, 
                           auto_create_tasks: bool = True) -> Dict[str, Any]:
        """Complete image processing workflow"""
        try:
            # Process document
            document_analysis = self.document_processor.process_document_image(image_data)
            
            # Create tasks if requested
            tasks = []
            if auto_create_tasks:
                tasks = self.task_creator.create_tasks_from_image(image_data, user_id)
            
            # Generate insights
            insights = self._generate_processing_insights(document_analysis, tasks)
            
            return {
                'document_analysis': document_analysis,
                'generated_tasks': tasks,
                'insights': insights,
                'processing_timestamp': datetime.now().isoformat(),
                'user_id': user_id
            }
            
        except Exception as e:
            logger.error(f"Error in complete image processing: {e}")
            return {'error': str(e)}
    
    def _generate_processing_insights(self, document_analysis: Dict[str, Any], 
                                    tasks: List[Dict[str, Any]]) -> List[str]:
        """Generate insights from processing results"""
        insights = []
        
        doc_type = document_analysis.get('document_type', 'unknown')
        confidence = document_analysis.get('confidence', 0)
        
        insights.append(f"Detected {doc_type} document with {confidence:.1%} confidence")
        
        if tasks:
            insights.append(f"Created {len(tasks)} automated tasks")
        
        # Add specific insights based on document type
        structured_data = document_analysis.get('structured_data', {})
        if doc_type == 'receipt' and 'total' in structured_data:
            insights.append(f"Expense amount: ${structured_data['total']}")
        
        return insights
    
    def get_processing_history(self, user_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Get user's image processing history"""
        # This would integrate with your database to store and retrieve history
        return []
    
    def get_visual_analytics(self, user_id: str) -> Dict[str, Any]:
        """Get visual processing analytics for user"""
        # This would provide analytics on user's visual processing patterns
        return {
            'total_processed': 0,
            'document_types': {},
            'automation_efficiency': 0.0
        }

# Global instance
visual_intelligence = VisualIntelligenceService()