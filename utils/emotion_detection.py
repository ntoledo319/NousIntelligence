"""
Emotion Detection Utility

This module provides functions for detecting emotions from voice audio
by chaining speech-to-text and text classification services from HuggingFace.

@ai_prompt: This module is the core logic for voice emotion analysis.
If you need to change the AI model or the analysis steps, this is the
place to do it. The main function is `analyze_voice_audio`.

@context_boundary: This module is a utility that depends on `utils.huggingface_helper`
for AI services and `models.EmotionLog` for database logging. It is called by
`routes.voice_emotion_routes`.
"""

# AI-GENERATED [2024-07-29]
# HUMAN-VALIDATED [2024-07-29]

import logging
import io
from typing import Dict, Any, Optional
import torch
import librosa
import numpy as np
from transformers import Wav2Vec2ForSequenceClassification, Wav2Vec2FeatureExtractor


from utils.huggingface_helper import speech_to_text_hf, classify_text_hf
from models import db, EmotionLog

logger = logging.getLogger(__name__)

# Load the voice emotion recognition model and feature extractor
try:
    voice_emotion_model_name = "ehcalabres/wav2vec2-lg-xlsr-en-speech-emotion-recognition"
    voice_emotion_feature_extractor = Wav2Vec2FeatureExtractor.from_pretrained(voice_emotion_model_name)
    voice_emotion_model = Wav2Vec2ForSequenceClassification.from_pretrained(voice_emotion_model_name)
    VOICE_EMOTION_MODEL_AVAILABLE = True
except Exception as e:
    logger.warning(f"Could not load voice emotion model: {e}")
    VOICE_EMOTION_MODEL_AVAILABLE = False


def analyze_voice_emotion_from_audio(audio_data: bytes) -> Dict[str, Any]:
    """
    Analyzes voice audio directly for emotions using a speech emotion recognition model.
    """
    if not VOICE_EMOTION_MODEL_AVAILABLE:
        return {"success": False, "error": "Voice emotion model not available."}

    try:
        # Convert audio bytes to a NumPy array
        audio_array, sampling_rate = librosa.load(io.BytesIO(audio_data), sr=16000)

        inputs = voice_emotion_feature_extractor(
            audio_array,
            sampling_rate=sampling_rate,
            return_tensors="pt",
            padding=True
        )

        with torch.no_grad():
            logits = voice_emotion_model(inputs.input_values, attention_mask=inputs.attention_mask).logits

        scores = torch.nn.functional.softmax(logits, dim=1).flatten().tolist()
        
        # Get the predicted label and score
        prediction = torch.argmax(logits, dim=1)
        predicted_label = voice_emotion_model.config.id2label[prediction.item()]
        
        # Create a list of all labels with their scores
        classification = [
            {"label": voice_emotion_model.config.id2label[i], "score": score}
            for i, score in enumerate(scores)
        ]
        # Sort by score descending
        classification = sorted(classification, key=lambda x: x["score"], reverse=True)

        return {
            "success": True,
            "emotion": predicted_label,
            "confidence": classification[0]['score'],
            "full_classification": classification,
        }
    except Exception as e:
        logger.error(f"Error analyzing voice emotion from audio: {str(e)}")
        return {"success": False, "error": str(e)}


def analyze_voice_audio(audio_data: bytes, user_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Analyzes voice audio for emotions by transcribing and then classifying,
    and also by analyzing the audio directly.

    This function orchestrates a multi-modal process for voice emotion analysis:
    1. Analyzes the raw audio data for emotional tone using a dedicated speech emotion model.
    2. Transcribes the raw audio data to text using `speech_to_text_hf`.
    3. Performs sentiment/emotion classification on the text using `classify_text_hf`.
    4. Combines the results for a more robust prediction.

    Args:
        audio_data: The audio data in bytes.
        user_id: The ID of the user, used for logging the detected emotion.

    Returns:
        A dictionary containing the full analysis result, including the
        transcribed text, detected emotion, and confidence scores.
    """
    # Step 1: Analyze emotion from raw audio
    audio_emotion_result = analyze_voice_emotion_from_audio(audio_data)

    # Step 2: Transcribe audio to text
    stt_result = speech_to_text_hf(audio_data)
    if not stt_result.get("success"):
        # If transcription fails, we can still return the audio emotion result
        if audio_emotion_result.get("success"):
            return {**audio_emotion_result, "source": "Voice"}
        return {"success": False, "error": "Failed to transcribe audio."}
    
    transcribed_text = stt_result.get("text")
    if not transcribed_text:
        # If no text, but we have audio emotion, return that
        if audio_emotion_result.get("success"):
            return {**audio_emotion_result, "source": "Voice", "transcribed_text": ""}
        return {"success": False, "error": "No text could be transcribed from audio."}

    # Step 3: Classify the sentiment of the text
    text_classification_result = classify_text_hf(transcribed_text)

    # Step 4: Combine audio and text results
    final_emotion = "unknown"
    final_confidence = 0.0
    final_classification = []
    source = "N/A"

    audio_success = audio_emotion_result.get("success", False)
    text_success = text_classification_result.get("success", False)

    # Prioritize audio emotion if confidence is high
    if audio_success and audio_emotion_result.get("confidence", 0) > 0.6:
        final_emotion = audio_emotion_result.get("emotion")
        final_confidence = audio_emotion_result.get("confidence")
        final_classification = audio_emotion_result.get("full_classification")
        source = "Voice"
    elif text_success:
        emotions = text_classification_result.get("classification", [])
        primary_emotion = emotions[0] if emotions else {"label": "unknown", "score": 0.0}
        final_emotion = primary_emotion.get("label")
        final_confidence = primary_emotion.get("score")
        final_classification = emotions
        source = "Text"
    elif audio_success: # Fallback to audio if text failed but audio succeeded
        final_emotion = audio_emotion_result.get("emotion")
        final_confidence = audio_emotion_result.get("confidence")
        final_classification = audio_emotion_result.get("full_classification")
        source = "Voice"
    
    result = {
        "success": True,
        "transcribed_text": transcribed_text,
        "emotion": final_emotion,
        "confidence": final_confidence,
        "full_classification": final_classification,
        "source": source,
        "audio_analysis": audio_emotion_result,
        "text_analysis": text_classification_result,
    }

    # Log the emotion if user_id is provided
    if user_id:
        log_emotion(
            user_id=user_id,
            emotion=result['emotion'],
            confidence=result['confidence'],
            source=source,
            details=f"Voice analysis - Text: '{transcribed_text}'"
        )

    return result

def log_emotion(user_id: str, emotion: str, confidence: float, source: str, details: str) -> None:
    """
    Logs a detected emotion event to the database.

    Args:
        user_id: The ID of the user associated with the event.
        emotion: The detected emotion label (e.g., 'joy', 'sadness').
        confidence: The confidence score from the AI model (0.0 to 1.0).
        source: The source of the detection (e.g., 'voice', 'text').
        details: Additional context, such as the transcribed text.
    """
    try:
        log_entry = EmotionLog(
            user_id=user_id,
            emotion=emotion,
            confidence=confidence,
            source=source,
            details=details
        )
        db.session.add(log_entry)
        db.session.commit()
    except Exception as e:
        logger.error(f"Error logging emotion for user {user_id}: {str(e)}")
        db.session.rollback() 