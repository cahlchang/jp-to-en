"""
Test cases for the Python parser module.
"""

import os
import tempfile
import unittest
from pathlib import Path

from src.parser.python_parser import PythonParser
from src.parser.parser_base import CodeComment


class TestPythonParser(unittest.TestCase):
    """Test suite for the Python parser."""
    
    def setUp(self):
        """Set up test environment."""
        self.parser = PythonParser()
        
        # Create a temporary directory for test files
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_path = Path(self.temp_dir.name)
    
    def tearDown(self):
        """Clean up test environment."""
        self.temp_dir.cleanup()
    
    def test_supported_extensions(self):
        """Test supported file extensions."""
        extensions = PythonParser.get_supported_extensions()
        self.assertIn(".py", extensions)
        self.assertIn(".pyi", extensions)
    
    def test_parse_single_line_comments(self):
        """Test parsing single line comments."""
        # Create a test file with single line comments
        test_content = """# This is a comment
x = 10  # This is an inline comment
# This is another comment

y = 20
# This is a comment after code
"""
        test_file = self._create_test_file("single_line.py", test_content)
        
        # Parse the file
        comments = self.parser.parse_file(test_file)
        
        # Check results
        self.assertEqual(len(comments), 4)
        self.assertEqual(comments[0].content, "This is a comment")
        self.assertEqual(comments[0].line_number, 1)
        self.assertFalse(comments[0].is_multiline)
        
        self.assertEqual(comments[1].content, "This is an inline comment")
        self.assertEqual(comments[1].line_number, 2)
        
        self.assertEqual(comments[2].content, "This is another comment")
        self.assertEqual(comments[2].line_number, 3)
        
        self.assertEqual(comments[3].content, "This is a comment after code")
        self.assertEqual(comments[3].line_number, 6)
    
    def test_parse_docstrings(self):
        """Test parsing docstrings."""
        # Create a test file with docstrings
        test_content = '''"""Module docstring."""

def function():
    """
    Function docstring.
    Multi-line.
    """
    pass

class MyClass:
    """Class docstring."""
    
    def method(self):
        """Method docstring."""
        pass
'''
        test_file = self._create_test_file("docstrings.py", test_content)
        
        # Parse the file
        comments = self.parser.parse_file(test_file)
        
        # Check results
        self.assertEqual(len(comments), 4)
        self.assertEqual(comments[0].content, "Module docstring.")
        self.assertEqual(comments[0].line_number, 1)
        self.assertFalse(comments[0].is_multiline)  # Single line docstring
        
        self.assertEqual(comments[1].content, "\n    Function docstring.\n    Multi-line.\n    ")
        self.assertEqual(comments[1].line_number, 4)
        self.assertTrue(comments[1].is_multiline)
        
        self.assertEqual(comments[2].content, "Class docstring.")
        self.assertEqual(comments[2].line_number, 10)
        
        self.assertEqual(comments[3].content, "Method docstring.")
        self.assertEqual(comments[3].line_number, 13)
    
    def test_parse_mixed_content(self):
        """Test parsing mixed comments and docstrings."""
        # Create a test file with mixed content
        test_content = '''"""Module docstring."""
# This is a comment

def function():
    """Function docstring."""
    x = 10  # Inline comment
    # Another comment
    pass
'''
        test_file = self._create_test_file("mixed.py", test_content)
        
        # Parse the file
        comments = self.parser.parse_file(test_file)
        
        # Check results
        self.assertEqual(len(comments), 4)
        self.assertEqual(comments[0].content, "Module docstring.")
        self.assertEqual(comments[1].content, "This is a comment")
        self.assertEqual(comments[2].content, "Function docstring.")
        self.assertEqual(comments[3].content, "Inline comment")
    
    def test_parse_japanese_comments(self):
        """Test parsing Japanese comments."""
        # Create a test file with Japanese comments
        test_content = """# これはコメントです
x = 10  # インラインコメント

def function():
    \"\"\"
    関数のドキュメント文字列です。
    複数行に渡ります。
    \"\"\"
    pass
"""
        test_file = self._create_test_file("japanese.py", test_content)
        
        # Parse the file
        comments = self.parser.parse_file(test_file)
        
        # Check results
        self.assertEqual(len(comments), 3)
        self.assertEqual(comments[0].content, "これはコメントです")
        self.assertEqual(comments[1].content, "インラインコメント")
        self.assertEqual(comments[2].content, "\n    関数のドキュメント文字列です。\n    複数行に渡ります。\n    ")
        self.assertTrue(comments[2].is_multiline)
    
    def _create_test_file(self, filename: str, content: str) -> Path:
        """Create a test file with the given content."""
        file_path = self.temp_path / filename
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return file_path


if __name__ == "__main__":
    unittest.main()
