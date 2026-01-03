"""
Consolidated API Routes - Phase 1.2 Backend Consolidation
Merges duplicate endpoints from api_routes.py, api_v2.py, enhanced_api_routes.py
"""
from flask import Blueprint, jsonify, request, session
from utils.unified_auth import require_auth
import time

consolidated_bp = Blueprint("consolidated_api", __name__, url_prefix="/api/v1")

@consolidated_bp.get("/health")
def health():
    """Unified health check endpoint"""
    return jsonify({
        "status": "healthy",
        "timestamp": time.time(),
        "version": "1.0.0"
    })

@consolidated_bp.get("/user")
@require_auth(allow_demo=True)
def get_user():
    """Get current user information"""
    user_id = session.get("user_id")
    username = session.get("username")
    user_data = session.get("user", {})
    
    if isinstance(user_data, dict) and user_data:
        return jsonify({"user": user_data})
    
    if user_id:
        return jsonify({
            "user": {
                "id": str(user_id),
                "name": username or "User",
                "email": session.get("email"),
                "isDemo": user_id == "demo"
            }
        })
    
    return jsonify({"user": {"id": "guest", "name": "Guest", "isDemo": False}})

@consolidated_bp.post("/chat")
@require_auth(allow_demo=True)
def chat():
    """
    Unified chat endpoint - connects to EmotionAwareTherapeuticAssistant
    Replaces all duplicate /chat endpoints
    """
    if not request.is_json:
        return jsonify({"error": "JSON required"}), 400
    
    data = request.get_json() or {}
    message = data.get("message", "").strip()
    
    if not message:
        return jsonify({"error": "Message required"}), 400
    
    if len(message) > 10000:
        return jsonify({"error": "Message too long"}), 413
    
    user_id = session.get("user_id", "demo")
    
    try:
        from services.emotion_aware_therapeutic_assistant import EmotionAwareTherapeuticAssistant
        assistant = EmotionAwareTherapeuticAssistant()
        response = assistant.get_therapeutic_response(
            user_input=message,
            user_id=user_id,
            context={"session_id": session.get("session_id")}
        )
        return jsonify(response)
    except Exception as e:
        import logging
        logging.error(f"Chat error: {e}")
        return jsonify({
            "response": "I apologize, but I encountered an issue. Please try again.",
            "error": str(e)
        }), 500

@consolidated_bp.get("/conversations")
@require_auth(allow_demo=True)
def get_conversations():
    """Get user's conversation history"""
    user_id = session.get("user_id")
    
    try:
        from models import Conversation
        from models.database import db
        
        conversations = Conversation.query.filter_by(user_id=user_id).order_by(
            Conversation.updated_at.desc()
        ).limit(50).all()
        
        return jsonify([{
            "id": conv.id,
            "title": conv.title or "Untitled Conversation",
            "created_at": conv.created_at.isoformat(),
            "updated_at": conv.updated_at.isoformat()
        } for conv in conversations])
    except Exception:
        return jsonify([])

@consolidated_bp.get("/conversations/<conversation_id>/messages")
@require_auth(allow_demo=True)
def get_messages(conversation_id):
    """Get messages for a specific conversation"""
    user_id = session.get("user_id")
    
    try:
        from models import Message, Conversation
        from models.database import db
        
        # Verify ownership
        conversation = Conversation.query.filter_by(
            id=conversation_id,
            user_id=user_id
        ).first_or_404()
        
        messages = Message.query.filter_by(
            conversation_id=conversation_id
        ).order_by(Message.created_at.asc()).all()
        
        return jsonify({
            "messages": [{
                "id": msg.id,
                "text": msg.content,
                "sender": "user" if msg.role == "user" else "assistant",
                "timestamp": msg.created_at.isoformat()
            } for msg in messages]
        })
    except Exception:
        return jsonify({"messages": []})
