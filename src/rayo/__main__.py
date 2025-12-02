"""
Entry point for running Rayo CLI as a module.

This allows users to run: python -m rayo
"""

from rayo.cli import app

if __name__ == "__main__":
    app()
