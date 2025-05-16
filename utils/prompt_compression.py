"""
@module prompt_compression
@description Token-saving prompt compression techniques for LLM interactions
@author AI Assistant
"""

import re
import string
import logging
from typing import Dict, List, Optional, Tuple, Union, Any
import hashlib

# Configure logger
logger = logging.getLogger(__name__)

class PromptCompressionLevel:
    """Compression level definitions"""
    NONE = "none"           # No compression
    LIGHT = "light"         # Light compression, preserves most information
    MEDIUM = "medium"       # Medium compression, balances size and quality
    AGGRESSIVE = "aggressive"  # Aggressive compression, minimizes tokens

# Common stopwords that can often be removed in compressed contexts
STOPWORDS = set([
    "a", "an", "the", "and", "or", "but", "if", "then", "else", "when",
    "up", "down", "in", "out", "on", "off", "over", "under", "again", "further",
    "then", "once", "here", "there", "why", "how", "all", "any", "both", "each",
    "few", "more", "most", "other", "some", "such", "no", "nor", "not", "only",
    "own", "same", "so", "than", "too", "very", "s", "t", "can", "will", "just",
    "don", "should", "now", "also", "however", "therefore"
])

def compress_prompt(prompt: str, level: str = PromptCompressionLevel.MEDIUM) -> str:
    """
    Compress a prompt to reduce token usage
    
    Args:
        prompt: The prompt text to compress
        level: Compression level to apply
        
    Returns:
        Compressed prompt text
    """
    if level == PromptCompressionLevel.NONE:
        return prompt
        
    # Save original prompt for logging
    original_length = len(prompt.split())
    
    if level == PromptCompressionLevel.LIGHT:
        compressed = light_compression(prompt)
    elif level == PromptCompressionLevel.MEDIUM:
        compressed = medium_compression(prompt)
    elif level == PromptCompressionLevel.AGGRESSIVE:
        compressed = aggressive_compression(prompt)
    else:
        logger.warning(f"Unknown compression level: {level}, using MEDIUM")
        compressed = medium_compression(prompt)
    
    # Log compression stats
    compressed_length = len(compressed.split())
    reduction = (1 - compressed_length / original_length) * 100 if original_length > 0 else 0
    logger.info(f"Compressed prompt: {original_length} → {compressed_length} words ({reduction:.1f}% reduction)")
    
    return compressed

def light_compression(text: str) -> str:
    """
    Apply light compression to text:
    - Remove redundant whitespace
    - Remove some unnecessary punctuation
    - Preserve most of the original text
    
    Args:
        text: Text to compress
        
    Returns:
        Lightly compressed text
    """
    # Remove redundant whitespace
    compressed = re.sub(r'\s+', ' ', text).strip()
    
    # Remove unnecessary quotes
    compressed = re.sub(r'"+([^"]+)"+', r'\1', compressed)
    
    # Replace common phrases with shorter equivalents
    replacements = {
        "in order to": "to",
        "a number of": "several",
        "a large number of": "many",
        "a small number of": "few",
        "due to the fact that": "because",
        "in spite of the fact that": "although",
        "in the event that": "if",
        "with regard to": "about",
        "for the purpose of": "for",
        "in the near future": "soon",
        "at this point in time": "now",
        "it is important to note that": "note that",
        "please be advised that": "",
        "thank you for your attention to this matter": "thanks",
    }
    
    for phrase, replacement in replacements.items():
        compressed = re.sub(rf'\b{re.escape(phrase)}\b', replacement, compressed, flags=re.IGNORECASE)
    
    return compressed

