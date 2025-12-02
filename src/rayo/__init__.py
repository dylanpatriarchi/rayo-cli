"""
Rayo CLI - A professional AI coding assistant for the terminal.

This package provides an intelligent coding assistant that can read files,
modify code, execute shell commands, and more, all with human-in-the-loop
safety confirmations.
"""

__version__ = "0.1.0"
__author__ = "Rayo Contributors"

from rayo.cli import app

__all__ = ["app", "__version__"]
