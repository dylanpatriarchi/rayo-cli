# System Prompts

Rayo uses an external system prompt file to define the AI assistant's behavior. This approach offers several advantages:

## Default System Prompt

The default system prompt is located at:
```
src/rayo/prompts/system_prompt.md
```

This file contains:
- **Identity**: Who Rayo is and its core principles
- **Tool Documentation**: Detailed descriptions of all available tools
- **Workflow Guidelines**: Best practices for common tasks
- **Example Interactions**: Sample conversations showing proper tool usage
- **Error Handling**: How to recover from common errors

## Custom System Prompts

You can create your own custom system prompt to tailor Rayo's behavior to your needs.

### Creating a Custom Prompt

1. Create a new markdown file with your custom prompt:
   ```bash
   cp src/rayo/prompts/system_prompt.md my_custom_prompt.md
   ```

2. Edit `my_custom_prompt.md` to customize:
   - Tone and personality
   - Coding standards and conventions
   - Project-specific guidelines
   - Additional tools or workflows

3. Configure Rayo to use your custom prompt:
   ```bash
   rayo config
   ```
   
   Or manually edit `~/.rayo/config.json`:
   ```json
   {
     "custom_prompt_path": "/path/to/my_custom_prompt.md"
   }
   ```

### Use Cases for Custom Prompts

**Team Standards**:
```markdown
## Code Style
- Always use 2 spaces for indentation
- Prefer functional programming patterns
- Write tests for all new functions
```

**Framework-Specific**:
```markdown
## React Best Practices
- Use functional components with hooks
- Implement proper error boundaries
- Follow the project's component structure
```

**Language-Specific**:
```markdown
## Python Guidelines
- Follow PEP 8 strictly
- Use type hints for all functions
- Prefer dataclasses over dictionaries
```

**Security-Focused**:
```markdown
## Security Rules
- Never log sensitive data
- Always validate user input
- Use parameterized queries for SQL
```

## Prompt Structure

A good system prompt should include:

1. **Identity**: Who the assistant is
2. **Principles**: Core values and approach
3. **Tools**: What capabilities are available
4. **Guidelines**: How to use tools effectively
5. **Examples**: Concrete usage patterns
6. **Limitations**: What the assistant cannot do

## Tips for Writing Prompts

- **Be Specific**: Clear instructions produce better results
- **Use Examples**: Show, don't just tell
- **Set Boundaries**: Define what should and shouldn't be done
- **Include Context**: Explain the "why" behind guidelines
- **Test Iteratively**: Refine based on actual usage

## Sharing Prompts

Since prompts are just markdown files, you can:
- Version control them with git
- Share them with your team
- Create prompt libraries for different projects
- Contribute improvements back to the community

## Advanced: Prompt Templates

You can create prompt templates for different scenarios:

```bash
prompts/
├── system_prompt.md          # Default
├── prompts/
│   ├── backend_dev.md        # Backend development
│   ├── frontend_dev.md       # Frontend development
│   ├── devops.md             # DevOps tasks
│   └── code_review.md        # Code review mode
```

Switch between them by updating the config or using environment variables.
