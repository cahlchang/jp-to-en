"""
Test cases for the Japanese text detector module.
"""

import unittest
from src.detector.japanese_detector import (
    contains_japanese_chars,
    is_japanese_text,
    find_japanese_spans,
    extract_japanese_text_with_context
)


class TestJapaneseDetector(unittest.TestCase):
    """Test suite for the Japanese text detector."""
    
    def test_contains_japanese_chars(self):
        """Test detection of Japanese characters."""
        # Test with Japanese text
        self.assertTrue(contains_japanese_chars("こんにちは"))
        self.assertTrue(contains_japanese_chars("日本語"))
        self.assertTrue(contains_japanese_chars("これはテストです"))
        
        # Test with mixed text
        self.assertTrue(contains_japanese_chars("Hello こんにちは World"))
        self.assertTrue(contains_japanese_chars("This is a 日本語 test"))
        
        # Test with non-Japanese text
        self.assertFalse(contains_japanese_chars("Hello World"))
        self.assertFalse(contains_japanese_chars("This is a test"))
        self.assertFalse(contains_japanese_chars("1234567890"))
    
    def test_is_japanese_text(self):
        """Test detection of Japanese text."""
        # Test with Japanese text
        self.assertTrue(is_japanese_text("こんにちは"))
        self.assertTrue(is_japanese_text("日本語のテキスト"))
        
        # Test with mixed text - should detect if enough Japanese
        self.assertTrue(is_japanese_text("これは a test です"))
        
        # Test with non-Japanese text
        self.assertFalse(is_japanese_text("Hello World"))
        self.assertFalse(is_japanese_text("This is a test"))
        
        # Test with short text that has some Japanese
        self.assertTrue(is_japanese_text("あa"))  # 50% Japanese
    
    def test_find_japanese_spans(self):
        """Test finding Japanese spans in text."""
        # Test with simple Japanese text
        spans = find_japanese_spans("こんにちは")
        self.assertEqual(len(spans), 1)
        self.assertEqual(spans[0].text, "こんにちは")
        
        # Test with mixed text
        mixed_text = "Hello こんにちは. This is a 日本語 test."
        spans = find_japanese_spans(mixed_text)
        self.assertEqual(len(spans), 2)
        self.assertEqual(spans[0].text, "こんにちは")
        self.assertEqual(spans[1].text, "日本語")
        
        # Test with context
        spans = find_japanese_spans(mixed_text, context_size=10)
        self.assertEqual(len(spans), 2)
        self.assertTrue("Hello " in spans[0].context_before)
        self.assertTrue(". This" in spans[0].context_after)
        
        # Test with no Japanese text
        spans = find_japanese_spans("Hello World")
        self.assertEqual(len(spans), 0)
    
    def test_extract_japanese_text_with_context(self):
        """Test extracting Japanese text with context."""
        # Test with mixed text
        mixed_text = "Hello こんにちは. This is a 日本語 test."
        extracts = extract_japanese_text_with_context(mixed_text)
        
        self.assertEqual(len(extracts), 2)
        
        # Check first extraction
        before1, text1, after1 = extracts[0]
        self.assertEqual(text1, "こんにちは")
        self.assertTrue("Hello " in before1)
        self.assertTrue(". This" in after1)
        
        # Check second extraction
        before2, text2, after2 = extracts[1]
        self.assertEqual(text2, "日本語")
        self.assertTrue("This is a " in before2)
        self.assertTrue(" test." in after2)
        
        # Test with no Japanese text
        extracts = extract_japanese_text_with_context("Hello World")
        self.assertEqual(len(extracts), 0)


if __name__ == "__main__":
    unittest.main()
