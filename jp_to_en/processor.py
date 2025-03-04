"""
Main processor module for jp-to-en.

This module coordinates the workflow between parsers, detectors, translators, 
and formatters to process files and translate Japanese comments to English.
"""

import logging
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Set

from rich.console import Console
from rich.progress import Progress

# パッケージからのインポート
from jp_to_en.detector.japanese_detector import extract_japanese_text_with_context
from jp_to_en.parser.parser_base import CodeComment
from jp_to_en.parser.parser_factory import ParserFactory
from jp_to_en.translator.openai_translator import OpenAITranslator, TranslationResult
from jp_to_en.formatter.diff_formatter import DiffFormatter


logger = logging.getLogger(__name__)


@dataclass
class ProcessingResult:
    """Results of processing a single file."""
    file_path: Path
    comments_found: int = 0
    japanese_comments_found: int = 0
    comments_translated: int = 0
    has_changes: bool = False
    original_content: str = ""
    updated_content: str = ""
    error: Optional[Exception] = None


@dataclass
class ProcessingSummary:
    """Summary of a batch processing operation."""
    processed_files: int = 0
    translated_files: int = 0
    total_comments: int = 0
    japanese_comments: int = 0
    translated_comments: int = 0
    error_files: int = 0
    skipped_files: int = 0


