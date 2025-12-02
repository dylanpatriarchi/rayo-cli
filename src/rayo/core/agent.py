"""
Core agent logic for Rayo CLI.

This module implements the RayoAgent class, which manages the conversation
loop, tool execution, and human-in-the-loop confirmations.
"""

import json
from typing import Any, Dict, List, Optional

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm
from rich.syntax import Syntax

from rayo.config import RayoConfig
from rayo.core.llm import LLMClient
from rayo.prompts import load_system_prompt
from rayo.tools import (
    ApplyPatchTool,
    ListFilesTool,
    ReadFileTool,
    RunBashTool,
    Tool,
    ToolError,
)

console = Console()


class RayoAgent:
    """
    The main agent that orchestrates LLM interactions and tool execution.

    This agent manages the conversation history, executes tools with
    human-in-the-loop confirmations, and handles errors gracefully.
    """

    def __init__(self, config: RayoConfig, custom_prompt_path: Optional[str] = None):
        """
        Initialize the Rayo agent.

        Args:
            config: RayoConfig instance with LLM settings.
            custom_prompt_path: Optional path to a custom system prompt file.
        """
        self.config = config
        self.llm = LLMClient(config)
        self.conversation_history: List[Dict[str, str]] = []
        self.tools: Dict[str, Tool] = {
            "list_files": ListFilesTool(),
            "read_file": ReadFileTool(),
            "apply_patch": ApplyPatchTool(),
            "run_bash": RunBashTool(),
        }

        # Load system prompt from file
        try:
            system_prompt = load_system_prompt(custom_prompt_path)
        except Exception as e:
            console.print(f"[yellow]⚠ Warning: Failed to load system prompt: {e}[/yellow]")
            console.print("[dim]Using fallback prompt...[/dim]")
            system_prompt = "You are Rayo, an AI coding assistant. Help users with their coding tasks."

        # Add system prompt to conversation
        self.conversation_history.append({
            "role": "system",
            "content": system_prompt,
        })

    def chat(self, user_input: str) -> str:
        """
        Process a user message and return the agent's response.

        Args:
            user_input: The user's message.

        Returns:
            The agent's response as a string.
        """
        # Add user message to history
        self.conversation_history.append({
            "role": "user",
            "content": user_input,
        })

        # Get LLM response
        try:
            response = self.llm.complete(self.conversation_history)
        except Exception as e:
            error_msg = f"Error communicating with LLM: {e}"
            console.print(f"[red]✗[/red] {error_msg}")
            return error_msg

        # Try to parse as tool call
        tool_result = self._try_execute_tool(response)

        if tool_result is not None:
            # Tool was executed, add result to history
            self.conversation_history.append({
                "role": "assistant",
                "content": response,
            })
            self.conversation_history.append({
                "role": "user",
                "content": f"Tool execution result: {tool_result}",
            })

            # Get follow-up response from LLM
            try:
                follow_up = self.llm.complete(self.conversation_history)
                self.conversation_history.append({
                    "role": "assistant",
                    "content": follow_up,
                })
                return follow_up
            except Exception as e:
                error_msg = f"Error getting follow-up response: {e}"
                console.print(f"[red]✗[/red] {error_msg}")
                return error_msg
        else:
            # Normal text response
            self.conversation_history.append({
                "role": "assistant",
                "content": response,
            })
            return response

    def _try_execute_tool(self, response: str) -> Optional[str]:
        """
        Try to parse and execute a tool call from the LLM response.

        Args:
            response: The LLM's response text.

        Returns:
            Tool execution result as a string, or None if not a tool call.
        """
        # Try to parse as JSON
        try:
            data = json.loads(response.strip())
        except json.JSONDecodeError:
            # Not a tool call, just a normal response
            return None

        # Check if it's a tool call
        if not isinstance(data, dict) or "tool" not in data:
            return None

        tool_name = data.get("tool")
        parameters = data.get("parameters", {})
        reasoning = data.get("reasoning", "No reasoning provided")

        # Display reasoning
        console.print(f"\n[cyan]🤖 Agent reasoning:[/cyan] {reasoning}\n")

        # Get the tool
        tool = self.tools.get(tool_name)
        if not tool:
            error_msg = f"Unknown tool: {tool_name}"
            console.print(f"[red]✗[/red] {error_msg}")
            return error_msg

        # Execute tool with confirmation for destructive operations
        try:
            if tool_name in ["apply_patch", "run_bash"]:
                return self._execute_with_confirmation(tool, parameters)
            else:
                return self._execute_tool(tool, parameters)
        except ToolError as e:
            error_msg = f"Tool error: {e}"
            console.print(f"[yellow]⚠[/yellow] {error_msg}")
            return error_msg

    def _execute_tool(self, tool: Tool, parameters: Dict[str, Any]) -> str:
        """
        Execute a tool without confirmation.

        Args:
            tool: The tool to execute.
            parameters: Tool parameters.

        Returns:
            Tool execution result as a string.
        """
        console.print(f"[dim]Executing {tool.name}...[/dim]")

        result = tool.execute(**parameters)

        if result.get("success"):
            console.print(f"[green]✓[/green] {tool.name} completed")
        else:
            console.print(f"[yellow]⚠[/yellow] {tool.name} completed with warnings")

        return json.dumps(result, indent=2)

    def _execute_with_confirmation(
        self,
        tool: Tool,
        parameters: Dict[str, Any],
    ) -> str:
        """
        Execute a tool with human-in-the-loop confirmation.

        Args:
            tool: The tool to execute.
            parameters: Tool parameters.

        Returns:
            Tool execution result as a string.
        """
        # Show what will be executed
        if tool.name == "apply_patch":
            self._show_patch_preview(parameters)
        elif tool.name == "run_bash":
            self._show_command_preview(parameters)

        # Ask for confirmation
        confirmed = Confirm.ask(
            "\n[bold yellow]Proceed with this operation?[/bold yellow]",
            default=False,
        )

        if not confirmed:
            console.print("[red]✗[/red] Operation cancelled by user")
            return json.dumps({
                "success": False,
                "output": "Operation cancelled by user",
            })

        # Execute the tool
        result = tool.execute(**parameters)

        # For apply_patch, actually write the file
        if tool.name == "apply_patch" and result.get("success"):
            ApplyPatchTool.write_file(
                result["path"],
                result["new_content"],
            )
            console.print(f"[green]✓[/green] File updated: {result['path']}")

        return json.dumps(result, indent=2)

    def _show_patch_preview(self, parameters: Dict[str, Any]) -> None:
        """Show a preview of the patch to be applied."""
        path = parameters.get("path", "unknown")
        original = parameters.get("original_snippet", "")
        new = parameters.get("new_snippet", "")

        console.print(Panel.fit(
            f"[bold]File:[/bold] {path}\n\n"
            "[bold red]- Original:[/bold red]\n"
            f"{original}\n\n"
            "[bold green]+ New:[/bold green]\n"
            f"{new}",
            title="[bold yellow]⚠ File Modification[/bold yellow]",
            border_style="yellow",
        ))

    def _show_command_preview(self, parameters: Dict[str, Any]) -> None:
        """Show a preview of the command to be executed."""
        command = parameters.get("command", "")

        syntax = Syntax(
            command,
            "bash",
            theme="monokai",
            line_numbers=False,
        )

        console.print(Panel.fit(
            syntax,
            title="[bold yellow]⚠ Shell Command[/bold yellow]",
            border_style="yellow",
        ))

    def start_repl(self) -> None:
        """
        Start the interactive REPL loop.

        This is the main entry point for the agent's interactive mode.
        """
        console.print(Panel.fit(
            "[bold cyan]Rayo AI Coding Assistant[/bold cyan]\n\n"
            "I'm here to help with your coding tasks!\n"
            "Type your requests, and I'll assist with reading files,\n"
            "modifying code, running commands, and more.\n\n"
            "[dim]Type 'exit' or press Ctrl+C to quit.[/dim]",
            border_style="cyan",
        ))

        while True:
            try:
                # Get user input
                user_input = console.input("\n[bold green]You:[/bold green] ")

                if user_input.strip().lower() in ["exit", "quit", "q"]:
                    console.print("\n[cyan]👋 Goodbye![/cyan]\n")
                    break

                if not user_input.strip():
                    continue

                # Process input
                response = self.chat(user_input)

                # Display response
                console.print(f"\n[bold cyan]Rayo:[/bold cyan] {response}")

            except KeyboardInterrupt:
                console.print("\n\n[cyan]👋 Goodbye![/cyan]\n")
                break
            except Exception as e:
                console.print(f"\n[red]✗ Error:[/red] {e}\n")
