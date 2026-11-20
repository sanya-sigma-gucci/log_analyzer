#!/usr/bin/env python3
"""Entry point wrapper for the log analyzer CLI."""
import sys

from log_analyzer.cli import main

if __name__ == "__main__":
    sys.exit(main())