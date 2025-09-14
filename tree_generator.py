"""
Directory tree generator for hidden files and directories.
"""

import os
from typing import List, Set
from pathlib import Path
from .filters import should_include_path, should_include_file, is_hidden_file_or_dir


def generate_hidden_directory_tree(project_path: str, include_dirs: Set[str], include_files: Set[str]) -> str:
    """
    Generate a directory tree structure focusing on hidden/build files.
    """
    tree_lines: List[str] = []
    project_name: str = os.path.basename(project_path.rstrip(os.sep))
    tree_lines.append(f"{project_name}/")

    def add_directory_content(current_path: str, prefix: str = "") -> None:
        try:
            items: List[str] = sorted(os.listdir(current_path))
            dirs: List[str] = [
                item
                for item in items
                if os.path.isdir(os.path.join(current_path, item))
            ]
            files: List[str] = [
                item
                for item in items
                if os.path.isfile(os.path.join(current_path, item))
            ]

            # Filter directories to only include hidden/build ones
            included_dirs = []
            for dirname in dirs:
                dir_path = os.path.join(current_path, dirname)
                # Include if it matches our patterns or is a hidden directory
                if should_include_path(dir_path, include_dirs) or is_hidden_file_or_dir(dir_path):
                    included_dirs.append(dirname)

            # Filter files to only include hidden/config/log ones
            included_files = []
            for filename in files:
                # Include if it matches our patterns or is a hidden file
                if should_include_file(filename, include_files) or is_hidden_file_or_dir(filename):
                    included_files.append(filename)

            # Display directories
            for i, dirname in enumerate(included_dirs):
                is_last_dir = (i == len(included_dirs) - 1) and len(included_files) == 0
                tree_lines.append(
                    f"{prefix}{'└── ' if is_last_dir else '├── '}{dirname}/"
                )
                next_prefix = prefix + ("    " if is_last_dir else "│   ")
                add_directory_content(
                    os.path.join(current_path, dirname), next_prefix
                )

            # Display files
            for i, filename in enumerate(included_files):
                is_last = i == len(included_files) - 1
                tree_lines.append(
                    f"{prefix}{'└── ' if is_last else '├── '}{filename}"
                )

        except PermissionError:
            tree_lines.append(f"{prefix}├── [Permission Denied]")

    add_directory_content(project_path)
    return "\n".join(tree_lines)