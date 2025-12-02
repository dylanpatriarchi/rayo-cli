"""
System tools for Rayo CLI.

This module provides tools for executing shell commands and
interacting with the operating system.
"""

import subprocess
from typing import Any, Dict

from rayo.tools.base import Tool, ToolError


class RunBashTool(Tool):
    """
    Tool for executing shell commands.

    Runs commands using subprocess and captures stdout/stderr.
    This tool requires user confirmation before execution.
    """

    @property
    def name(self) -> str:
        return "run_bash"

    @property
    def description(self) -> str:
        return (
            "Execute a shell command and return the output. "
            "Captures both stdout and stderr. Requires user confirmation."
        )

    def execute(self, command: str, timeout: int = 30) -> Dict[str, Any]:
        """
        Execute a shell command.

        Args:
            command: The shell command to execute.
            timeout: Maximum execution time in seconds (default: 30).

        Returns:
            Dictionary with success status, stdout, stderr, and return code.

        Raises:
            ToolError: If the command execution fails or times out.
        """
        if not command or not command.strip():
            raise ToolError("Command cannot be empty")

        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout,
            )

            return {
                "success": result.returncode == 0,
                "output": result.stdout,
                "error": result.stderr,
                "return_code": result.returncode,
                "command": command,
            }

        except subprocess.TimeoutExpired:
            raise ToolError(
                f"Command timed out after {timeout} seconds: {command}"
            )
        except Exception as e:
            raise ToolError(f"Failed to execute command: {e}") from e
