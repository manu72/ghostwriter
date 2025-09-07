import re
from datetime import datetime
from pathlib import Path
from typing import Optional


def sanitize_subject(text: str, max_length: int = 30) -> str:
    """Sanitize text for use in filename, keeping only safe characters."""
    # Remove special characters, keep only alphanumeric and common separators
    sanitized = re.sub(r"[^\w\s-]", "", text.lower())
    # Replace spaces and multiple separators with single underscores
    sanitized = re.sub(r"[\s_-]+", "_", sanitized)
    # Remove leading/trailing underscores
    sanitized = sanitized.strip("_")
    # Truncate to max length
    if len(sanitized) > max_length:
        sanitized = sanitized[:max_length].rstrip("_")

    return sanitized or "example"


def generate_markdown_filename(
    example_type: str, prompt: str, timestamp: Optional[datetime] = None
) -> str:
    """Generate a filename for markdown example files.

    Format: {type}_{subject}_{datetime}.md

    Args:
        example_type: 'user' or 'llm'
        prompt: The user prompt text to derive subject from
        timestamp: Optional timestamp, defaults to current time

    Returns:
        Generated filename string
    """
    if timestamp is None:
        timestamp = datetime.now()

    # Extract subject from prompt
    subject = sanitize_subject(prompt)

    # Format timestamp
    timestamp_str = timestamp.strftime("%Y%m%d_%H%M%S")

    return f"{example_type}_{subject}_{timestamp_str}.md"


def create_markdown_content(
    prompt: str,
    response: str,
    example_type: str,
    timestamp: Optional[datetime] = None,
    title: Optional[str] = None,
) -> str:
    """Create markdown content for a training example.

    Args:
        prompt: The user prompt
        response: The assistant response
        example_type: 'user' or 'llm'
        timestamp: Optional timestamp, defaults to current time
        title: Optional custom title, defaults to prompt (truncated)

    Returns:
        Formatted markdown string
    """
    if timestamp is None:
        timestamp = datetime.now()

    if title is None:
        # Use first 50 characters of prompt as title
        title = prompt[:50].strip()
        if len(prompt) > 50:
            title += "..."

    # Format timestamp for display
    formatted_time = timestamp.strftime("%Y-%m-%d %H:%M:%S")

    return f"""# {title}

**Type:** {example_type}  
**Created:** {formatted_time}  
**Prompt:** {prompt}

## Content

{response}
"""


def ensure_examples_directory(author_dir: Path) -> Path:
    """Ensure the examples directory exists for an author.

    Args:
        author_dir: Path to the author's directory

    Returns:
        Path to the examples directory
    """
    examples_dir = author_dir / "examples"
    examples_dir.mkdir(exist_ok=True)
    return examples_dir


def save_example_as_markdown(
    author_dir: Path,
    prompt: str,
    response: str,
    example_type: str,
    timestamp: Optional[datetime] = None,
) -> Path:
    """Save a training example as a markdown file.

    Args:
        author_dir: Path to the author's directory
        prompt: The user prompt
        response: The assistant response
        example_type: 'user' or 'llm'
        timestamp: Optional timestamp, defaults to current time

    Returns:
        Path to the created markdown file
    """
    examples_dir = ensure_examples_directory(author_dir)

    if timestamp is None:
        timestamp = datetime.now()

    filename = generate_markdown_filename(example_type, prompt, timestamp)
    filepath = examples_dir / filename

    content = create_markdown_content(prompt, response, example_type, timestamp)

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)

    return filepath
