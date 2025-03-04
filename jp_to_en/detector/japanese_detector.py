"""
Japanese text detection module.

This module provides functions to detect Japanese text in source code comments.
"""

import re
from dataclasses import dataclass
from typing import List, Optional, Tuple

import langdetect
from langdetect import DetectorFactory
from langdetect.lang_detect_exception import LangDetectException

# Set fixed random seed for consistent language detection
DetectorFactory.seed = 0


@dataclass
class JapaneseTextSpan:
    """A span of Japanese text found in a string."""
    text: str
    start_pos: int
    end_pos: int
    context_before: str = ""
    context_after: str = ""


def contains_japanese_chars(text: str) -> bool:
    """
    Check if the text contains Japanese characters (Hiragana, Katakana, or Kanji).
    
    Args:
        text: The text to check
        
    Returns:
        True if the text contains Japanese characters, False otherwise
    """
    # Unicode ranges for Japanese characters
    # Hiragana: U+3040-U+309F
    # Katakana: U+30A0-U+30FF
    # Kanji: U+4E00-U+9FAF
    japanese_pattern = re.compile(r'[\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FAF]')
    return bool(japanese_pattern.search(text))


def is_japanese_text(text: str, min_confidence: float = 0.5) -> bool:
    """
    Determine if a text is Japanese.
    
    Args:
        text: The text to analyze
        min_confidence: Minimum confidence level to consider the text Japanese
        
    Returns:
        True if the text is detected as Japanese, False otherwise
    """
    # Quick check for Japanese characters
    if not contains_japanese_chars(text):
        return False
    
    # For very short texts, rely on character detection
    if len(text) < 15:
        # Require a higher density of Japanese characters for short texts
        japanese_chars = sum(1 for c in text if '\u3040' <= c <= '\u309F' or 
                                              '\u30A0' <= c <= '\u30FF' or 
                                              '\u4E00' <= c <= '\u9FAF')
        return japanese_chars / len(text) > 0.4
    
    # For longer texts, use langdetect
    try:
        # Get language probabilities
        probabilities = langdetect.detect_langs(text)
        
        # Check if Japanese is the most likely language with sufficient confidence
        for prob in probabilities:
            if prob.lang == 'ja' and prob.prob >= min_confidence:
                return True
                
        return False
    except LangDetectException:
        # Fallback to character-based detection if langdetect fails
        japanese_chars = sum(1 for c in text if '\u3040' <= c <= '\u309F' or 
                                              '\u30A0' <= c <= '\u30FF' or 
                                              '\u4E00' <= c <= '\u9FAF')
        return japanese_chars / len(text) > 0.2


def find_japanese_spans(text: str, context_size: int = 50) -> List[JapaneseTextSpan]:
    """
    Find spans of Japanese text in a string with surrounding context.
    
    Args:
        text: The text to analyze
        context_size: Number of characters to include as context before and after
        
    Returns:
        List of JapaneseTextSpan objects
    """
    if not text or not contains_japanese_chars(text):
        return []
    
    results = []
    
    # Split text into sentences or segments
    segments = re.split(r'([.!?。！？\n]+)', text)
    
    current_pos = 0
    for segment in segments:
        if not segment:
            current_pos += len(segment)
            continue
            
        if is_japanese_text(segment):
            # Get context before
            start_context = max(0, current_pos - context_size)
            context_before = text[start_context:current_pos]
            
            # Get context after
            end_pos = current_pos + len(segment)
            end_context = min(len(text), end_pos + context_size)
            context_after = text[end_pos:end_context]
            
            results.append(JapaneseTextSpan(
                text=segment,
                start_pos=current_pos,
                end_pos=end_pos,
                context_before=context_before,
                context_after=context_after
            ))
        
        current_pos += len(segment)
    
    return results


def extract_japanese_text_with_context(text: str) -> List[Tuple[str, str, str]]:
    """
    Extract Japanese text segments with their surrounding context.
    
    Args:
        text: The text to analyze
        
    Returns:
        List of tuples (context_before, japanese_text, context_after)
    """
    spans = find_japanese_spans(text)
    return [(span.context_before, span.text, span.context_after) for span in spans]
