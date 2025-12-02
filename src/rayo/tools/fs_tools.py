"""
File system tools for Rayo CLI.

This module provides tools for interacting with the file system:
- Listing files in a directory
- Reading file contents
- Applying patches to files with verification
"""

import os
from pathlib import Path
from typing import Any, Dict, List, Set

from rayo.tools.base import Tool, ToolError


class ListFilesTool(Tool):
    """
    Tool for listing files in a directory.

    Returns a tree structure of files and directories, ignoring common
    directories like .git, __pycache__, .venv, node_modules, etc.
    """

    # Directories to ignore when listing files
    IGNORE_DIRS: Set[str] = {
        ".git",
        "__pycache__",
        ".venv",
        "venv",
        "node_modules",
        ".pytest_cache",
        ".mypy_cache",
        ".ruff_cache",
        "dist",
        "build",
        "*.egg-info",
    }

    @property
    def name(self) -> str:
        return "list_files"

    @property
    def description(self) -> str:
        return (
            "List files and directories in a given path. "
            "Returns a tree structure. Ignores common build/cache directories."
        )

    def execute(self, path: str = ".") -> Dict[str, Any]:
        """
        List files in the specified directory.

        Args:
            path: Directory path to list (default: current directory).

        Returns:
            Dictionary with success status and tree output.

        Raises:
            ToolError: If the path doesn't exist or isn't accessible.
        """
        target_path = Path(path).resolve()

        if not target_path.exists():
            raise ToolError(f"Path does not exist: {path}")

        if not target_path.is_dir():
            raise ToolError(f"Path is not a directory: {path}")

        try:
            tree = self._build_tree(target_path)
            return {
                "success": True,
                "output": tree,
                "path": str(target_path),
            }
        except Exception as e:
            raise ToolError(f"Failed to list files: {e}") from e

    def _build_tree(self, path: Path, prefix: str = "", max_depth: int = 5) -> str:
        """
        Build a tree structure representation of the directory.

        Args:
            path: Path to build tree for.
            prefix: Prefix for tree formatting.
            max_depth: Maximum depth to traverse.

        Returns:
            String representation of the directory tree.
        """
        if max_depth <= 0:
            return f"{prefix}[...]\n"

        lines: List[str] = []

        try:
            items = sorted(path.iterdir(), key=lambda x: (not x.is_dir(), x.name))
        except PermissionError:
            return f"{prefix}[Permission Denied]\n"

        for i, item in enumerate(items):
            # Skip ignored directories
            if item.name in self.IGNORE_DIRS or item.name.startswith("."):
                continue

            is_last = i == len(items) - 1
            current_prefix = "└── " if is_last else "├── "
            next_prefix = "    " if is_last else "│   "

            if item.is_dir():
                lines.append(f"{prefix}{current_prefix}{item.name}/\n")
                lines.append(
                    self._build_tree(item, prefix + next_prefix, max_depth - 1)
                )
            else:
                # Show file size
                try:
                    size = item.stat().st_size
                    size_str = self._format_size(size)
                    lines.append(f"{prefix}{current_prefix}{item.name} ({size_str})\n")
                except Exception:
                    lines.append(f"{prefix}{current_prefix}{item.name}\n")

        return "".join(lines)

    @staticmethod
    def _format_size(size: int) -> str:
        """Format file size in human-readable format."""
        for unit in ["B", "KB", "MB", "GB"]:
            if size < 1024.0:
                return f"{size:.1f}{unit}"
            size /= 1024.0
        return f"{size:.1f}TB"


class ReadFileTool(Tool):
    """
    Tool for reading file contents.

    Returns the file content with line numbers for easy reference.
    """

    @property
    def name(self) -> str:
        return "read_file"

    @property
    def description(self) -> str:
        return "Read the contents of a file. Returns content with line numbers."

    def execute(self, path: str) -> Dict[str, Any]:
        """
        Read the specified file.

        Args:
            path: Path to the file to read.

        Returns:
            Dictionary with success status and file content.

        Raises:
            ToolError: If the file doesn't exist or can't be read.
        """
        file_path = Path(path).resolve()

        if not file_path.exists():
            raise ToolError(f"File does not exist: {path}")

        if not file_path.is_file():
            raise ToolError(f"Path is not a file: {path}")

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Add line numbers
            lines = content.split("\n")
            numbered_lines = [
                f"{i+1:4d} | {line}" for i, line in enumerate(lines)
            ]
            numbered_content = "\n".join(numbered_lines)

            return {
                "success": True,
                "output": numbered_content,
                "path": str(file_path),
                "lines": len(lines),
            }
        except UnicodeDecodeError:
            raise ToolError(f"File is not a text file or uses unsupported encoding: {path}")
        except Exception as e:
            raise ToolError(f"Failed to read file: {e}") from e


class ApplyPatchTool(Tool):
    """
    Tool for applying patches to files.

    This tool performs a search-and-replace operation with verification.
    It ensures the original snippet exists uniquely in the file before
    replacing it with the new content.
    """

    @property
    def name(self) -> str:
        return "apply_patch"

    @property
    def description(self) -> str:
        return (
            "Apply a patch to a file by replacing an original snippet with new content. "
            "Verifies the original snippet exists uniquely before applying the change."
        )

    def execute(
        self,
        path: str,
        original_snippet: str,
        new_snippet: str,
    ) -> Dict[str, Any]:
        """
        Apply a patch to the specified file.

        Args:
            path: Path to the file to patch.
            original_snippet: The exact text to find and replace.
            new_snippet: The new text to insert.

        Returns:
            Dictionary with success status and details about the change.

        Raises:
            ToolError: If the file doesn't exist, snippet not found, or found multiple times.
        """
        file_path = Path(path).resolve()

        if not file_path.exists():
            raise ToolError(f"File does not exist: {path}")

        if not file_path.is_file():
            raise ToolError(f"Path is not a file: {path}")

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
        except Exception as e:
            raise ToolError(f"Failed to read file: {e}") from e

        # Verify the original snippet exists
        count = content.count(original_snippet)

        if count == 0:
            raise ToolError(
                f"Original snippet not found in {path}. "
                "Please verify the exact text to replace."
            )

        if count > 1:
            raise ToolError(
                f"Original snippet found {count} times in {path}. "
                "Please provide a more specific snippet that appears only once."
            )

        # Apply the patch
        new_content = content.replace(original_snippet, new_snippet, 1)

        # This will be written only after user confirmation in the agent
        return {
            "success": True,
            "output": "Patch prepared (awaiting confirmation)",
            "path": str(file_path),
            "original": original_snippet,
            "new": new_snippet,
            "new_content": new_content,  # Agent will write this after confirmation
        }

    @staticmethod
    def write_file(path: str, content: str) -> None:
        """
        Write content to a file.

        This is called by the agent after user confirmation.

        Args:
            path: Path to the file.
            content: Content to write.

        Raises:
            ToolError: If writing fails.
        """
        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)
        except Exception as e:
            raise ToolError(f"Failed to write file: {e}") from e
