"""
Configuration management for Rayo CLI.

This module handles loading, saving, and managing user configuration
using Pydantic models for validation and type safety.
"""

import json
from pathlib import Path
from typing import Dict, Optional

from pydantic import BaseModel, Field, field_validator
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt

console = Console()


class RayoConfig(BaseModel):
    """
    Configuration model for Rayo CLI.

    Attributes:
        api_keys: Dictionary mapping provider names to API keys.
        default_model: The default LLM model to use (e.g., "gpt-4", "claude-3-opus").
        max_tokens: Maximum number of tokens for LLM responses.
        temperature: Temperature setting for LLM (0.0 to 2.0).
    """

    api_keys: Dict[str, str] = Field(default_factory=dict)
    default_model: str = Field(default="gpt-4")
    max_tokens: int = Field(default=4096, ge=1, le=128000)
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    custom_prompt_path: Optional[str] = Field(default=None)

    @field_validator("default_model")
    @classmethod
    def validate_model_name(cls, v: str) -> str:
        """Validate that model name is not empty."""
        if not v or not v.strip():
            raise ValueError("Model name cannot be empty")
        return v.strip()


def get_config_path() -> Path:
    """
    Get the path to the Rayo configuration file.

    Returns:
        Path object pointing to ~/.rayo/config.json
    """
    config_dir = Path.home() / ".rayo"
    config_dir.mkdir(exist_ok=True)
    return config_dir / "config.json"


def load_config() -> RayoConfig:
    """
    Load configuration from disk.

    If the configuration file doesn't exist, returns a default configuration.

    Returns:
        RayoConfig instance with loaded or default settings.

    Raises:
        ValueError: If the configuration file is malformed.
    """
    config_path = get_config_path()

    if not config_path.exists():
        console.print(
            "[yellow]No configuration found. Using defaults.[/yellow]",
            style="dim",
        )
        return RayoConfig()

    try:
        with open(config_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return RayoConfig(**data)
    except json.JSONDecodeError as e:
        raise ValueError(f"Configuration file is malformed: {e}") from e
    except Exception as e:
        raise ValueError(f"Failed to load configuration: {e}") from e


def save_config(config: RayoConfig) -> None:
    """
    Save configuration to disk.

    Args:
        config: RayoConfig instance to save.

    Raises:
        IOError: If unable to write configuration file.
    """
    config_path = get_config_path()

    try:
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(config.model_dump(), f, indent=2)
        console.print(
            f"[green]✓[/green] Configuration saved to {config_path}",
            style="dim",
        )
    except Exception as e:
        raise IOError(f"Failed to save configuration: {e}") from e


def setup_wizard() -> RayoConfig:
    """
    Interactive setup wizard for configuring Rayo CLI.

    Prompts the user for API keys and preferences using Rich prompts.
    Sensitive inputs (API keys) are masked.

    Returns:
        RayoConfig instance with user-provided settings.
    """
    console.print(
        Panel.fit(
            "[bold cyan]Rayo CLI Setup Wizard[/bold cyan]\n\n"
            "Let's configure your AI coding assistant!",
            border_style="cyan",
        )
    )

    # Load existing config if available
    try:
        existing_config = load_config()
    except ValueError:
        existing_config = RayoConfig()

    # API Key Configuration
    console.print("\n[bold]API Key Configuration[/bold]")
    console.print(
        "Rayo supports multiple LLM providers. Enter your API key(s) below.\n"
        "Leave blank to skip a provider.\n",
        style="dim",
    )

    providers = ["openai", "anthropic", "cohere", "azure"]
    api_keys: Dict[str, str] = {}

    for provider in providers:
        existing_key = existing_config.api_keys.get(provider, "")
        prompt_text = f"{provider.capitalize()} API Key"

        if existing_key:
            prompt_text += " [dim](already configured)[/dim]"

        key = Prompt.ask(
            prompt_text,
            password=True,
            default="" if not existing_key else "***EXISTING***",
        )

        # Keep existing key if user entered the placeholder
        if key and key != "***EXISTING***":
            api_keys[provider] = key
        elif existing_key and key == "***EXISTING***":
            api_keys[provider] = existing_key

    if not api_keys:
        console.print(
            "[yellow]⚠[/yellow] No API keys configured. "
            "You'll need to add them later to use Rayo.",
            style="dim",
        )

    # Model Configuration
    console.print("\n[bold]Model Configuration[/bold]")

    default_model = Prompt.ask(
        "Default model",
        default=existing_config.default_model,
    )

    max_tokens_str = Prompt.ask(
        "Max tokens",
        default=str(existing_config.max_tokens),
    )

    temperature_str = Prompt.ask(
        "Temperature (0.0-2.0)",
        default=str(existing_config.temperature),
    )

    # Create and validate config
    try:
        config = RayoConfig(
            api_keys=api_keys,
            default_model=default_model,
            max_tokens=int(max_tokens_str),
            temperature=float(temperature_str),
        )
    except ValueError as e:
        console.print(f"[red]✗[/red] Invalid configuration: {e}")
        console.print("Using default values for invalid fields.", style="dim")
        config = RayoConfig(api_keys=api_keys)

    # Save configuration
    save_config(config)

    console.print(
        "\n[bold green]✓ Setup complete![/bold green]\n"
        "You can now run [cyan]rayo start[/cyan] to begin coding with AI assistance.\n",
    )

    return config
