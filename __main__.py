"""
Main entry point for HiddenFileReader application.
"""

import sys
from .cli import main as cli_main
from .gui import main as gui_main


def main():
    if len(sys.argv) > 1:
        # CLI mode
        cli_main()
    else:
        # GUI mode
        gui_main()


if __name__ == "__main__":
    main()