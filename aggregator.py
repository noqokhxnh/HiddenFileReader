"""
Main aggregator module to collect hidden file contents.
"""

import os
from typing import Dict, List, Set, Optional
from pathlib import Path
from .constants import MAX_FILE_SIZE
from .filters import get_include_patterns, should_include_path, should_include_file, is_hidden_file_or_dir, DEFAULT_EXCLUDE_PATTERNS, should_exclude_path
from .tree_generator import generate_hidden_directory_tree
from .output_formats import write_markdown_output, write_json_output, write_sqlite_output


def is_binary_file(file_path: str) -> bool:
    """
    Check if a file is binary by reading a small portion of it.
    Returns True if the file appears to be binary.
    """
    try:
        with open(file_path, "rb") as f:
            chunk = f.read(1024)  # Read first 1KB
            # Check for null bytes which are common in binary files
            if b'\\x00' in chunk:
                return True
            # Check if most characters are non-printable
            text_chars = bytearray({7,8,9,10,12,13,27} | set(range(0x20, 0x100)) - {0x7f})
            printable_count = sum(1 for byte in chunk if byte in text_chars)
            return printable_count / len(chunk) < 0.7 if chunk else False
    except:
        return True  # If we can't read the file, treat as binary


def aggregate_hidden_files(project_path: str, text: Dict[str, str], exclude_patterns: Optional[Set[str]] = None, 
                          dry_run: bool = False, output_format: str = "txt", max_file_size: int = MAX_FILE_SIZE,
                          file_filter: str = "all") -> bool:
    """Main function to aggregate hidden files and directories"""
    if not os.path.isdir(project_path):
        print(text["not_found"].format(path=project_path))
        return False

    # Use default exclude patterns if none provided
    if exclude_patterns is None:
        exclude_patterns = DEFAULT_EXCLUDE_PATTERNS

    print(text["analyzing"] + project_path)
    print(text["scanning"])

    include_dirs, include_files = get_include_patterns()
    print(text["included_types"] + ", ".join(sorted(include_files)))

    content_lines: List[str] = []
    content_lines.append("# " + "=" * 50)
    content_lines.append(f"# Path: {project_path}")
    content_lines.append("# Hidden File Analysis")
    content_lines.append("# " + "=" * 50)
    content_lines.append("")

    print(text["generating_tree"])
    content_lines.append("## DIRECTORY STRUCTURE")
    content_lines.append("```")
    content_lines.append(generate_hidden_directory_tree(project_path, include_dirs, include_files))
    content_lines.append("```")
    content_lines.append("")

    print(text["processing_files"])
    content_lines.append("## FILE CONTENTS")
    content_lines.append("")

    file_count: int = 0
    total_size: int = 0
    total_lines: int = 0
    file_contents: Dict[str, str] = {}  # For JSON/SQLite output

    for root, dirs, files in os.walk(project_path):
        # Filter directories to exclude system folders and large directories
        dirs[:] = [
            d
            for d in dirs
            if not should_exclude_path(os.path.join(root, d), exclude_patterns)
        ]
        
        # Also filter to only traverse directories that might contain hidden files
        dirs[:] = [
            d
            for d in dirs
            if should_include_path(os.path.join(root, d), include_dirs) or 
               is_hidden_file_or_dir(os.path.join(root, d))
        ]

        for file in files:
            file_path = os.path.join(root, file)
            rel_path = os.path.relpath(file_path, project_path)
            
            # Skip files in excluded directories
            if should_exclude_path(file_path, exclude_patterns):
                continue

            # Apply file filtering based on --dotfiles, --config, --all options
            is_dotfile = is_hidden_file_or_dir(file_path)
            is_config_file = should_include_file(file, {".env", ".env.*", "*.env", "*.env.*", "*.ini", "*.toml", "*.yaml", "*.yml", "*.json", "*.xml"})
            
            if file_filter == "dotfiles" and not is_dotfile:
                continue
            elif file_filter == "config" and not is_config_file:
                continue
            # For "all", we include everything that passes other filters

            # Include file if it matches our patterns or is hidden
            if not (should_include_file(file, include_files) or is_hidden_file_or_dir(file_path)):
                continue

            try:
                file_size = os.path.getsize(file_path)
                if file_size > max_file_size:
                    print(
                        text["skip_large"].format(
                            file=rel_path, size=file_size, limit=max_file_size
                        )
                    )
                    continue

                # Skip binary files
                if is_binary_file(file_path):
                    print(text["skip_binary"].format(file=rel_path))
                    continue

                print(text["processing"].format(file=rel_path))
                
                # If dry run, just count files without reading content
                if dry_run:
                    file_count += 1
                    total_size += file_size
                    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                        total_lines += sum(1 for _ in f)
                    continue
                
                with open(
                    file_path, "r", encoding="utf-8", errors="ignore"
                ) as f:
                    file_content = f.read()

                # Store content for different output formats
                file_contents[rel_path] = file_content

                # For text output, add to content_lines
                if output_format == "txt" or output_format == "md":
                    content_lines.append(f"### {rel_path}")
                    content_lines.append("```")
                    content_lines.append(file_content)
                    content_lines.append("```")
                    content_lines.append("")

                file_count += 1
                total_size += len(file_content)
                total_lines += file_content.count('\\n') + 1

            except Exception as e:
                if not dry_run:
                    if output_format == "txt" or output_format == "md":
                        content_lines.append(f"### {rel_path}")
                        content_lines.append(
                            f"```\n# Error reading file: {str(e)}\n```"
                        )
                        content_lines.append("")
                    else:
                        file_contents[rel_path] = f"# Error reading file: {str(e)}"

    # Handle dry run output
    if dry_run:
        print("")
        print("🔍 DRY RUN - Files that would be processed:")
        print(text["summary"])
        print(text["file_count"].format(count=file_count))
        print(text["size"].format(size=total_size, kb=total_size // 1024))
        print(text["line_count"].format(lines=total_lines))
        return True

    # Write output based on format
    base_output_path = os.path.join(project_path, "hidden_dump")
    
    if output_format == "json":
        output_path = write_json_output(file_contents, base_output_path + ".json")
    elif output_format == "sqlite":
        output_path = write_sqlite_output(file_contents, base_output_path + ".db")
    elif output_format == "md":
        output_path = write_markdown_output(content_lines, base_output_path + ".md")
    else:  # txt format
        output_path = base_output_path + ".txt"
        final_content = "\n".join(content_lines)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(final_content)

    print("")
    print(text["success"] + output_path)
    print("")
    print(text["summary"])
    print(text["file_count"].format(count=file_count))
    print(
        text["size"].format(size=total_size, kb=total_size // 1024)
    )
    print(text["line_count"].format(lines=total_lines))
    return True