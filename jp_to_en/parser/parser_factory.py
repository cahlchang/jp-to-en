"""
Parser factory module for selecting the appropriate parser based on file extension.
"""

import importlib
import inspect
import pkgutil
from pathlib import Path
from typing import Dict, List, Optional, Type

# パッケージからのインポート
from jp_to_en.parser.parser_base import SourceCodeParser


class ParserFactory:
    """Factory for creating language-specific source code parsers."""
    
    _parsers: Dict[str, Type[SourceCodeParser]] = {}
    _initialized = False
    
    @classmethod
    def initialize(cls) -> None:
        """
        Initialize the parser factory by discovering all available parsers.
        """
        if cls._initialized:
            return
            
        # Import all modules in the parser package
        import jp_to_en.parser as parser_pkg
        package_prefix = "jp_to_en.parser"
        
        for _, modname, _ in pkgutil.iter_modules(parser_pkg.__path__):
            if modname == "parser_base" or modname == "parser_factory":
                continue
                
            module = importlib.import_module(f"{package_prefix}.{modname}")
            
            # Find parser classes in the module
            for name, obj in inspect.getmembers(module):
                if (inspect.isclass(obj) and 
                    hasattr(obj, "get_supported_extensions") and
                    callable(getattr(obj, "get_supported_extensions"))):
                    
                    # Register the parser with its supported extensions
                    for ext in obj.get_supported_extensions():
                        cls._parsers[ext] = obj
        
        cls._initialized = True
    
    @classmethod
    def get_parser_for_file(cls, file_path: Path) -> Optional[SourceCodeParser]:
        """
        Get the appropriate parser for a given file.
        
        Args:
            file_path: Path to the source code file
            
        Returns:
            An instance of the appropriate parser, or None if no parser is available
        """
        if not cls._initialized:
            cls.initialize()
            
        ext = file_path.suffix.lower()
        parser_class = cls._parsers.get(ext)
        
        if parser_class:
            return parser_class()
        
        return None
    
    @classmethod
    def get_supported_extensions(cls) -> List[str]:
        """
        Get all file extensions supported by the registered parsers.
        
        Returns:
            List of supported file extensions
        """
        if not cls._initialized:
            cls.initialize()
            
        return list(cls._parsers.keys())
    
    @classmethod
    def register_parser(cls, extension: str, parser_class: Type[SourceCodeParser]) -> None:
        """
        Manually register a parser for a specific file extension.
        
        Args:
            extension: File extension (e.g., '.py')
            parser_class: Parser class to register
        """
        if not cls._initialized:
            cls.initialize()
            
        cls._parsers[extension.lower()] = parser_class
