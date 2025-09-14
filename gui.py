"""
GUI version of HiddenFileReader using tkinter.
"""

import os
import sys
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from .aggregator import aggregate_hidden_files
from .constants import TEXT_VI, TEXT_EN, MAX_FILE_SIZE
from .filters import DEFAULT_EXCLUDE_PATTERNS
import io
import contextlib
import subprocess
import platform


class HiddenFileReaderGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("🔍 HiddenFileReader")
        self.root.geometry("900x700")

        self.output_path = None  # Save output path for opening

        # Language selection
        tk.Label(root, text="🌐 Language:").grid(row=0, column=0, padx=10, pady=5, sticky="w")
        self.lang_var = tk.StringVar(value="en")
        lang_menu = ttk.Combobox(root, textvariable=self.lang_var, values=["en", "vi"], state="readonly", width=10)
        lang_menu.grid(row=0, column=1, padx=10, pady=5, sticky="w")

        # Project path selection
        tk.Label(root, text="📂 Project Directory:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.path_var = tk.StringVar()
        self.path_entry = tk.Entry(root, textvariable=self.path_var, width=50)
        self.path_entry.grid(row=1, column=1, padx=10, pady=5)
        tk.Button(root, text="Browse", command=self.choose_folder).grid(row=1, column=2, padx=5, pady=5)

        # Output format selection
        tk.Label(root, text="📄 Output Format:").grid(row=2, column=0, padx=10, pady=5, sticky="w")
        self.format_var = tk.StringVar(value="txt")
        format_menu = ttk.Combobox(root, textvariable=self.format_var, values=["txt", "md", "json", "sqlite"], state="readonly", width=10)
        format_menu.grid(row=2, column=1, padx=10, pady=5, sticky="w")

        # File filter selection
        tk.Label(root, text="🔍 File Filter:").grid(row=3, column=0, padx=10, pady=5, sticky="w")
        self.filter_var = tk.StringVar(value="all")
        filter_menu = ttk.Combobox(root, textvariable=self.filter_var, values=["all", "dotfiles", "config"], state="readonly", width=10)
        filter_menu.grid(row=3, column=1, padx=10, pady=5, sticky="w")

        # Max file size entry
        tk.Label(root, text="📏 Max File Size (MB):").grid(row=4, column=0, padx=10, pady=5, sticky="w")
        self.max_size_var = tk.StringVar(value=str(MAX_FILE_SIZE // (1024 * 1024)))  # Convert to MB
        max_size_entry = tk.Entry(root, textvariable=self.max_size_var, width=10)
        max_size_entry.grid(row=4, column=1, padx=10, pady=5, sticky="w")

        # Additional exclude patterns
        tk.Label(root, text="🚫 Exclude Patterns:").grid(row=5, column=0, padx=10, pady=5, sticky="w")
        self.exclude_var = tk.StringVar()
        exclude_entry = tk.Entry(root, textvariable=self.exclude_var, width=50)
        exclude_entry.grid(row=5, column=1, padx=10, pady=5)
        tk.Label(root, text="(comma-separated)").grid(row=5, column=2, padx=5, pady=5, sticky="w")

        # Dry run checkbox
        self.dry_run_var = tk.BooleanVar()
        dry_run_check = tk.Checkbutton(root, text="🔍 Dry Run (list files only)", variable=self.dry_run_var)
        dry_run_check.grid(row=6, column=0, columnspan=2, padx=10, pady=5, sticky="w")

        # Run + Open buttons
        tk.Button(root, text="▶️ Run HiddenFileReader", command=self.run_hiddenfilereader).grid(
            row=7, column=0, pady=10, padx=10, sticky="w"
        )

        self.open_btn = tk.Button(root, text="📂 Open Output Folder", command=self.open_output_folder, state="disabled")
        self.open_btn.grid(row=7, column=1, pady=10, sticky="w")

        # Log output area
        tk.Label(root, text="📜 Log output:").grid(row=8, column=0, padx=10, pady=5, sticky="nw")
        self.log_text = tk.Text(root, wrap="word", height=20)
        self.log_text.grid(row=8, column=1, columnspan=2, padx=10, pady=5, sticky="nsew")

        # Scrollbar for log
        scrollbar = tk.Scrollbar(root, command=self.log_text.yview)
        scrollbar.grid(row=8, column=3, sticky="nsew")
        self.log_text.config(yscrollcommand=scrollbar.set)

        # Allow layout stretching
        root.grid_rowconfigure(8, weight=1)
        root.grid_columnconfigure(1, weight=1)

    def choose_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.path_var.set(folder)

    def run_hiddenfilereader(self):
        project_path = self.path_var.get().strip() or os.getcwd()
        lang = self.lang_var.get().lower()
        output_format = self.format_var.get()
        file_filter = self.filter_var.get()
        dry_run = self.dry_run_var.get()
        
        text = TEXT_EN if lang == "en" else TEXT_VI
        project_path = os.path.abspath(project_path)

        # Handle max file size
        try:
            max_size_mb = int(self.max_size_var.get())
            max_file_size = max_size_mb * 1024 * 1024
        except ValueError:
            max_file_size = MAX_FILE_SIZE
            self.max_size_var.set(str(MAX_FILE_SIZE // (1024 * 1024)))

        # Handle exclude patterns
        exclude_patterns = DEFAULT_EXCLUDE_PATTERNS.copy()
        if self.exclude_var.get().strip():
            additional_patterns = [p.strip() for p in self.exclude_var.get().split(",")]
            exclude_patterns.update(additional_patterns)

        # Safety check for root filesystem
        if project_path == "/":
            response = messagebox.askyesno(
                "⚠️ Warning", 
                "You are about to scan the entire root filesystem. This may take a very long time and consume significant resources. Continue?"
            )
            if not response:
                self.log_text.insert(tk.END, "❌ Scan cancelled by user.\n")
                self.log_text.see(tk.END)
                return

        # Reset state
        self.open_btn.config(state="disabled")
        self.output_path = None

        # Redirect stdout/stderr to log box
        log_buffer = io.StringIO()
        with contextlib.redirect_stdout(log_buffer), contextlib.redirect_stderr(log_buffer):
            success = aggregate_hidden_files(
                project_path, 
                text, 
                exclude_patterns, 
                dry_run,
                output_format,
                max_file_size,
                file_filter
            )

        # Print log to Text widget
        self.log_text.insert(tk.END, log_buffer.getvalue() + "\n")
        self.log_text.see(tk.END)  # Scroll to end

        if success and not dry_run:
            # Determine output file path based on format
            base_path = os.path.join(project_path, "hidden_dump")
            if output_format == "json":
                self.output_path = base_path + ".json"
            elif output_format == "sqlite":
                self.output_path = base_path + ".db"
            elif output_format == "md":
                self.output_path = base_path + ".md"
            else:  # txt format
                self.output_path = base_path + ".txt"
                
            self.open_btn.config(state="normal")  # Enable open button
            messagebox.showinfo("✅ Success", text["done"])
        elif not success:
            messagebox.showerror("❌ Error", text["error"])

    def open_output_folder(self):
        if self.output_path and os.path.exists(self.output_path):
            folder = os.path.dirname(self.output_path)
            if platform.system() == "Windows":
                os.startfile(folder)
            elif platform.system() == "Darwin":  # macOS
                subprocess.run(["open", folder])
            else:  # Linux
                subprocess.run(["xdg-open", folder])
        else:
            messagebox.showwarning("⚠️", "Output file not found!")


def main():
    root = tk.Tk()
    app = HiddenFileReaderGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()