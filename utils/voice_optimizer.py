"""
Voice Optimization Module

This module provides optimizations for the voice interface to reduce costs
while maintaining high quality. It implements:

1. Audio compression before sending to cloud APIs
2. Adaptive sampling rate based on speech detection
3. Batch processing for non-real-time transcriptions
4. Local voice processing when available
5. Voice activity detection to avoid processing silence

@module utils.voice_optimizer
@description Voice processing optimizations for reduced API costs
"""

import os
import logging
import tempfile
import subprocess
import base64
from typing import Dict, Any, Optional, Union, Tuple, List
import io
import wave
import array
import struct
import math
import time

logger = logging.getLogger(__name__)

# Check for local processing tools
FFMPEG_AVAILABLE = False
try:
    result = subprocess.run(['ffmpeg', '-version'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    FFMPEG_AVAILABLE = result.returncode == 0
except:
    logger.warning("ffmpeg not available for audio optimization")

# Local whisper detection
WHISPER_LOCAL_AVAILABLE = os.path.exists(os.path.expanduser("~/whisper.cpp/models/tiny.en.bin"))

# Constants
DEFAULT_SAMPLE_RATE = 16000  # 16kHz is standard for most speech recognition
MIN_SAMPLE_RATE = 8000       # 8kHz is minimum for intelligible speech
HIGH_QUALITY_SAMPLE_RATE = 24000  # 24kHz for higher quality when needed

class VoiceOptimizer:
    def __init__(self):
        self.settings = {
            "compress_audio": True,
            "use_local_when_available": True,
            "adaptive_sampling": True,
            "vad_optimization": True,
            "batch_processing": True,
            "max_batch_size": 10,
            "silence_threshold": 0.05,
            "min_audio_duration": 0.5  # Minimum duration in seconds
        }
        
        # Pending batch for non-real-time processing
        self.pending_batch = []
        self.last_batch_process = time.time()
        
        logger.info("Voice optimizer initialized with settings: %s", self.settings)
    
    def optimize_audio_for_api(self, audio_data: bytes, 
                             is_realtime: bool = False,
                             priority: str = "standard") -> Tuple[bytes, Dict[str, Any]]:
        """
        Optimize audio data for API processing based on priority and realtime requirements
        
        Args:
            audio_data: Raw audio data bytes
            is_realtime: Whether this is for realtime processing
            priority: Priority level ('economy', 'standard', 'premium')
            
        Returns:
            Tuple of (optimized_audio_bytes, metadata)
        """
        metadata = {
            "original_size": len(audio_data),
            "original_duration": 0,
            "optimized_size": 0,
            "optimized_duration": 0,
            "compression_ratio": 0,
            "sample_rate": DEFAULT_SAMPLE_RATE,
            "contains_speech": True
        }
        
        try:
            # Skip optimization for premium priority unless compression will be significant
            if priority == "premium" and len(audio_data) < 500000:  # < 500KB
                return audio_data, metadata
            
            # Basic audio info extraction
            audio_info = self._get_audio_info(audio_data)
            metadata.update(audio_info)
            
            # Voice activity detection to check if audio contains actual speech
            if self.settings["vad_optimization"]:
                speech_detected, speech_info = self._detect_speech(audio_data)
                metadata["contains_speech"] = speech_detected
                metadata.update(speech_info)
                
                # If no speech detected and not realtime, we can optimize heavily
                if not speech_detected and not is_realtime:
                    # For non-speech audio, we can be aggressive with compression
                    return self._compress_audio(audio_data, aggressive=True)
            
            # Determine optimal sample rate based on content
            if self.settings["adaptive_sampling"]:
                optimal_rate = self._get_optimal_sample_rate(audio_info, priority)
                metadata["sample_rate"] = optimal_rate
                
                # Resample if needed
                if audio_info.get("sample_rate") != optimal_rate:
                    audio_data = self._resample_audio(audio_data, 
                                                     audio_info.get("sample_rate", DEFAULT_SAMPLE_RATE),
                                                     optimal_rate)
            
            # Compress audio data as needed
            if self.settings["compress_audio"]:
                # Use more aggressive compression for economy mode
                aggressive = (priority == "economy")
                audio_data, comp_info = self._compress_audio(audio_data, aggressive=aggressive)
                metadata.update(comp_info)
            
            # Trim silence if detected and not realtime
            if not is_realtime and self.settings["vad_optimization"]:
                audio_data, trim_info = self._trim_silence(audio_data)
                metadata.update(trim_info)
            
            return audio_data, metadata
            
        except Exception as e:
            logger.error(f"Error optimizing audio: {str(e)}")
            # Return original data if optimization fails
            return audio_data, metadata
    
    def _get_audio_info(self, audio_data: bytes) -> Dict[str, Any]:
        """Extract basic information from audio data"""
        info = {
            "sample_rate": DEFAULT_SAMPLE_RATE,
            "channels": 1,
            "duration": 0,
            "bit_depth": 16
        }
        
        try:
            # Try to parse WAV header for basic info
            if audio_data[:4] == b'RIFF' and audio_data[8:12] == b'WAVE':
                with io.BytesIO(audio_data) as buf:
                    with wave.open(buf, 'rb') as wav:
                        info["sample_rate"] = wav.getframerate()
                        info["channels"] = wav.getnchannels()
                        info["bit_depth"] = wav.getsampwidth() * 8
                        frames = wav.getnframes()
                        info["duration"] = frames / info["sample_rate"]
        except Exception as e:
            logger.warning(f"Could not extract audio info: {str(e)}")
            # Estimate duration for raw PCM data
            samples = len(audio_data) / 2  # Assuming 16-bit samples
            info["duration"] = samples / DEFAULT_SAMPLE_RATE
        
        return info
    
    def _detect_speech(self, audio_data: bytes) -> Tuple[bool, Dict[str, Any]]:
        """
        Detect if audio contains speech and calculate voice activity metrics
        
        Returns:
            Tuple of (contains_speech, speech_info)
        """
        speech_info = {
            "speech_duration": 0,
            "speech_percentage": 0,
            "energy_level": 0
        }
        
        try:
            # Convert audio to PCM samples for analysis
            samples = self._get_pcm_samples(audio_data)
            if not samples:
                return False, speech_info
            
            # Calculate energy level
            energy = sum(abs(s) for s in samples) / len(samples)
            normalized_energy = min(1.0, energy / 32768.0)  # Normalize to 0-1 for 16-bit audio
            speech_info["energy_level"] = normalized_energy
            
            # Basic speech detection - check if energy exceeds threshold
            threshold = self.settings["silence_threshold"]
            frames_with_speech = sum(1 for s in samples if abs(s) / 32768.0 > threshold)
            speech_percentage = frames_with_speech / len(samples) if samples else 0
            speech_info["speech_percentage"] = speech_percentage
            
            # Get audio info for duration calculation
            audio_info = self._get_audio_info(audio_data)
            speech_info["speech_duration"] = audio_info.get("duration", 0) * speech_percentage
            
            # Determine if this contains significant speech
            contains_speech = (
                speech_percentage > 0.05 and  # More than 5% speech
                speech_info["speech_duration"] > self.settings["min_audio_duration"] and  # Minimum duration
                normalized_energy > 0.01  # Minimum energy
            )
            
            return contains_speech, speech_info
            
        except Exception as e:
            logger.warning(f"Speech detection failed: {str(e)}")
            return True, speech_info  # Default to True to be safe
    
    def _get_pcm_samples(self, audio_data: bytes) -> List[int]:
        """Convert audio bytes to PCM samples for analysis"""
        try:
            # Try to parse as WAV first
            if audio_data[:4] == b'RIFF' and audio_data[8:12] == b'WAVE':
                with io.BytesIO(audio_data) as buf:
                    with wave.open(buf, 'rb') as wav:
                        # Read all frames as bytes
                        frame_bytes = wav.readframes(wav.getnframes())
                        
                        # Convert to samples based on bit depth
                        if wav.getsampwidth() == 2:  # 16-bit
                            samples = array.array('h')
                            samples.frombytes(frame_bytes)
                            return samples.tolist()
                        elif wav.getsampwidth() == 1:  # 8-bit
                            samples = array.array('B')
                            samples.frombytes(frame_bytes)
                            # Convert 8-bit (0-255) to 16-bit (-32768 to 32767)
                            return [(s - 128) * 256 for s in samples]
            
            # Fallback for raw PCM data - assume 16-bit signed samples
            samples = array.array('h')
            samples.frombytes(audio_data[:min(len(audio_data), 32000)])  # Sample for efficiency
            return samples.tolist()
            
        except Exception as e:
            logger.warning(f"Failed to extract PCM samples: {str(e)}")
            return []
    
    def _get_optimal_sample_rate(self, audio_info: Dict[str, Any], priority: str) -> int:
        """Determine optimal sample rate based on audio content and priority"""
        # Get current sample rate
        current_rate = audio_info.get("sample_rate", DEFAULT_SAMPLE_RATE)
        
        # For premium priority, maintain or increase quality
        if priority == "premium":
            return max(current_rate, HIGH_QUALITY_SAMPLE_RATE)
        
        # For economy, use lowest acceptable rate
        if priority == "economy":
            return MIN_SAMPLE_RATE
        
        # For standard, use default rate
        return min(current_rate, DEFAULT_SAMPLE_RATE)
    
    def _resample_audio(self, audio_data: bytes, from_rate: int, to_rate: int) -> bytes:
        """Resample audio to a different sample rate"""
        if not FFMPEG_AVAILABLE or from_rate == to_rate:
            return audio_data
            
        try:
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as input_file:
                input_file.write(audio_data)
                input_path = input_file.name
                
            output_path = input_path + '.resampled.wav'
            
            # Use ffmpeg for high-quality resampling
            command = [
                'ffmpeg', '-y',
                '-i', input_path,
                '-ar', str(to_rate),
                '-ac', '1',  # Force mono
                output_path
            ]
            
            result = subprocess.run(
                command, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE
            )
            
            if result.returncode == 0 and os.path.exists(output_path):
                with open(output_path, 'rb') as f:
                    resampled_data = f.read()
                
                # Clean up temp files
                os.unlink(input_path)
                os.unlink(output_path)
                
                return resampled_data
            else:
                logger.warning(f"Resampling failed: {result.stderr.decode()}")
                return audio_data
                
        except Exception as e:
            logger.error(f"Error during resampling: {str(e)}")
            return audio_data
            
    def _compress_audio(self, audio_data: bytes, aggressive: bool = False) -> Tuple[bytes, Dict[str, Any]]:
        """
        Compress audio to reduce size while maintaining quality
        
        Args:
            audio_data: Input audio data
            aggressive: Whether to use more aggressive compression
            
        Returns:
            Tuple of (compressed_data, compression_info)
        """
        compression_info = {
            "original_size": len(audio_data),
            "optimized_size": len(audio_data),
            "compression_ratio": 1.0,
            "compression_method": "none"
        }
        
        if not FFMPEG_AVAILABLE:
            return audio_data, compression_info
            
        try:
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as input_file:
                input_file.write(audio_data)
                input_path = input_file.name
                
            output_path = input_path + '.compressed.wav'
            
            # Compression settings based on aggressiveness
            if aggressive:
                # Very aggressive compression for non-critical audio
                command = [
                    'ffmpeg', '-y',
                    '-i', input_path,
                    '-ar', str(MIN_SAMPLE_RATE),  # Minimum sample rate
                    '-ac', '1',                   # Mono
                    '-codec:a', 'pcm_s16le',      # 16-bit PCM
                    output_path
                ]
                compression_info["compression_method"] = "aggressive"
            else:
                # Standard compression that maintains good quality
                command = [
                    'ffmpeg', '-y',
                    '-i', input_path,
                    '-ar', str(DEFAULT_SAMPLE_RATE),  # Standard sample rate
                    '-ac', '1',                       # Mono
                    '-codec:a', 'pcm_s16le',          # 16-bit PCM
                    output_path
                ]
                compression_info["compression_method"] = "standard"
            
            result = subprocess.run(
                command, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE
            )
            
            if result.returncode == 0 and os.path.exists(output_path):
                with open(output_path, 'rb') as f:
                    compressed_data = f.read()
                
                # Update compression info
                compression_info["optimized_size"] = len(compressed_data)
                if len(audio_data) > 0:
                    compression_info["compression_ratio"] = len(compressed_data) / len(audio_data)
                
                # Clean up temp files
                os.unlink(input_path)
                os.unlink(output_path)
                
                return compressed_data, compression_info
            else:
                logger.warning(f"Compression failed: {result.stderr.decode()}")
                return audio_data, compression_info
                
        except Exception as e:
            logger.error(f"Error during compression: {str(e)}")
            return audio_data, compression_info
    
    def _trim_silence(self, audio_data: bytes) -> Tuple[bytes, Dict[str, Any]]:
        """Trim silence from beginning and end of audio"""
        trim_info = {
            "trimmed": False,
            "original_duration": 0,
            "trimmed_duration": 0,
            "silence_removed_seconds": 0
        }
        
        if not FFMPEG_AVAILABLE:
            return audio_data, trim_info
            
        try:
            # Get original duration
            audio_info = self._get_audio_info(audio_data)
            trim_info["original_duration"] = audio_info.get("duration", 0)
            
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as input_file:
                input_file.write(audio_data)
                input_path = input_file.name
                
            output_path = input_path + '.trimmed.wav'
            
            # Use ffmpeg to trim silence
            command = [
                'ffmpeg', '-y',
                '-i', input_path,
                '-af', f'silenceremove=start_periods=1:start_threshold={self.settings["silence_threshold"]}:start_silence=0.1:detection=peak,aformat=dblp,silenceremove=stop_periods=1:stop_threshold={self.settings["silence_threshold"]}:stop_silence=0.1:detection=peak',
                output_path
            ]
            
            result = subprocess.run(
                command, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE
            )
            
            if result.returncode == 0 and os.path.exists(output_path):
                with open(output_path, 'rb') as f:
                    trimmed_data = f.read()
                
                # Get trimmed duration
                trimmed_info = self._get_audio_info(trimmed_data)
                trim_info["trimmed_duration"] = trimmed_info.get("duration", 0)
                trim_info["silence_removed_seconds"] = max(0, trim_info["original_duration"] - trim_info["trimmed_duration"])
                trim_info["trimmed"] = trim_info["silence_removed_seconds"] > 0.2  # Only count if significant
                
                # Clean up temp files
                os.unlink(input_path)
                os.unlink(output_path)
                
                return trimmed_data, trim_info
            else:
                logger.warning(f"Silence trimming failed: {result.stderr.decode()}")
                return audio_data, trim_info
                
        except Exception as e:
            logger.error(f"Error during silence trimming: {str(e)}")
            return audio_data, trim_info
    
    def add_to_batch(self, audio_data: bytes, callback=None, metadata: Dict[str, Any] = None):
        """Add audio data to batch for processing"""
        if not self.settings["batch_processing"]:
            return False
            
        batch_item = {
            "audio_data": audio_data,
            "callback": callback,
            "metadata": metadata or {},
            "timestamp": time.time()
        }
        
        self.pending_batch.append(batch_item)
        
        # Process batch if it's full or old enough
        should_process = (
            len(self.pending_batch) >= self.settings["max_batch_size"] or
            (time.time() - self.last_batch_process) > 10  # Process at least every 10 seconds
        )
        
        if should_process:
            self.process_batch()
            return True
            
        return False
        
    def process_batch(self):
        """Process pending batch of audio data"""
        if not self.pending_batch:
            return
            
        batch = self.pending_batch
        self.pending_batch = []
        self.last_batch_process = time.time()
        
        logger.info(f"Processing batch of {len(batch)} audio items")
        
        # TODO: Implement batched processing through AI service manager
        # This would be connected to the AI service for bulk processing
        
        # For now, process each item individually
        for item in batch:
            try:
                callback = item.get("callback")
                if callable(callback):
                    # Process the item and call the callback with results
                    audio_data = item.get("audio_data")
                    metadata = item.get("metadata", {})
                    
                    # The callback function would need to handle the transcription
                    callback(audio_data, metadata)
            except Exception as e:
                logger.error(f"Error processing batch item: {str(e)}")

# Initialize the global voice optimizer
voice_optimizer = VoiceOptimizer()

def get_voice_optimizer() -> VoiceOptimizer:
    """Get the global voice optimizer instance"""
    global voice_optimizer
    return voice_optimizer