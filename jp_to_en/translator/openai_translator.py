"""
OpenAI API translator module.

This module provides functionality to translate Japanese text to English
using OpenAI's translate model.
"""

import logging
import time
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

import openai

logger = logging.getLogger(__name__)


@dataclass
class TranslationResult:
    """Represents the result of a translation operation."""
    original_text: str
    translated_text: str
    context_before: str = ""
    context_after: str = ""
    confidence: float = 0.0
    model_used: str = ""


class OpenAITranslator:
    """Translator using OpenAI's API for Japanese to English translation."""
    
    def __init__(
        self, 
        api_key: str, 
        model: str = "text-translation-3", 
        max_retries: int = 3,
        retry_delay: float = 1.0
    ):
        """
        Initialize the OpenAI translator.
        
        Args:
            api_key: OpenAI API key
            model: Translation model to use
            max_retries: Maximum number of retries for failed API calls
            retry_delay: Initial delay between retries (in seconds)
        """
        self.api_key = api_key
        self.model = model
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.client = openai.OpenAI(api_key=api_key)
    
    def translate(
        self, 
        text: str, 
        context_before: str = "", 
        context_after: str = ""
    ) -> TranslationResult:
        """
        Translate Japanese text to English, considering the context.
        
        Args:
            text: Japanese text to translate
            context_before: Text appearing before the Japanese text
            context_after: Text appearing after the Japanese text
            
        Returns:
            TranslationResult object containing the translated text
        """
        if not text.strip():
            return TranslationResult(original_text=text, translated_text=text)
        
        # Prepare prompt with context
        prompt = self._create_prompt(text, context_before, context_after)
        
        # Call API with retries
        for attempt in range(self.max_retries):
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": "You are a professional translator specializing in translating programming comments and documentation from Japanese to English. Maintain the technical meaning and nuance. Provide only the translated text without explanations."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.3,  # Lower temperature for more consistent translations
                )
                
                translated_text = response.choices[0].message.content.strip()
                
                return TranslationResult(
                    original_text=text,
                    translated_text=translated_text,
                    context_before=context_before,
                    context_after=context_after,
                    model_used=self.model
                )
                
            except (openai.RateLimitError, openai.APITimeoutError) as e:
                logger.warning(f"Rate limit or timeout error: {e}. Retrying in {self.retry_delay}s...")
                if attempt < self.max_retries - 1:
                    # Exponential backoff
                    time.sleep(self.retry_delay * (2 ** attempt))
                else:
                    logger.error(f"Failed to translate after {self.max_retries} attempts: {e}")
                    return TranslationResult(original_text=text, translated_text=text)
                    
            except Exception as e:
                logger.error(f"Translation error: {e}")
                return TranslationResult(original_text=text, translated_text=text)
    
    def batch_translate(
        self, 
        texts_with_context: List[Tuple[str, str, str]]
    ) -> List[TranslationResult]:
        """
        Translate multiple Japanese text segments in a batch.
        
        Args:
            texts_with_context: List of tuples (japanese_text, context_before, context_after)
            
        Returns:
            List of TranslationResult objects
        """
        results = []
        
        for text, context_before, context_after in texts_with_context:
            result = self.translate(text, context_before, context_after)
            results.append(result)
            
            # Add a small delay to avoid rate limits
            time.sleep(0.1)
            
        return results
    
    def _create_prompt(self, text: str, context_before: str, context_after: str) -> str:
        """
        Create a prompt for the OpenAI API that includes the text and context.
        
        Args:
            text: Japanese text to translate
            context_before: Text appearing before the Japanese text
            context_after: Text appearing after the Japanese text
            
        Returns:
            Formatted prompt string
        """
        prompt = "Translate the following Japanese text to English:\n\n"
        
        if context_before:
            prompt += f"Context before: {context_before}\n\n"
            
        prompt += f"Text to translate: {text}\n\n"
        
        if context_after:
            prompt += f"Context after: {context_after}\n\n"
            
        prompt += "Translation:"
        
        return prompt
