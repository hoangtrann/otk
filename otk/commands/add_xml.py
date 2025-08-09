import typer
from pathlib import Path
from rich.console import Console

from otk.templating import get_template_env

app = typer.Typer()
console = Console()

def _to_class_name(name: str) -> str:
    """Converts a model name like 'project.task' to 'ProjectTask'."""
    return ''.join(part.capitalize() for part in name.split('.'))

def _ensure_xml_data_wrapper(file_path: Path):
    """Ensures the file is wrapped with <odoo>...</odoo>."""
    if not file_path.exists() or file_path.stat().st_size == 0:
        file_path.write_text("<odoo>\n\n</odoo>\n", encoding='utf-8')

def _append_xml_to_file(file_path: Path, xml_content: str):
    """Appends XML content inside the <odoo> tag of a file."""
    _ensure_xml_data_wrapper(file_path)
    content = file_path.read_text(encoding='utf-8')
    marker = '</odoo>'
    if marker in content:
        content = content.replace(marker, f"{xml_content}\n{marker}")
    else:
        content += xml_content
    file_path.write_text(content, encoding='utf-8')

@app.command()
def action(
    model_name: str = typer.Argument(..., help="The model the action is for (e.g., 'res.partner')."),
    module: str = typer.Option(..., "--module", help="The technical name of the module."),
    addons_path_str: str = typer.Option(".", "--addons-path", help="The path to the addons directory."),
):
    """Creates a window action for a model."""
    console.print(f"[bold green]Creating action for:[/] {model_name} in module [bold cyan]{module}[/]")

    addons_path = Path(addons_path_str).resolve()
    module_path = addons_path / module

    if not module_path.is_dir():
        console.print(f"[bold red]Error:[/] Module not found at: {module_path}")
        raise typer.Exit(1)

    model_name_snake = model_name.replace('.', '_')
    action_context = {
        "model_name": model_name,
        "model_name_snake": model_name_snake,
        "action_name": _to_class_name(model_name),
    }

    env = get_template_env()
    template = env.get_template("action/window_action.xml.j2")
    rendered_content = template.render(action_context)

    output_file = module_path / 'views' / 'actions_and_menus.xml'
    _append_xml_to_file(output_file, rendered_content)
    console.print(f"  [green]✓[/] Appended action to: {output_file.relative_to(addons_path.parent)}")

    console.print(f"\n[bold green]Successfully created action! ✨[/]")
    console.print("Don't forget to add the XML file to your __manifest__.py if it's not already there:")
    console.print(f"    'data': [\n        'views/actions_and_menus.xml',\n        ...\n    ],", style="yellow")

@app.command()
def menu(
    name: str = typer.Argument(..., help="The UI text for the menu item."),
    module: str = typer.Option(..., "--module", help="The technical name of the module."),
    action: str = typer.Option(..., "--action", help="The XML ID of the action to trigger (e.g., 'my_module.action_my_model')."),
    parent: str = typer.Option(..., "--parent", help="The XML ID of the parent menu."),
    addons_path_str: str = typer.Option(".", "--addons-path", help="The path to the addons directory."),
):
    """Creates a menu item to trigger an action."""
    console.print(f"[bold green]Creating menu:[/] {name} in module [bold cyan]{module}[/]")

    addons_path = Path(addons_path_str).resolve()
    module_path = addons_path / module

    if not module_path.is_dir():
        console.print(f"[bold red]Error:[/] Module not found at: {module_path}")
        raise typer.Exit(1)

    menu_context = {
        "menu_name": name,
        "menu_id_snake": name.lower().replace(" ", "_"),
        "action_id": action,
        "parent_menu_id": parent,
    }

    env = get_template_env()
    template = env.get_template("menu/menuitem.xml.j2")
    rendered_content = template.render(menu_context)

    output_file = module_path / 'views' / 'actions_and_menus.xml'
    _append_xml_to_file(output_file, rendered_content)
    console.print(f"  [green]✓[/] Appended menu to: {output_file.relative_to(addons_path.parent)}")

    console.print(f"\n[bold green]Successfully created menu! ✨[/]")
    console.print("Don't forget to add the XML file to your __manifest__.py if it's not already there:")
    console.print(f"    'data': [\n        'views/actions_and_menus.xml',\n        ...\n    ],", style="yellow")
