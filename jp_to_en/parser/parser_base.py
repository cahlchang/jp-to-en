"""
Base parser interface for extracting comments from source code.

This module defines the interface that all language-specific parsers must implement.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import List, Protocol, Optional


@dataclass
class CodeComment:
    """Represents a comment extracted from source code."""
    content: str  # The text content of the comment
    line_number: int  # The line number where the comment starts
    column: int  # The column where the comment starts
    is_multiline: bool  # Whether this is a multi-line comment
    file_path: Optional[Path] = None  # The source file path
    
    @property
    def is_block_comment(self) -> bool:
        """Returns True if this is a block/multi-line comment."""
        return self.is_multiline


class SourceCodeParser(Protocol):
    """Protocol defining the interface for source code parsers."""
    
    def parse_file(self, file_path: Path) -> List[CodeComment]:
        """
        Parse a source code file and extract all comments.
        
        Args:
            file_path: Path to the source code file
            
        Returns:
            List of extracted comments
        """
        ...
    
    def parse_string(self, content: str, filename: Optional[str] = None) -> List[CodeComment]:
        """
        Parse source code from a string and extract all comments.
        
        Args:
            content: Source code as a string
            filename: Optional filename for reference
            
        Returns:
            List of extracted comments
        """
        ...
    
    @classmethod
    def get_supported_extensions(cls) -> List[str]:
        """
        Get the list of file extensions supported by this parser.
        
        Returns:
            List of supported file extensions (e.g., ['.py', '.pyi'])
        """
        ...