def medium_compression(text: str) -> str:
    """
    Apply medium compression to text:
    - Light compression plus
    - Remove most filler words
    - Simplify sentence structure
    - Use abbreviations for common terms
    
    Args:
        text: Text to compress
        
    Returns:
        Medium compressed text
    """
    # Apply light compression first
    compressed = light_compression(text)
    
    # Remove more filler words and phrases
    for word in ["actually", "basically", "literally", "really", "simply", "just", "very", 
                "quite", "rather", "somewhat", "extremely", "definitely", "certainly", 
                "probably", "practically", "effectively", "essentially", "virtually"]:
        compressed = re.sub(rf'\b{word}\b', '', compressed, flags=re.IGNORECASE)
        
    # Replace common words with abbreviations
    abbreviations = {
        "application": "app",
        "configuration": "config",
        "database": "DB",
        "information": "info",
        "implementation": "impl",
        "management": "mgmt",
        "production": "prod",
        "development": "dev",
        "example": "ex",
        "reference": "ref",
        "specification": "spec",
        "technical": "tech",
        "requirements": "reqs",
        "documentation": "docs",
        "application programming interface": "API",
        "command line interface": "CLI",
        "graphical user interface": "GUI",
        "with respect to": "re",
    }
    
    for word, abbr in abbreviations.items():
        compressed = re.sub(rf'\b{re.escape(word)}\b', abbr, compressed, flags=re.IGNORECASE)
    
    # Remove unnecessary determiners and conjunctions (not all, to maintain readability)
    for word in ["a", "an", "the", "that", "which", "who", "whom"]:
        compressed = re.sub(rf'\b{word}\b\s', '', compressed, flags=re.IGNORECASE)
    
    # Clean up any resulting double spaces
    compressed = re.sub(r'\s+', ' ', compressed).strip()
    
    return compressed

def aggressive_compression(text: str) -> str:
    """
    Apply aggressive compression to text:
    - Medium compression plus
    - Remove all non-essential words
    - Use extreme abbreviation
    - Telegraphic style (like bullet points)
    
    Args:
        text: Text to compress
        
    Returns:
        Aggressively compressed text
    """
    # Apply medium compression first
    compressed = medium_compression(text)
    
    # Remove almost all stopwords
    words = compressed.split()
    words = [word for word in words if word.lower() not in STOPWORDS]
    compressed = ' '.join(words)
    
    # Remove most punctuation except periods and question marks
    compressed = re.sub(r'[,;:()\[\]"]', '', compressed)
    
    # Replace remaining common phrases with ultra-short versions
    extreme_abbr = {
        "in my opinion": "IMO",
        "as soon as possible": "ASAP",
        "for example": "e.g.",
        "that is": "i.e.",
        "as far as i know": "AFAIK",
        "to be determined": "TBD",
        "in other words": "i.e.",
        "on the other hand": "OTOH",
        "by the way": "BTW",
        "as far as i can tell": "AFAICT",
        "in relation to": "re",
        "regarding": "re",
        "with reference to": "re",
        "to sum up": "∴",  # Therefore symbol
        "greater than": ">",
        "less than": "<",
        "equal to": "=",
        "not equal to": "≠",
        "approximately": "~",
        "without": "w/o",
        "with": "w/",
        "between": "btw",
    }
    
    for phrase, abbr in extreme_abbr.items():
        compressed = re.sub(rf'\b{re.escape(phrase)}\b', abbr, compressed, flags=re.IGNORECASE)
    
    # Convert lists to bullet points
    list_markers = ["first", "firstly", "second", "secondly", "third", "thirdly", 
                   "fourth", "fifth", "finally", "lastly", "next", "then", 
                   "additionally", "moreover", "furthermore"]
    
    for marker in list_markers:
        compressed = re.sub(rf'\b{marker}\b,?\s*', '• ', compressed, flags=re.IGNORECASE)
    
    # Clean up
    compressed = re.sub(r'\s+', ' ', compressed).strip()
    
    return compressed