class Processor:
    """Main processor for translating Japanese comments to English."""
    
    def __init__(
        self,
        api_key: str,
        output_dir: Optional[str] = None,
        dry_run: bool = False,
        verbose: bool = False,
        console: Optional[Console] = None
    ):
        """
        Initialize the processor.
        
        Args:
            api_key: OpenAI API key
            output_dir: Directory to write output files (None for in-place)
            dry_run: Show changes without modifying files
            verbose: Enable verbose output
            console: Rich console for output
        """
        self.api_key = api_key
        self.output_dir = Path(output_dir) if output_dir else None
        self.dry_run = dry_run
        self.verbose = verbose
        self.console = console or Console()
        
        # Initialize components
        self.translator = OpenAITranslator(api_key=api_key)
        self.formatter = DiffFormatter(console=self.console)
        
        # Initialize parser factory
        ParserFactory.initialize()
        
        # Create output directory if necessary
        if self.output_dir and not self.output_dir.exists():
            self.output_dir.mkdir(parents=True)
    
    def process_files(self, file_paths: List[Path]) -> ProcessingSummary:
        """
        Process multiple files, translating Japanese comments to English.
        
        Args:
            file_paths: List of file paths to process
            
        Returns:
            Processing summary
        """
        summary = ProcessingSummary()
        
        with Progress() as progress:
            task = progress.add_task("[green]Processing files...", total=len(file_paths))
            
            for file_path in file_paths:
                try:
                    result = self.process_file(file_path)
                    
                    # Update summary
                    summary.processed_files += 1
                    summary.total_comments += result.comments_found
                    summary.japanese_comments += result.japanese_comments_found
                    summary.translated_comments += result.comments_translated
                    
                    if result.has_changes:
                        summary.translated_files += 1
                        
                    if result.error:
                        summary.error_files += 1
                        
                except Exception as e:
                    logger.error(f"Error processing file {file_path}: {e}")
                    summary.error_files += 1
                
                progress.update(task, advance=1)
        
        # Display summary
        self.formatter.display_translation_summary(
            processed_files=summary.processed_files,
            translated_files=summary.translated_files,
            translated_comments=summary.translated_comments,
            skipped_files=summary.skipped_files,
            errors=summary.error_files
        )
        
        return summary
    
    def process_file(self, file_path: Path) -> ProcessingResult:
        """
        Process a single file, translating Japanese comments to English.
        
        Args:
            file_path: Path to the file to process
            
        Returns:
            Processing result
        """
        if self.verbose:
            self.console.print(f"Processing file: {file_path}")
            
        result = ProcessingResult(file_path=file_path)
        
        # Check if file exists
        if not file_path.exists() or not file_path.is_file():
            logger.error(f"File not found: {file_path}")
            return result
            
        # Get parser for file
        parser = ParserFactory.get_parser_for_file(file_path)
        if not parser:
            if self.verbose:
                self.console.print(f"[yellow]No parser available for {file_path}[/]")
            return result
            
        try:
            # Read file content
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            result.original_content = content
            
            # Parse comments
            comments = parser.parse_file(file_path)
            result.comments_found = len(comments)
            
            if self.verbose:
                self.console.print(f"Found {len(comments)} comments in {file_path}")
                
            # Process each comment
            japanese_comments = []
            translations = []
            
            for comment in comments:
                # Extract Japanese text with context
                japanese_segments = extract_japanese_text_with_context(comment.content)
                
                if japanese_segments:
                    japanese_comments.append(comment)
                    
                    # Translate Japanese segments
                    for context_before, japanese_text, context_after in japanese_segments:
                        translation = self.translator.translate(
                            japanese_text, context_before, context_after
                        )
                        translations.append((comment, translation))
            
            result.japanese_comments_found = len(japanese_comments)
            result.comments_translated = len(translations)
            
            if translations:
                result.has_changes = True
                
                # Preview changes
                if self.verbose or self.dry_run:
                    self.formatter.preview_file_changes(file_path, translations)
                
                # Apply changes if not in dry run mode
                if not self.dry_run:
                    updated_content = self._apply_translations(content, translations)
                    result.updated_content = updated_content
                    
                    # Save changes
                    output_path = self._get_output_path(file_path)
                    
                    with open(output_path, 'w', encoding='utf-8') as f:
                        f.write(updated_content)
                        
                    # Show diff
                    if self.verbose:
                        self.formatter.display_file_diff(
                            file_path, content, updated_content
                        )
            else:
                if self.verbose:
                    self.console.print(f"[yellow]No Japanese comments found in {file_path}[/]")
                    
        except Exception as e:
            logger.error(f"Error processing file {file_path}: {e}")
            result.error = e
            
        return result
    
    def _apply_translations(
        self, 
        content: str, 
        translations: List[Tuple[CodeComment, TranslationResult]]
    ) -> str:
        """
        Apply translations to the file content.
        
        Args:
            content: Original file content
            translations: List of (comment, translation) pairs
            
        Returns:
            Updated file content
        """
        # Sort translations by position in reverse order
        # (to avoid position shifts when replacing text)
        sorted_translations = sorted(
            translations,
            key=lambda t: (t[0].line_number, t[0].column),
            reverse=True
        )
        
        lines = content.splitlines()
        
        # Apply translations to each line
        for comment, translation in sorted_translations:
            # Get the comment line
            line_idx = comment.line_number - 1
            if line_idx >= len(lines):
                continue
                
            line = lines[line_idx]
            
            # Replace Japanese text with English translation in the line
            # This is a simplified approach and may need more sophisticated
            # handling for complex comments
            if comment.is_multiline:
                # For multiline comments, replace content within comment markers
                # This is a simplified approach and may need more sophisticated
                # handling for different formats
                updated_line = line.replace(comment.content, translation.translated_text)
            else:
                # For single-line comments, replace after the comment marker
                comment_start = line.find('#')
                if comment_start >= 0:
                    before_comment = line[:comment_start + 1]
                    updated_line = before_comment + ' ' + translation.translated_text
                else:
                    updated_line = line
                    
            lines[line_idx] = updated_line
            
        return '\n'.join(lines)
    
    def _get_output_path(self, file_path: Path) -> Path:
        """
        Get the output path for a file.
        
        Args:
            file_path: Original file path
            
        Returns:
            Output file path
        """
        if self.output_dir:
            # Create relative path from original file to maintain directory structure
            try:
                rel_path = file_path.relative_to(Path.cwd())
            except ValueError:
                # If not a subpath, use the filename only
                rel_path = file_path.name
                
            return self.output_dir / rel_path
        else:
            # In-place modification
            return file_path
