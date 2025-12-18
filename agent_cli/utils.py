import re
from pathlib import Path
from typing import List, Optional, Tuple


def read_file_content(filepath: str) -> Optional[str]:
    """Read file content, handling both absolute and relative paths."""
    try:
        path = Path(filepath)
        if not path.is_absolute():
            path = Path.cwd() / path
        if not path.exists() or not path.is_file():
            return None
        return path.read_text(encoding="utf-8")
    except Exception:
        return None


def process_file_references(text: str, ui_instance) -> Tuple[str, List[str]]:
    """Process @filename references in text and return enhanced prompt with file contents.
    
    Args:
        text: The input text containing @filename references
        ui_instance: UI instance for printing warnings
        
    Returns:
        Tuple containing (enhanced_text, list_of_contents)
    """
    pattern = r'@("([^"]+)"|(\S+))'
    file_contents = []
    processed_text = text

    for match in re.finditer(pattern, text):
        filename = match.group(2) or match.group(3)
        content = read_file_content(filename)
        if content:
            file_contents.append(f"File: {filename}\n{content}")
            processed_text = processed_text.replace(match.group(0), f"[File: {filename}]")
        else:
            if hasattr(ui_instance, 'print_warning'):
                ui_instance.print_warning(f"Could not read file '{filename}'")

    if file_contents:
        enhanced_prompt = "\n\n".join(file_contents) + "\n\nUser request: " + processed_text
    else:
        enhanced_prompt = processed_text

    return enhanced_prompt, file_contents
