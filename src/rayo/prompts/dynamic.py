"""
Dynamic prompt loading system for Rayo CLI.

This module provides intelligent prompt management that loads only
the necessary sections based on context, reducing token usage.
"""

from pathlib import Path
from typing import Dict, List, Optional


class PromptSection:
    """Represents a section of the system prompt."""
    
    def __init__(self, name: str, content: str, priority: int = 5):
        """
        Initialize a prompt section.
        
        Args:
            name: Section identifier
            content: Section content
            priority: Priority level (1=always, 10=rarely needed)
        """
        self.name = name
        self.content = content
        self.priority = priority


def parse_prompt_sections(prompt_text: str) -> Dict[str, PromptSection]:
    """
    Parse the full prompt into sections.
    
    Args:
        prompt_text: Full prompt markdown text
        
    Returns:
        Dictionary mapping section names to PromptSection objects
    """
    sections = {}
    current_section = None
    current_content = []
    
    for line in prompt_text.split('\n'):
        if line.startswith('## '):
            # Save previous section
            if current_section:
                sections[current_section] = PromptSection(
                    name=current_section,
                    content='\n'.join(current_content),
                    priority=_get_section_priority(current_section)
                )
            
            # Start new section
            current_section = line[3:].strip()
            current_content = [line]
        elif current_section:
            current_content.append(line)
    
    # Save last section
    if current_section:
        sections[current_section] = PromptSection(
            name=current_section,
            content='\n'.join(current_content),
            priority=_get_section_priority(current_section)
        )
    
    return sections


def _get_section_priority(section_name: str) -> int:
    """
    Determine section priority (1=always include, 10=rarely needed).
    
    Args:
        section_name: Name of the section
        
    Returns:
        Priority level (1-10)
    """
    # Always include (core behavior)
    if section_name in ['Identity', 'Core Principles', 'Response Format']:
        return 1
    
    # Include for first interaction
    if section_name in ['Session Initialization']:
        return 2
    
    # Include when using tools
    if section_name in ['Available Tools', 'Guardrails and Validation']:
        return 3
    
    # Include for complex tasks
    if section_name in ['Autonomous Project Understanding', 'Workflow Guidelines']:
        return 4
    
    # Include for reference
    if section_name in ['Best Practices', 'Example Interactions']:
        return 5
    
    # Rarely needed
    return 7


def build_dynamic_prompt(
    sections: Dict[str, PromptSection],
    context: Optional[str] = None,
    is_first_message: bool = False,
    using_tools: bool = False,
    max_tokens: int = 2000
) -> str:
    """
    Build a dynamic prompt based on context.
    
    Args:
        sections: Available prompt sections
        context: Current conversation context
        is_first_message: Whether this is the first user message
        using_tools: Whether tools are being used
        max_tokens: Maximum tokens for the prompt (approximate)
        
    Returns:
        Optimized prompt string
    """
    # Determine which sections to include
    include_sections = []
    
    # Always include core sections (priority 1)
    include_sections.extend([
        s for s in sections.values() if s.priority == 1
    ])
    
    # Include session init on first message
    if is_first_message:
        include_sections.extend([
            s for s in sections.values() if s.priority == 2
        ])
    
    # Include tool sections when using tools
    if using_tools:
        include_sections.extend([
            s for s in sections.values() if s.priority == 3
        ])
    
    # Add additional sections based on available token budget
    current_size = sum(len(s.content) for s in include_sections)
    estimated_tokens = current_size // 4  # Rough estimate: 4 chars = 1 token
    
    # Add more sections if we have token budget
    for priority in [4, 5, 6, 7]:
        if estimated_tokens >= max_tokens:
            break
        
        for section in sections.values():
            if section.priority == priority and section not in include_sections:
                section_tokens = len(section.content) // 4
                if estimated_tokens + section_tokens <= max_tokens:
                    include_sections.append(section)
                    estimated_tokens += section_tokens
    
    # Build the final prompt
    prompt_parts = [s.content for s in include_sections]
    return '\n\n'.join(prompt_parts)


def load_dynamic_prompt(
    custom_prompt_path: Optional[str] = None,
    context: Optional[str] = None,
    is_first_message: bool = False,
    using_tools: bool = False,
    max_tokens: int = 2000
) -> str:
    """
    Load a dynamically optimized system prompt.
    
    Args:
        custom_prompt_path: Optional path to custom prompt
        context: Current conversation context
        is_first_message: Whether this is the first message
        using_tools: Whether tools are being used
        max_tokens: Maximum tokens for the prompt
        
    Returns:
        Optimized system prompt
    """
    # Load full prompt
    if custom_prompt_path:
        prompt_path = Path(custom_prompt_path)
    else:
        prompt_path = Path(__file__).parent / "system_prompt.md"
    
    with open(prompt_path, 'r', encoding='utf-8') as f:
        full_prompt = f.read()
    
    # Parse into sections
    sections = parse_prompt_sections(full_prompt)
    
    # Build dynamic prompt
    return build_dynamic_prompt(
        sections=sections,
        context=context,
        is_first_message=is_first_message,
        using_tools=using_tools,
        max_tokens=max_tokens
    )


__all__ = ['load_dynamic_prompt', 'PromptSection', 'parse_prompt_sections']
