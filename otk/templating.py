
from jinja2 import Environment, FileSystemLoader
from pathlib import Path
from typing import Optional

def get_template_env():
    """Initializes and returns the Jinja2 environment."""
    template_dir = Path(__file__).parent / 'templates'
    # template_dir = Path(__file__) / 'templates'
    return Environment(loader=FileSystemLoader(template_dir))

def render_template(template_name: str, context: dict, output_path: Optional[Path]) -> str:
    """
    Renders a Jinja2 template. If output_path is provided, it writes to a file.
    Always returns the rendered content as a string.

    Args:
        template_name: The name of the template file.
        context: A dictionary of variables to pass to the template.
        output_path: The optional path to write the rendered file to.
    """
    env = get_template_env()
    template = env.get_template(template_name)
    rendered_content = template.render(context)

    if output_path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(rendered_content)

    return rendered_content

