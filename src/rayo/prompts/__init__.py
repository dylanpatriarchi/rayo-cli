"""
Prompts package for Rayo CLI.

This package contains system prompts and prompt management utilities.
"""

from pathlib import Path
from typing import Optional


def load_system_prompt(custom_prompt_path: Optional[str] = None) -> str:
    """
    Load the system prompt from a file.

    Args:
        custom_prompt_path: Optional path to a custom prompt file.
                          If not provided, uses the default system prompt.

    Returns:
        The system prompt as a string.

    Raises:
        FileNotFoundError: If the prompt file doesn't exist.
        IOError: If the prompt file cannot be read.
    """
    if custom_prompt_path:
        prompt_path = Path(custom_prompt_path)
    else:
        # Default system prompt
        prompt_path = Path(__file__).parent / "system_prompt.md"

    if not prompt_path.exists():
        raise FileNotFoundError(f"Prompt file not found: {prompt_path}")

    try:
        with open(prompt_path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        raise IOError(f"Failed to load prompt: {e}") from e


__all__ = ["load_system_prompt"]
