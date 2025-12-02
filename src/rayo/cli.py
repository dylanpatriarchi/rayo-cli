"""
CLI interface for Rayo using Typer.

This module defines the command-line interface for Rayo CLI,
including commands for starting the agent and configuring settings.
"""

import sys

import typer
from rich.console import Console

from rayo.config import load_config, setup_wizard
from rayo.core.agent import RayoAgent

app = typer.Typer(
    name="rayo",
    help="A professional AI coding assistant for the terminal",
    add_completion=False,
)

console = Console()


@app.command()
def start() -> None:
    """
    Start the Rayo AI coding assistant.

    Launches an interactive session where you can chat with the AI
    and have it help with coding tasks like reading files, modifying
    code, and running commands.
    """
    try:
        # Load configuration
        config = load_config()

        # Check if API keys are configured
        if not config.api_keys:
            console.print(
                "[yellow]⚠ No API keys configured.[/yellow]\n"
                "Please run [cyan]rayo config[/cyan] to set up your API keys.\n"
            )
            sys.exit(1)

        # Create and start agent
        agent = RayoAgent(config, custom_prompt_path=config.custom_prompt_path)
        agent.start_repl()

    except KeyboardInterrupt:
        console.print("\n[cyan]👋 Goodbye![/cyan]\n")
        sys.exit(0)
    except Exception as e:
        console.print(f"[red]✗ Error:[/red] {e}\n")
        sys.exit(1)


@app.command()
def config() -> None:
    """
    Configure Rayo settings.

    Launches an interactive wizard to set up API keys and preferences.
    Configuration is saved to ~/.rayo/config.json
    """
    try:
        setup_wizard()
    except KeyboardInterrupt:
        console.print("\n[yellow]Configuration cancelled.[/yellow]\n")
        sys.exit(0)
    except Exception as e:
        console.print(f"[red]✗ Error:[/red] {e}\n")
        sys.exit(1)


@app.command()
def version() -> None:
    """
    Show the version of Rayo CLI.
    """
    from rayo import __version__

    console.print(f"Rayo CLI version [cyan]{__version__}[/cyan]")


def main() -> None:
    """Main entry point for the CLI."""
    app()


if __name__ == "__main__":
    main()
