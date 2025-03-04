"""
Diff formatter module for displaying translation results.

This module provides functions to format and display translation results,
including before/after diffs and summary information.
"""

import difflib
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.syntax import Syntax
from rich.table import Table
from rich.text import Text

from jp_to_en.parser.parser_base import CodeComment
from jp_to_en.translator.openai_translator import TranslationResult


class DiffFormatter:
    """Formatter for displaying translation diffs and results."""
    
    def __init__(self, console: Optional[Console] = None):
        """
        Initialize the diff formatter.
        
        Args:
            console: Rich console for output (creates a new one if not provided)
        """
        self.console = console or Console()
    
    def display_translation_result(self, result: TranslationResult) -> None:
        """
        Display a single translation result.
        
        Args:
            result: Translation result to display
        """
        # Create a table to show original and translated text
        table = Table(title="Translation Result", show_header=True, header_style="bold")
        table.add_column("Original (Japanese)", style="yellow")
        table.add_column("Translated (English)", style="green")
        
        table.add_row(result.original_text, result.translated_text)
        
        self.console.print(table)
        
        # Show context if available
        if result.context_before or result.context_after:
            context_table = Table(title="Context", show_header=True, header_style="bold")
            context_table.add_column("Position")
            context_table.add_column("Text")
            
            if result.context_before:
                context_table.add_row("Before", Text(result.context_before, style="dim"))
                
            if result.context_after:
                context_table.add_row("After", Text(result.context_after, style="dim"))
                
            self.console.print(context_table)
    
    def display_file_diff(
        self,
        file_path: Path,
        original_content: str,
        updated_content: str,
        syntax_highlighting: bool = True
    ) -> None:
        """
        Display a unified diff between original and updated file content.
        
        Args:
            file_path: Path to the file
            original_content: Original file content
            updated_content: Updated file content with translations
            syntax_highlighting: Whether to use syntax highlighting
        """
        self.console.print(Panel(f"[bold blue]File: {file_path}[/]"))
        
        # Get file extension for syntax highlighting
        extension = file_path.suffix.lstrip('.')
        
        # Generate unified diff
        diff = list(difflib.unified_diff(
            original_content.splitlines(),
            updated_content.splitlines(),
            fromfile=f"original/{file_path.name}",
            tofile=f"translated/{file_path.name}",
            lineterm=''
        ))
        
        if diff:
            # Join diff lines into a single string
            diff_text = '\n'.join(diff)
            
            # Display diff with syntax highlighting if requested
            if syntax_highlighting:
                self.console.print(Syntax(diff_text, "diff", theme="monokai"))
            else:
                self.console.print(diff_text)
        else:
            self.console.print("[yellow]No changes made to the file.[/]")
    
    def display_translation_summary(
        self,
        processed_files: int,
        translated_files: int,
        translated_comments: int,
        skipped_files: int = 0,
        errors: int = 0
    ) -> None:
        """
        Display a summary of the translation operation.
        
        Args:
            processed_files: Total number of files processed
            translated_files: Number of files with translations
            translated_comments: Total number of comments translated
            skipped_files: Number of files skipped
            errors: Number of errors encountered
        """
        # Create a summary table
        table = Table(title="Translation Summary", show_header=True, header_style="bold")
        table.add_column("Metric", style="cyan")
        table.add_column("Count", justify="right")
        
        table.add_row("Files Processed", str(processed_files))
        table.add_row("Files with Translations", str(translated_files))
        table.add_row("Comments Translated", str(translated_comments))
        
        if skipped_files > 0:
            table.add_row("Files Skipped", str(skipped_files))
            
        if errors > 0:
            table.add_row("Errors", f"[bold red]{errors}[/]")
        
        self.console.print(table)
    
    def display_error(self, message: str, exception: Optional[Exception] = None) -> None:
        """
        Display an error message.
        
        Args:
            message: Error message to display
            exception: Optional exception object
        """
        error_text = f"[bold red]ERROR:[/] {message}"
        
        if exception:
            error_text += f"\n{type(exception).__name__}: {str(exception)}"
            
        self.console.print(Panel(error_text, border_style="red"))
    
    def preview_file_changes(
        self,
        file_path: Path,
        translations: List[Tuple[CodeComment, TranslationResult]]
    ) -> None:
        """
        Preview changes to be made to a file.
        
        Args:
            file_path: Path to the file
            translations: List of (original_comment, translation_result) pairs
        """
        self.console.print(Panel(f"[bold blue]Preview Changes for {file_path}[/]"))
        
        if not translations:
            self.console.print("[yellow]No changes to preview.[/]")
            return
            
        # Create a table to display the changes
        table = Table(show_header=True, header_style="bold")
        table.add_column("Line", style="cyan", justify="right")
        table.add_column("Original (Japanese)", style="yellow")
        table.add_column("Translated (English)", style="green")
        
        for comment, result in translations:
            table.add_row(
                str(comment.line_number),
                comment.content,
                result.translated_text
            )
            
        self.console.print(table)
