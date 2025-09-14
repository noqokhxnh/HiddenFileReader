"""
HiddenFileReader - One file version
A tool to analyze and dump hidden files and directories that are typically excluded in code repositories.
"""

import os
import sys
import argparse
from pathlib import Path
from typing import Set, Tuple, Union, List, Dict


# Constants
MAX_FILE_SIZE = 100 * 1024 * 1024  # 100 MB

TEXT_VI = {
    "app_title": "🔍 HIDDENFILEREADER",
    "input_project_path": "📂 Nhập đường dẫn thư mục dự án: ",
    "done": "\n🎉 Hoàn thành! File hidden_dump.txt đã sẵn sàng.",
    "error": "\n💥 Có lỗi xảy ra trong quá trình xử lý.",
    "analyzing": "🔍 Đang phân tích dự án tại: ",
    "scanning": "🔍 Đang quét thư mục...",
    "included_types": "📁 Các loại tệp sẽ được bao gồm: ",
    "generating_tree": "📁 Đang tạo cây thư mục...",
    "processing_files": "📄 Đang xử lý các tệp ẩn...",
    "skip_large": "⚠️  Bỏ qua {file} (kích thước {size} byte > giới hạn {limit} byte)",
    "processing": "  📝 Xử lý: {file}",
    "success": "✅ Thành công! Đã tạo file: ",
    "summary": "📊 Thống kê:",
    "file_count": "   - Số file đã xử lý: {count}",
    "size": "   - Kích thước file đầu ra: {size} ký tự (~{kb} KB)",
    "line_count": "   - Tổng số dòng: {lines}",
    "write_error": "❌ Lỗi ghi file: {error}",
    "not_found": "❌ Lỗi: Thư mục '{path}' không tồn tại!",
}

TEXT_EN = {
    "app_title": "🔍 HIDDENFILEREADER",
    "input_project_path": "📂 Enter the project folder path: ",
    "done": "\n🎉 Done! The hidden_dump.txt file is ready.",
    "error": "\n💥 An error occurred during processing.",
    "analyzing": "🔍 Analyzing project at: ",
    "scanning": "🔍 Scanning directories...",
    "included_types": "📁 File types included: ",
    "generating_tree": "📁 Generating directory tree...",
    "processing_files": "📄 Processing hidden files...",
    "skip_large": "⚠️  Skipping {file} (size {size} bytes > limit {limit} bytes)",
    "processing": "  📝 Processing: {file}",
    "success": "✅ Success! File created: ",
    "summary": "📊 Summary:",
    "file_count": "   - Files processed: {count}",
    "size": "   - Output size: {size} characters (~{kb} KB)",
    "line_count": "   - Total lines: {lines}",
    "write_error": "❌ Error writing file: {error}",
    "not_found": "❌ Error: Folder '{path}' not found!",
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


def aggregate_hidden_files(project_path: str, text: Dict[str, str]) -> bool:
    """Main function to aggregate hidden files and directories"""
    if not os.path.isdir(project_path):
        print(text["not_found"].format(path=project_path))
        return False

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

    for root, dirs, files in os.walk(project_path):
        # Filter directories to only traverse those that might contain hidden files
        dirs[:] = [
            d
            for d in dirs
            if should_include_path(os.path.join(root, d), include_dirs) or 
               is_hidden_file_or_dir(os.path.join(root, d))
        ]

        for file in files:
            file_path = os.path.join(root, file)
            rel_path = os.path.relpath(file_path, project_path)

            # Include file if it matches our patterns or is hidden
            if not (should_include_file(file, include_files) or is_hidden_file_or_dir(file_path)):
                continue

            try:
                file_size = os.path.getsize(file_path)
                if file_size > MAX_FILE_SIZE:
                    print(
                        text["skip_large"].format(
                            file=rel_path, size=file_size, limit=MAX_FILE_SIZE
                        )
                    )
                    continue

                print(text["processing"].format(file=rel_path))
                with open(
                    file_path, "r", encoding="utf-8", errors="ignore"
                ) as f:
                    file_content = f.read()

                content_lines.append(f"### {rel_path}")
                content_lines.append("```")
                content_lines.append(file_content)
                content_lines.append("```")
                content_lines.append("")

                file_count += 1
                total_size += len(file_content)

            except Exception as e:
                content_lines.append(f"### {rel_path}")
                content_lines.append(
                    f"```\n# Error reading file: {str(e)}\n```"
                )
                content_lines.append("")

    output_path = os.path.join(project_path, "hidden_dump.txt")
    final_content = "\n".join(content_lines)

    try:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(final_content)

        with open(output_path, "r", encoding="utf-8") as f:
            line_count = sum(1 for _ in f)

        print("")
        print(text["success"] + output_path)
        print("")
        print(text["summary"])
        print(text["file_count"].format(count=file_count))
        print(
            text["size"].format(size=len(final_content), kb=total_size // 1024)
        )
        print(text["line_count"].format(lines=line_count))
        return True

    except Exception as e:
        print(text["write_error"].format(error=str(e)))
        return False


def main():
    parser = argparse.ArgumentParser(description="HiddenFileReader - Analyze hidden files and directories")
    parser.add_argument("path", nargs="?", default=".", help="Project path to analyze (default: current directory)")
    parser.add_argument("--lang", choices=["en", "vi"], default="en", help="Language for output messages")
    
    args = parser.parse_args()
    
    project_path = os.path.abspath(args.path)
    text = TEXT_EN if args.lang == "en" else TEXT_VI
    
    print(text["app_title"])
    print("=" * 50)
    
    success = aggregate_hidden_files(project_path, text)
    
    if success:
        print(text["done"])
    else:
        print(text["error"])
        sys.exit(1)


if __name__ == "__main__":
    main()