def compress_conversation_history(conversation: List[Dict[str, str]], 
                                 max_tokens: int = 2000, 
                                 level: str = PromptCompressionLevel.MEDIUM) -> List[Dict[str, str]]:
    """
    Compress a conversation history to fit within token limits
    
    Args:
        conversation: List of message dictionaries with 'role' and 'content'
        max_tokens: Maximum tokens to target
        level: Compression level to apply
        
    Returns:
        Compressed conversation history
    """
    # If conversation is empty or very short, return as is
    if not conversation or len(conversation) < 3:
        return conversation
    
    compressed_conversation = []
    
    # Always include the system message if present
    if conversation[0]['role'] == 'system':
        compressed_conversation.append(conversation[0])
        conversation = conversation[1:]
    
    # Always keep the most recent user message
    last_user_msg = next((msg for msg in reversed(conversation) 
                         if msg['role'] == 'user'), None)
    
    if last_user_msg:
        # Remove the last user message from the list
        conversation = [msg for msg in conversation if msg != last_user_msg]
    
    # Estimate tokens per message (rough approximation)
    def estimate_tokens(text):
        return len(text.split()) * 1.3  # Rough approximation: 1 word ≈ 1.3 tokens
    
    # Calculate available tokens (accounting for the last user message)
    available_tokens = max_tokens
    if last_user_msg:
        available_tokens -= estimate_tokens(last_user_msg['content'])
    
    # Calculate tokens for conversation
    message_tokens = [(msg, estimate_tokens(msg['content'])) for msg in conversation]
    total_estimated_tokens = sum(tokens for _, tokens in message_tokens)
    
    # If already under limit, apply basic compression and return
    if total_estimated_tokens <= available_tokens:
        compressed_conversation.extend([
            {'role': msg['role'], 'content': compress_prompt(msg['content'], PromptCompressionLevel.LIGHT)}
            for msg in conversation
        ])
        
        # Add the last user message
        if last_user_msg:
            compressed_conversation.append(last_user_msg)
            
        return compressed_conversation
    
    # We need more aggressive compression
    
    # Strategy 1: Increase compression level
    compressed_msgs = []
    remaining_tokens = available_tokens
    
    # Try to compress with current level first
    compression_level = level
    for msg, tokens in message_tokens:
        # Skip system messages (already handled)
        if msg['role'] == 'system':
            continue
            
        compressed_content = compress_prompt(msg['content'], compression_level)
        estimated_compressed_tokens = estimate_tokens(compressed_content)
        
        if estimated_compressed_tokens <= remaining_tokens:
            compressed_msgs.append({'role': msg['role'], 'content': compressed_content})
            remaining_tokens -= estimated_compressed_tokens
        else:
            # If can't fit, try more aggressive compression
            if compression_level != PromptCompressionLevel.AGGRESSIVE:
                compression_level = PromptCompressionLevel.AGGRESSIVE
                compressed_content = compress_prompt(msg['content'], compression_level)
                estimated_compressed_tokens = estimate_tokens(compressed_content)
                
                if estimated_compressed_tokens <= remaining_tokens:
                    compressed_msgs.append({'role': msg['role'], 'content': compressed_content})
                    remaining_tokens -= estimated_compressed_tokens
    
    # Strategy 2: If still too large, summarize or drop older messages
    if not compressed_msgs:
        # Calculate how many recent messages we can include
        reversed_msgs = list(reversed(message_tokens))
        temp_compressed = []
        
        for msg, tokens in reversed_msgs:
            compressed_content = compress_prompt(msg['content'], PromptCompressionLevel.AGGRESSIVE)
            estimated_compressed_tokens = estimate_tokens(compressed_content)
            
            if estimated_compressed_tokens <= remaining_tokens:
                temp_compressed.append({'role': msg['role'], 'content': compressed_content})
                remaining_tokens -= estimated_compressed_tokens
            else:
                # If we can't even fit one message, create a summary
                if not temp_compressed:
                    summary = f"Earlier conversation summary: User discussed {summarize_content(msg['content'])}."
                    summary_tokens = estimate_tokens(summary)
                    
                    if summary_tokens <= remaining_tokens:
                        temp_compressed.append({'role': 'system', 'content': summary})
                break
                
        compressed_msgs = list(reversed(temp_compressed))
    
    # Add compressed messages to result
    compressed_conversation.extend(compressed_msgs)
    
    # Always add the most recent user message
    if last_user_msg:
        compressed_conversation.append(last_user_msg)
    
    return compressed_conversation

