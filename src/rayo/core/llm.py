"""
LLM client wrapper for Rayo CLI.

This module provides a wrapper around LiteLLM for making
LLM API calls with proper configuration and error handling.
"""

from typing import Any, Dict, List, Optional

import litellm
from litellm import completion

from rayo.config import RayoConfig


class LLMClient:
    """
    Client for interacting with LLM providers via LiteLLM.

    This class handles API key configuration and provides a clean
    interface for making completion requests.
    """

    def __init__(self, config: RayoConfig):
        """
        Initialize the LLM client.

        Args:
            config: RayoConfig instance with API keys and model settings.
        """
        self.config = config
        self._configure_api_keys()

    def _configure_api_keys(self) -> None:
        """Configure API keys for LiteLLM."""
        import os

        for provider, key in self.config.api_keys.items():
            # Set environment variables for LiteLLM
            if provider == "openai":
                os.environ["OPENAI_API_KEY"] = key
            elif provider == "anthropic":
                os.environ["ANTHROPIC_API_KEY"] = key
            elif provider == "cohere":
                os.environ["COHERE_API_KEY"] = key
            elif provider == "azure":
                os.environ["AZURE_API_KEY"] = key

    def complete(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
    ) -> str:
        """
        Make a completion request to the LLM.

        Args:
            messages: List of message dictionaries with 'role' and 'content'.
            model: Model to use (defaults to config.default_model).
            max_tokens: Maximum tokens (defaults to config.max_tokens).
            temperature: Temperature setting (defaults to config.temperature).

        Returns:
            The LLM's response content as a string.

        Raises:
            Exception: If the API call fails.
        """
        model = model or self.config.default_model
        max_tokens = max_tokens or self.config.max_tokens
        temperature = temperature or self.config.temperature

        try:
            response = completion(
                model=model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
            )

            # Extract content from response
            if hasattr(response, "choices") and len(response.choices) > 0:
                return response.choices[0].message.content or ""

            return ""

        except Exception as e:
            raise Exception(f"LLM API call failed: {e}") from e
