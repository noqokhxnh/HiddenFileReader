"""
Main CLI entry point for HiddenFileReader.
"""

import os
import sys
import argparse
from typing import Set
from .constants import TEXT_EN, TEXT_VI, MAX_FILE_SIZE
from .aggregator import aggregate_hidden_files
from .filters import DEFAULT_EXCLUDE_PATTERNS


def main():
    parser = argparse.ArgumentParser(description="HiddenFileReader - Analyze hidden files and directories")
    parser.add_argument("path", nargs="?", default=".", help="Project path to analyze (default: current directory)")
    parser.add_argument("--lang", choices=["en", "vi"], default="en", help="Language for output messages")
    parser.add_argument("--exclude", action="append", help="Additional exclude patterns (can be used multiple times)")
    parser.add_argument("--dry-run", action="store_true", help="Only list files that would be processed, without reading content")
    parser.add_argument("--format", choices=["txt", "md", "json", "sqlite"], default="txt", help="Output format (default: txt)")
    parser.add_argument("--max-size", type=str, help="Maximum file size to process (e.g., 10M, 100K)")
    parser.add_argument("--filter", choices=["all", "dotfiles", "config"], default="all", help="File filtering mode")
    
    args = parser.parse_args()
    
    project_path = os.path.abspath(args.path)
    text = TEXT_EN if args.lang == "en" else TEXT_VI
    
    # Handle exclude patterns
    exclude_patterns = DEFAULT_EXCLUDE_PATTERNS.copy()
    if args.exclude:
        exclude_patterns.update(args.exclude)
    
    # Parse max-size argument
    max_file_size = MAX_FILE_SIZE
    if args.max_size:
        size_str = args.max_size.upper()
        if size_str.endswith('G'):
            max_file_size = int(size_str[:-1]) * 1024 * 1024 * 1024
        elif size_str.endswith('M'):
            max_file_size = int(size_str[:-1]) * 1024 * 1024
        elif size_str.endswith('K'):
            max_file_size = int(size_str[:-1]) * 1024
        else:
            max_file_size = int(size_str)
    
    # Safety check for root filesystem
    if project_path == "/":
        response = input("⚠️  Warning: You are about to scan the entire root filesystem. This may take a very long time and consume significant resources. Continue? (y/N): ")
        if response.lower() != 'y':
            print("❌ Scan cancelled by user.")
            sys.exit(0)
    
    print(text["app_title"])
    print("=" * 50)
    
    success = aggregate_hidden_files(
        project_path, 
        text, 
        exclude_patterns, 
        args.dry_run,
        args.format,
        max_file_size,
        args.filter
    )
    
    if success:
        print(text["done"])
    else:
        print(text["error"])
        sys.exit(1)


if __name__ == "__main__":
    main()