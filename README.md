# HiddenFileReader 🕵️‍♂️

A tool to analyze and dump hidden files and directories that are typically excluded in code repositories.

## Features ✨

- Detects and reads hidden files and directories (e.g., `.env`, `.git`, `dist`, `build`, etc.)
- Focuses on files that are usually ignored by tools like ProjectDump
- Generates comprehensive reports with directory structure and file contents
- Supports both command-line and GUI interfaces
- Handles large files gracefully with size limits
- Works with various file types including logs, configuration files, and build artifacts
- **Smart exclude patterns** to skip system directories and common large directories
- **Multiple output formats**: TXT, Markdown, JSON, and SQLite
- **File filtering options**: `--dotfiles`, `--config`, `--all`
- **File size filtering** with `--max-size` option
- **Binary file detection** to skip non-text files
- **Safety features**: Root filesystem warning and `--dry-run` option
- **Enhanced GUI** with better statistics display

## Installation 📦

```bash
pip install -e .
```

## Usage 🚀

### Command Line Interface

```bash
# Analyze current directory
hiddenfilereader

# Analyze specific directory
hiddenfilereader /path/to/project

# With language selection
hiddenfilereader --lang vi /path/to/project

# With exclude patterns
hiddenfilereader --exclude node_modules --exclude .cache

# Dry run to see what files would be processed
hiddenfilereader --dry-run

# Different output formats
hiddenfilereader --format md    # Markdown
hiddenfilereader --format json  # JSON
hiddenfilereader --format sqlite # SQLite

# File filtering
hiddenfilereader --filter dotfiles  # Only dotfiles
hiddenfilereader --filter config    # Only config files

# Max file size
hiddenfilereader --max-size 50M  # Skip files larger than 50MB
```

### GUI Interface

```bash
# Run the GUI version
python -m HiddenFileReader
```

## File Types Included 📁

- Log files: `*.log`, `*.out`
- Configuration files: `.env`, `*.ini`, `*.toml`, `*.conf`, `*.theme`, `.gitignore`
- Build directories: `dist`, `build`, `target`
- Hidden directories: `.git`, `.vscode`, `.idea`
- Dependency lock files: `package-lock.json`, `yarn.lock`
- Cache files: `*.pyc`, `.DS_Store`
- And many more hidden or build-related files

## Output Formats 📤

The tool can generate output in multiple formats:

1. **Text (.txt)** - Default format with directory structure and file contents
2. **Markdown (.md)** - Same as text but with Markdown syntax highlighting
3. **JSON (.json)** - Key-value pairs with filename as key and content as value (ideal for AI/LLM processing)
4. **SQLite (.db)** - Database with each file as a row (easy SQL querying)

## Safety Features 🛡️

- Automatically skips system directories (`/proc`, `/sys`, `/dev`)
- Skips common large directories (`node_modules`, `.git`, `__pycache__`, etc.)
- Warns when scanning root filesystem (`/`)
- `--dry-run` option to preview files without reading content
- Binary file detection to skip non-text files
- Configurable maximum file size limits

## License 📄

MIT