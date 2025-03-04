"""
Python source code parser for extracting comments.

This module provides a parser for extracting comments from Python source code files.
"""

import re
from pathlib import Path
from typing import List, Optional, Tuple

try:
    # パッケージとしてインストール時
    from jp_to_en.parser.parser_base import CodeComment
except ImportError:
    # 開発環境での実行時
    from src.parser.parser_base import CodeComment


class PythonParser:
    """Parser for extracting comments from Python source code."""
    
    @classmethod
    def get_supported_extensions(cls) -> List[str]:
        """
        Get the list of file extensions supported by this parser.
        
        Returns:
            List of supported file extensions
        """
        return ['.py', '.pyi']
    
    def parse_file(self, file_path: Path) -> List[CodeComment]:
        """
        Parse a Python source file and extract all comments.
        
        Args:
            file_path: Path to the Python source file
            
        Returns:
            List of extracted comments
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            return self.parse_string(content, str(file_path))
        except UnicodeDecodeError:
            # Try with alternative encoding
            with open(file_path, 'r', encoding='latin-1') as f:
                content = f.read()
            return self.parse_string(content, str(file_path))
    
    def parse_string(self, content: str, filename: Optional[str] = None) -> List[CodeComment]:
        """
        Parse Python source code from a string and extract all comments.
        
        Args:
            content: Python source code as a string
            filename: Optional filename for reference
            
        Returns:
            List of extracted comments
        """
        file_path = Path(filename) if filename else None
        comments = []
        
        # Find all comments and docstrings
        line_comments = self._extract_line_comments(content)
        docstrings = self._extract_docstrings(content)
        
        # Process line comments
        for line_num, col, comment_text in line_comments:
            comments.append(CodeComment(
                content=comment_text,
                line_number=line_num,
                column=col,
                is_multiline=False,
                file_path=file_path
            ))
        
        # Process docstrings
        for line_num, col, docstring_text, is_multiline in docstrings:
            comments.append(CodeComment(
                content=docstring_text,
                line_number=line_num,
                column=col,
                is_multiline=is_multiline,
                file_path=file_path
            ))
        
        # Sort comments by line number
        comments.sort(key=lambda c: (c.line_number, c.column))
        
        return comments
    
    def _extract_line_comments(self, content: str) -> List[Tuple[int, int, str]]:
        """
        Extract all line comments (# comments) from Python code.
        
        Args:
            content: Python source code
            
        Returns:
            List of tuples (line_number, column, comment_text)
        """
        results = []
        lines = content.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            # Find the start of the comment
            comment_match = re.search(r'(^|\s)#\s*(.*?)$', line)
            if comment_match:
                # Calculate the column position
                col = comment_match.start()
                
                # Extract the comment text (excluding the # character)
                comment_text = comment_match.group(2)
                
                results.append((line_num, col, comment_text))
        
        return results
    
    def _extract_docstrings(self, content: str) -> List[Tuple[int, int, str, bool]]:
        """
        Extract all docstrings from Python code.
        
        Args:
            content: Python source code
            
        Returns:
            List of tuples (line_number, column, docstring_text, is_multiline)
        """
        results = []
        
        # Handle triple-quoted docstrings (both """ and ''')
        # We use a regex pattern that captures the docstring delimiter and content
        docstring_pattern = re.compile(r'("""|\'\'\')(.*?)\1|'
                                       r'("""|\'\'\')(.*?)(?:\1|$)',
                                       re.DOTALL)
        
        for match in docstring_pattern.finditer(content):
            # The docstring content is either in group 2 or 4
            docstring_text = match.group(2) or match.group(4) or ''
            
            # Calculate line number and column
            start_pos = match.start()
            preceding_text = content[:start_pos]
            line_num = preceding_text.count('\n') + 1
            
            # Calculate column position
            last_newline = preceding_text.rfind('\n')
            if last_newline == -1:
                col = start_pos
            else:
                col = start_pos - last_newline - 1
            
            # Determine if it's multiline
            is_multiline = '\n' in docstring_text
            
            results.append((line_num, col, docstring_text, is_multiline))
        
        return results
