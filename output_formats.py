"""
Module for handling different output formats for HiddenFileReader.
"""

import os
import json
import sqlite3
from typing import Dict, List, Tuple
from pathlib import Path


def write_markdown_output(content_lines: List[str], output_path: str) -> str:
    """Write content in Markdown format with syntax highlighting."""
    md_path = output_path.replace(".txt", ".md")
    with open(md_path, "w", encoding="utf-8") as f:
        f.write("\n".join(content_lines))
    return md_path


def write_json_output(file_contents: Dict[str, str], output_path: str) -> str:
    """Write content in JSON format (key = filename, value = content)."""
    json_path = output_path.replace(".txt", ".json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(file_contents, f, indent=2, ensure_ascii=False)
    return json_path


def write_sqlite_output(file_contents: Dict[str, str], output_path: str) -> str:
    """Write content in SQLite format (each file as a row)."""
    sqlite_path = output_path.replace(".txt", ".db")
    
    # Remove existing database file if it exists
    if os.path.exists(sqlite_path):
        os.remove(sqlite_path)
    
    conn = sqlite3.connect(sqlite_path)
    cursor = conn.cursor()
    
    # Create table
    cursor.execute("""
        CREATE TABLE files (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filepath TEXT NOT NULL,
            content TEXT NOT NULL
        )
    """)
    
    # Insert file contents
    for filepath, content in file_contents.items():
        cursor.execute(
            "INSERT INTO files (filepath, content) VALUES (?, ?)",
            (filepath, content)
        )
    
    conn.commit()
    conn.close()
    return sqlite_path