# Rayo CLI

> A professional, open-source AI coding assistant for the terminal

Rayo CLI is a production-grade Python package that brings AI-powered coding assistance directly to your terminal. Similar to Claude Code, Rayo provides intelligent file operations, code modifications, and shell command execution with built-in safety features.

## Features

- 🤖 **AI-Powered Assistant**: Leverages LiteLLM to support multiple AI providers (OpenAI, Anthropic, etc.)
- 🛡️ **Human-in-the-Loop Safety**: Confirms destructive operations before execution
- 📁 **Smart File Operations**: Read, list, and intelligently patch files with verification
- 🎨 **Beautiful Terminal UI**: Rich console output for an enhanced user experience
- ⚙️ **Easy Configuration**: Interactive setup wizard for API keys and preferences
- 🔒 **Type-Safe**: Full type hinting and Pydantic validation throughout
- 📝 **Customizable Prompts**: External system prompts that can be tailored to your workflow

## Installation

```bash
# Clone the repository
git clone https://github.com/dylanpatriarchi/rayo-cli.git
cd rayo-cli

# Install in development mode
pip install -e .
```

## Quick Start

### 1. Configure Rayo

Run the setup wizard to configure your API keys:

```bash
rayo config
```

This will create a configuration file at `~/.rayo/config.json` with your settings.

### 2. Start the Assistant

Launch the interactive AI assistant:

```bash
rayo start
```

### 3. Start Coding!

Ask Rayo to help with your coding tasks:

- "List all Python files in this directory"
- "Read the contents of main.py"
- "Refactor the calculate_total function to use list comprehension"
- "Run the tests"

## Configuration

Configuration is stored in `~/.rayo/config.json`. You can manually edit this file or use `rayo config` to update settings.

Example configuration:

```json
{
  "api_keys": {
    "openai": "sk-..."
  },
  "default_model": "gpt-4",
  "max_tokens": 4096,
  "temperature": 0.7,
  "custom_prompt_path": "/path/to/custom_prompt.md"
}
```

### Custom System Prompts

Rayo supports custom system prompts to tailor the AI's behavior to your needs. See [docs/PROMPTS.md](docs/PROMPTS.md) for detailed information on creating and using custom prompts.

## Safety Features

Rayo implements human-in-the-loop confirmations for potentially destructive operations:

- **File Modifications**: Shows a diff before applying patches
- **Shell Commands**: Displays the command before execution

You must explicitly approve these actions by typing `y` when prompted.

## Architecture

Rayo is built with a clean, modular architecture:

- **CLI Layer**: Typer-based command interface
- **Configuration Layer**: Pydantic models with JSON persistence
- **Tools Layer**: Pluggable tool system (filesystem, shell, etc.)
- **Core Agent**: LLM integration with conversation management

## Requirements

- Python 3.9 or higher
- API key for supported LLM provider (OpenAI, Anthropic, etc.)

## Development

```bash
# Install with development dependencies
pip install -e ".[dev]"

# Run type checking
mypy src/rayo

# Format code
black src/rayo

# Lint code
ruff check src/rayo
```

## License

MIT License - see LICENSE file for details

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Roadmap

- [ ] Add support for more tools (git operations, search, etc.)
- [ ] Implement conversation history persistence
- [ ] Add unit and integration tests
- [ ] Support for custom tool plugins
- [ ] Multi-turn conversation improvements
- [ ] Token usage tracking and cost estimation

---

Built with ❤️ by the Rayo community
