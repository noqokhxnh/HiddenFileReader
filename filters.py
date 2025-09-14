"""
Filters for identifying hidden files and directories to include in the dump.
"""

from pathlib import Path
from typing import Set, Tuple, Union


# Default exclude patterns for system directories and common large directories
DEFAULT_EXCLUDE_PATTERNS = {
    # Linux system folders
    "/proc",
    "/sys",
    "/dev",
    # Common large directories
    "node_modules",
    ".git",
    "__pycache__",
    "venv",
    ".venv",
    ".cache",
    # Build artifacts that are typically large
    "build",
    "dist",
    "target"
}


def get_include_patterns() -> Tuple[Set[str], Set[str]]:
    """
    Returns patterns for directories and files that should be included
    (these are typically hidden or build-related files that ProjectDump excludes)
    """
    # Directories to include (typically hidden or build directories)
    include_dirs = {
        # Build artifacts
        "dist",
        "build",
        "target",
        "out",
        "bin",
        "obj",
        "generated",
        # Framework build folders
        ".next",
        ".nuxt",
        ".angular",
        ".expo",
        # Logs directories
        "logs",
        "log",
        # Temp directories
        "temp",
        "tmp",
        ".tmp",
        # Configuration directories
        ".vscode",
        ".idea",
        ".vs",
        # Version control metadata
        ".git",
        ".svn",
        ".hg",
        # Dependency directories not covered above
        ".venv",
        "venv",
        "env",
        ".env",
        "__pycache__",
        # CI/CD directories
        ".github",
        ".gitlab",
        ".circleci",
        # Docker
        ".docker",
        "docker",
        # Database directories
        "db",
        "database",
        "sqlite",
    }

    # File patterns to include (typically hidden config or log files)
    include_files = {
        # Log files
        "*.log",
        "*.log.*",
        "*.out",
        # Configuration files
        ".env",
        ".env.*",
        "*.env",
        "*.env.*",
        "*.ini",
        "*.toml",
        "*.conf",
        "*.theme",
        ".gitignore",
        ".gitconfig",
        ".editorconfig",
        # Package manager files
        "package-lock.json",
        "yarn.lock",
        "pnpm-lock.yaml",
        "composer.lock",
        "poetry.lock",
        "Cargo.lock",
        # Build/compile artifacts
        "*.pyc",
        "*.pyo",
        "*.pyd",
        "*.class",
        "*.o",
        "*.so",
        "*.dll",
        "*.exe",
        "*.dylib",
        "*.a",
        # Cache files
        ".DS_Store",
        "Thumbs.db",
        "desktop.ini",
        # Backup files
        "*.bak",
        "*.swp",
        "*.swo",
        # Coverage reports
        "coverage/",
        ".coverage",
        # Other hidden files
        ".bashrc",
        ".zshrc",
        ".profile",
        ".vimrc",
        ".eslintrc",
        ".prettierrc",
    }

    return include_dirs, include_files


def should_exclude_path(path: Union[str, Path], exclude_patterns: Set[str]) -> bool:
    """
    Check if a path should be excluded based on exclude patterns.
    Returns True if the path matches any exclude pattern.
    """
    path_str = str(path)
    path_obj = Path(path)
    
    # Check if any part of the path matches our exclude patterns
    for pattern in exclude_patterns:
        # Check if pattern is in the full path
        if pattern in path_str:
            return True
        # Check if pattern matches any part of the path
        for part in path_obj.parts:
            if part == pattern:
                return True
    return False


def should_include_path(path: Union[str, Path], include_dirs: Set[str]) -> bool:
    """
    Check if a path should be included based on directory patterns.
    Returns True if any part of the path matches an include pattern.
    """
    path_parts = Path(path).parts
    # Check if any part of the path matches our include patterns
    for part in path_parts:
        if part.lower() in include_dirs:
            return True
    return False


def should_include_file(filename: str, include_files: Set[str]) -> bool:
    """
    Check if a file should be included based on file patterns.
    """
    filename_lower = filename.lower()
    
    for pattern in include_files:
        pattern_lower = pattern.lower()
        
        # Exact match
        if filename_lower == pattern_lower:
            return True
            
        # Extension match (patterns starting with *.)
        if pattern.startswith("*.") and filename_lower.endswith(pattern[1:].lower()):
            return True
            
        # Prefix match (patterns ending with / for directories)
        if pattern.endswith("/") and filename_lower.startswith(pattern[:-1].lower()):
            return True
            
    return False


def is_hidden_file_or_dir(path: Union[str, Path]) -> bool:
    """
    Check if a file or directory is hidden (starts with a dot).
    """
    path_obj = Path(path)
    # Check if any part of the path is hidden
    for part in path_obj.parts:
        if part.startswith('.'):
            return True
    return False
