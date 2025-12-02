"""
Base classes and interfaces for Rayo tools.

This module defines the abstract base class that all tools must implement,
as well as custom exceptions for tool-specific errors.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict


class ToolError(Exception):
    """
    Custom exception for tool-specific errors.

    This exception is raised when a tool encounters an error during execution.
    The agent can catch this exception and provide feedback to the LLM for
    self-correction.
    """

    pass


class Tool(ABC):
    """
    Abstract base class for all Rayo tools.

    Each tool must implement the execute method and provide a name and description.
    Tools are the primary way the agent interacts with the system (files, shell, etc.).
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """
        Get the tool's name.

        Returns:
            A unique identifier for this tool (e.g., "read_file", "run_bash").
        """
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """
        Get the tool's description.

        Returns:
            A human-readable description of what this tool does.
        """
        pass

    @abstractmethod
    def execute(self, **kwargs: Any) -> Dict[str, Any]:
        """
        Execute the tool with the given parameters.

        Args:
            **kwargs: Tool-specific parameters.

        Returns:
            A dictionary containing the tool's output. Should include at minimum:
            - "success": bool indicating if the operation succeeded
            - "output": str with the result or error message

        Raises:
            ToolError: If the tool encounters an error during execution.
        """
        pass

    def to_schema(self) -> Dict[str, Any]:
        """
        Convert the tool to a JSON schema for LLM function calling.

        Returns:
            A dictionary representing the tool's schema.
        """
        return {
            "name": self.name,
            "description": self.description,
        }