def summarize_content(text: str, max_words: int = 20) -> str:
    """
    Create a very short summary of content
    
    Args:
        text: Text to summarize
        max_words: Maximum words in summary
        
    Returns:
        Brief summary of the text
    """
    # Extract most important words (non-stopwords)
    words = re.findall(r'\b\w+\b', text.lower())
    important_words = [word for word in words if word not in STOPWORDS and len(word) > 2]
    
    # Get word frequencies
    word_freq = {}
    for word in important_words:
        word_freq[word] = word_freq.get(word, 0) + 1
    
    # Get top words
    top_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
    top_words = top_words[:min(10, len(top_words))]
    
    # Create summary
    if len(top_words) >= 3:
        topics = ", ".join([word for word, _ in top_words[:3]])
        return topics
    
    # Fallback if we don't have enough important words
    return "their request" if len(text) > 50 else text[:50].strip()

def hash_persistent_content(content: str) -> str:
    """
    Create a short hash for persistent content to reference later
    
    Args:
        content: Content to hash
        
    Returns:
        Short hash string
    """
    return hashlib.md5(content.encode()).hexdigest()[:8]

def compress_prompt_with_references(prompt: str, reference_content: Dict[str, str]) -> Tuple[str, Dict[str, str]]:
    """
    Compress prompt by replacing repeated content with references
    
    Args:
        prompt: Prompt text to compress
        reference_content: Existing reference content dictionary
        
    Returns:
        Tuple of (compressed prompt, updated reference dict)
    """
    # Find chunks of text that could be referenced
    references = reference_content.copy()
    chunks = re.split(r'[.!?]\s+', prompt)
    
    # Only replace chunks that are reasonably long
    MIN_CHUNK_LENGTH = 50
    
    # Process each chunk
    compressed_chunks = []
    
    for chunk in chunks:
        if len(chunk) >= MIN_CHUNK_LENGTH:
            # Check if this chunk is similar to any existing reference
            existing_ref = None
            for ref_id, ref_text in references.items():
                # Simple similarity check (could be improved)
                if len(chunk) > 0.9 * len(ref_text) and len(chunk) < 1.1 * len(ref_text):
                    # Check for substantial overlap
                    common_words = set(chunk.lower().split()) & set(ref_text.lower().split())
                    if len(common_words) > 0.8 * len(set(chunk.lower().split())):
                        existing_ref = ref_id
                        break
            
            if existing_ref:
                # Replace with reference
                compressed_chunks.append(f"[REF:{existing_ref}]")
            else:
                # Store as new reference if reasonably long
                if len(chunk) >= MIN_CHUNK_LENGTH:
                    ref_id = hash_persistent_content(chunk)
                    references[ref_id] = chunk
                    compressed_chunks.append(f"[REF:{ref_id}]")
                else:
                    compressed_chunks.append(chunk)
        else:
            compressed_chunks.append(chunk)
    
    # Join with proper sentence boundaries
    compressed = ""
    for i, chunk in enumerate(compressed_chunks):
        if chunk.startswith("[REF:"):
            if i > 0 and not compressed.endswith(" "):
                compressed += " "
            compressed += chunk
            if i < len(compressed_chunks) - 1:
                compressed += " "
        else:
            compressed += chunk
            if i < len(compressed_chunks) - 1 and not chunk.endswith((".", "!", "?")):
                compressed += ". "
    
    return compressed, references

def expand_references(text: str, references: Dict[str, str]) -> str:
    """
    Expand references in compressed text
    
    Args:
        text: Text with references
        references: Reference content dictionary
        
    Returns:
        Expanded text
    """
    def replace_ref(match):
        ref_id = match.group(1)
        return references.get(ref_id, f"[Unknown reference: {ref_id}]")
    
    return re.sub(r'\[REF:([a-f0-9]+)\]', replace_ref, text) 