#!/usr/bin/env python3
"""
jp-to-en: A CLI tool to convert Japanese comments in code to English.

This is the main entry point for the command-line interface.
"""

import argparse
import logging
import os
import sys
from pathlib import Path
from typing import List, Optional

from rich.console import Console
from rich.logging import RichHandler

# パッケージからのインポート
from jp_to_en.processor import Processor
from jp_to_en.config_manager import ConfigManager


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    handlers=[RichHandler(rich_tracebacks=True)]
)
logger = logging.getLogger("jp-to-en")
console = Console()


def setup_argparser() -> argparse.ArgumentParser:
    """Set up and return the argument parser for CLI options."""
    parser = argparse.ArgumentParser(
        description="Convert Japanese comments in code to English"
    )
    
    parser.add_argument(
        "paths",
        nargs="*",
        type=str,
        help="Files or directories to process (default: current directory)",
    )
    
    parser.add_argument(
        "--recursive", "-r",
        action="store_true",
        help="Process directories recursively",
    )
    
    parser.add_argument(
        "--output-dir", "-o",
        type=str,
        help="Directory to write output files (if not specified, files are modified in-place)",
    )
    
    parser.add_argument(
        "--dry-run", "-d",
        action="store_true",
        help="Show changes without modifying files",
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose output",
    )
    
    parser.add_argument(
        "--quiet", "-q",
        action="store_true",
        help="Suppress all output except errors",
    )
    
    parser.add_argument(
        "--api-key", "-k",
        type=str,
        help="OpenAI API key (can also be set via OPENAI_API_KEY environment variable)",
    )
    
    parser.add_argument(
        "--save-api-key",
        action="store_true",
        help="Save the provided API key for future use",
    )
    
    parser.add_argument(
        "--config", "-c",
        type=str,
        help="Path to configuration file",
    )
    
    return parser


def find_files(paths: List[str], recursive: bool = False) -> List[Path]:
    """
    Find all files to process based on the given paths.
    
    Args:
        paths: List of file or directory paths to process
        recursive: Whether to search directories recursively
        
    Returns:
        List of Path objects for files to process
    """
    result = []
    
    for path_str in paths:
        path = Path(path_str)
        
        if not path.exists():
            logger.warning(f"Path does not exist: {path}")
            continue
            
        if path.is_file():
            result.append(path)
        elif path.is_dir():
            if recursive:
                for file_path in path.glob("**/*"):
                    if file_path.is_file():
                        result.append(file_path)
            else:
                for file_path in path.glob("*"):
                    if file_path.is_file():
                        result.append(file_path)
    
    return result


def main() -> int:
    """
    Main entry point for the CLI application.
    
    Returns:
        Exit code (0 for success, non-zero for errors)
    """
    # Parse command-line arguments
    parser = setup_argparser()
    args = parser.parse_args()
    
    # Configure logging based on verbosity flags
    if args.verbose:
        logger.setLevel(logging.DEBUG)
    elif args.quiet:
        logger.setLevel(logging.ERROR)
    
    # Initialize config manager
    config_manager = ConfigManager()
    
    # Get API key with priority: args > environment > saved
    api_key = args.api_key or os.environ.get("OPENAI_API_KEY") or config_manager.get_api_key()
    
    if not api_key:
        logger.error(
            "OpenAI API key not provided. Please use one of the following methods:\n"
            "1. Use --api-key option\n"
            "2. Set OPENAI_API_KEY environment variable\n"
            "3. Save an API key using --save-api-key option\n"
            "\nTo get an OpenAI API key, visit: https://platform.openai.com/api-keys"
        )
        return 1
    
    # Save API key if requested
    if args.save_api_key and args.api_key:
        if config_manager.set_api_key(args.api_key):
            logger.info("API key saved successfully to ~/.jp-to-en/credentials.json")
        else:
            logger.warning("Failed to save API key")
    
    # Use current directory if no paths specified
    paths = args.paths
    if not paths:
        paths = ["."]
        # Default to recursive if processing current directory without explicit paths
        if not args.recursive:
            logger.info("Processing current directory. Use -r for recursive processing.")
    
    # Find files to process
    files = find_files(paths, args.recursive)
    if not files:
        logger.error("No files found to process.")
        return 1
    
    # Show recursive info if using -r
    if args.recursive:
        logger.info(f"Found {len(files)} file(s) recursively")
    else:
        logger.info(f"Found {len(files)} file(s) to process (use -r for recursive)")
    
    # Process files
    processor = Processor(
        api_key=api_key,
        output_dir=args.output_dir,
        dry_run=args.dry_run,
        verbose=args.verbose,
        console=console
    )
    
    summary = processor.process_files(files)
    
    # Return error if no files were processed successfully
    if summary.processed_files == 0 or summary.error_files == summary.processed_files:
        return 1
        
    return 0


if __name__ == "__main__":
    sys.exit(main())
