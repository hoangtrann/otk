import typer
import subprocess
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from pathlib import Path
from otk.commands import add, extend, lint
from otk.reference_guide import show_reference, show_help, start_interactive_guide
from otk.interactive import prompt_for_choice, prompt_for_text, prompt_for_confirmation
from otk.discovery import find_project_root, find_addons_paths

app = typer.Typer(invoke_without_command=True)
console = Console()

app.add_typer(add.app, name="add")
app.add_typer(extend.app, name="extend")
app.add_typer(lint.app, name="lint")

@app.callback()
def main(
    ctx: typer.Context,
    addons_path_str: str = typer.Option(".", "--addons-path", help="The path to the addons directory."),
):
    """OTK (Odoo ToolKit) - A comprehensive CLI for Odoo development.

    Run without commands to start interactive mode, or use specific commands:
    - add: Create new components (modules, models, views, actions, menus)
    - extend: Modify existing components (view inheritance)
    - lint: Enhanced validation with RNG schemas and modern syntax checking
    - guide: Interactive quick reference guide for Odoo development
    """
    if ctx.invoked_subcommand is None:
        # No subcommand was provided, start interactive mode
        interactive(addons_path_str)

@app.command()
def interactive(
    addons_path_str: str = typer.Option(".", "--addons-path", help="The path to the addons directory.")
):
    """Start interactive mode for OTK (Odoo ToolKit) with menu-driven interface."""
    welcome_text = Text()
    welcome_text.append("🚀 OTK Interactive Mode 🚀\n", style="bold blue")
    welcome_text.append("Use ↑↓ arrow keys to navigate, Enter to select, Ctrl+C to exit", style="dim cyan")

    console.print(Panel.fit(
        welcome_text,
        border_style="blue",
        padding=(1, 2)
    ))

    # Setup paths - use current working directory as base
    cwd = Path.cwd()
    if addons_path_str == ".":
        # If using default, use current working directory
        addons_path = cwd
    else:
        addons_path = Path(addons_path_str).resolve()
    
    # Find project root but prioritize user's working directory
    project_root = find_project_root(addons_path) or addons_path
    
    if project_root == addons_path or addons_path == cwd:
        all_addons_paths = [addons_path]
    else:
        all_addons_paths = find_addons_paths(project_root)
    
    # Filter to only include actual Odoo modules (have __manifest__.py)
    all_modules = []
    for path in all_addons_paths:
        if path.is_dir():
            for module_dir in path.iterdir():
                if (module_dir.is_dir() and 
                    (module_dir / '__manifest__.py').exists() and
                    module_dir.name != 'otk' and  # Exclude this project itself
                    not module_dir.name.startswith('.')):  # Exclude hidden dirs
                    all_modules.append(module_dir.name)
    
    if not all_modules:
        # If no modules found, scan current directory for module directories
        for item in addons_path.iterdir():
            if (item.is_dir() and 
                (item / '__manifest__.py').exists() and 
                item.name != 'otk' and 
                not item.name.startswith('.')):
                all_modules.append(item.name)

    # Interactive main loop
    while True:
        try:
            main_choice = show_main_menu()

            if "Module Management" in main_choice:
                handle_module_menu(all_addons_paths, addons_path)
            elif "Model Management" in main_choice:
                handle_model_menu(all_modules, addons_path)
            elif "View Management" in main_choice:
                handle_view_menu(all_modules, addons_path)
            elif "Extension Management" in main_choice:
                handle_extension_menu(all_modules, addons_path)
            elif "Exit" in main_choice:
                console.print("\n[bold green]👋 Goodbye![/]")
                break

        except KeyboardInterrupt:
            console.print("\n\n[bold yellow]Operation cancelled by user.[/]")
            break
        except Exception as e:
            console.print(f"\n[bold red]Error: {e}[/]")
            console.print("[yellow]Press Enter to continue...[/]")
            input()

def show_main_menu():
    """Display the main menu and get user choice."""
    console.print("\n" + "="*60)
    menu_content = Text()
    menu_content.append("🚀 ", style="bold blue")
    menu_content.append("OTK Main Menu", style="bold cyan")
    menu_content.append(" 🚀", style="bold blue")

    console.print(Panel.fit(menu_content, border_style="cyan", padding=(1, 2)))

    choices = [
        "1. Module Management",
        "️2. Model Management",
        "️3. View Management",
        "4. Extension Management",
        "5. Exit"
    ]

    return prompt_for_choice("What would you like to do?", choices)

def handle_module_menu(all_addons_paths, addons_path):
    """Handle module management submenu."""
    console.print(Panel.fit("[bold green]Module Management[/]", border_style="green"))

    choices = ["Create New Module", "List Existing Modules", "Back to Main Menu"]
    choice = prompt_for_choice("Select an option:", choices)

    if choice == "Create New Module":
        module_name = prompt_for_text("Enter module name (e.g., 'my_custom_module'):")
        if module_name:
            # Use the add command functionality
            try:
                result = subprocess.run([
                    "uv", "run", "otk", "add", "module", module_name,
                    "--addons-path", str(addons_path)
                ], capture_output=True, text=True, cwd=Path.cwd())

                if result.returncode == 0:
                    console.print(f"[bold green]✓ Successfully created module '{module_name}'[/]")
                else:
                    console.print(f"[bold red]✗ Error creating module: {result.stderr}[/]")
            except Exception as e:
                console.print(f"[bold red]✗ Error: {e}[/]")

    elif choice == "List Existing Modules":
        console.print("\n[bold cyan]Existing Modules:[/]")
        if all_modules:
            for i, module_name in enumerate(all_modules, 1):
                # Find the module path
                module_path = None
                for addons_path in all_addons_paths:
                    potential_path = addons_path / module_name
                    if potential_path.exists():
                        module_path = potential_path
                        break
                
                if module_path:
                    console.print(f"  {i}. [green]{module_name}[/] ([dim]{module_path}[/])")
                else:
                    console.print(f"  {i}. [green]{module_name}[/]")
        else:
            console.print("  [dim]No Odoo modules found in current directory.[/]")
            console.print("  [dim]Tip: Make sure you're in an Odoo addons directory or create a new module.[/]")

    console.print("\n[yellow]Press Enter to continue...[/]")
    input()

def handle_model_menu(all_modules, addons_path):
    """Handle model management submenu."""
    console.print(Panel.fit("[bold magenta]Model Management[/]", border_style="magenta"))

    choices = [
        "Create New Model",
        "Create Model with Inheritance",
        "Create Wizard Model",
        "Back to Main Menu"
    ]
    choice = prompt_for_choice("Select an option:", choices)

    if choice in ["Create New Model", "Create Model with Inheritance", "Create Wizard Model"]:
        module = prompt_for_choice("Select target module:", all_modules)
        model_name = prompt_for_text("Enter model name (e.g., 'project.task', 'res.partner'):")

        cmd_args = ["uv", "run", "otk"]

        if choice == "Create Wizard Model":
            cmd_args.extend(["add", "wizard", model_name, "--module", module])
        else:
            cmd_args.extend(["add", "model", model_name, "--module", module])

            if choice == "Create Model with Inheritance":
                inherit_model = prompt_for_text("Enter model to inherit from (e.g., 'mail.thread'):")
                cmd_args.extend(["--inherit", inherit_model])

        try:
            # Add the addons-path parameter to ensure correct path
            if "--addons-path" not in cmd_args:
                cmd_args.extend(["--addons-path", str(addons_path)])
            
            result = subprocess.run(cmd_args, capture_output=True, text=True, cwd=addons_path)
            if result.returncode == 0:
                console.print(f"[bold green]✓ Successfully created model '{model_name}'[/]")
                # Note: modules list should be refreshed on next menu access
            else:
                console.print(f"[bold red]✗ Error: {result.stderr}[/]")
        except Exception as e:
            console.print(f"[bold red]✗ Error: {e}[/]")

    console.print("\n[yellow]Press Enter to continue...[/]")
    input()

def handle_view_menu(all_modules, addons_path):
    """Handle view management submenu."""
    console.print(Panel.fit("[bold yellow]View Management[/]", border_style="yellow"))

    choices = [
        "Generate Views for Model",
        "Create Custom View",
        "Back to Main Menu"
    ]
    choice = prompt_for_choice("Select an option:", choices)

    if choice == "Generate Views for Model":
        module = prompt_for_choice("Select target module:", all_modules)
        model_name = prompt_for_text("Enter model name (e.g., 'project.task'):")

        view_types = []
        available_types = ["form", "list", "search", "kanban"]

        console.print("\nSelect view types to generate:")
        for view_type in available_types:
            if prompt_for_confirmation(f"Include {view_type} view?", default=True):
                view_types.append(view_type)

        if view_types:
            view_type_str = ",".join(view_types)
            try:
                result = subprocess.run([
                    "uv", "run", "otk", "add", "view", model_name,
                    "--module", module, "--type", view_type_str,
                    "--addons-path", str(addons_path)
                ], capture_output=True, text=True, cwd=addons_path)

                if result.returncode == 0:
                    console.print(f"[bold green]✓ Successfully generated {view_type_str} views for '{model_name}'[/]")
                else:
                    console.print(f"[bold red]✗ Error: {result.stderr}[/]")
            except Exception as e:
                console.print(f"[bold red]✗ Error: {e}[/]")

    console.print("\n[yellow]Press Enter to continue...[/]")
    input()

def handle_extension_menu(all_modules, addons_path):
    """Handle extension management submenu."""
    console.print(Panel.fit("[bold red]Extension Management[/]", border_style="red"))

    choices = [
        "Extend Existing View",
        "Create Menu Item",
        "Create Action",
        "Back to Main Menu"
    ]
    choice = prompt_for_choice("Select an option:", choices)

    if choice == "Extend Existing View":
        module = prompt_for_choice("Select target module:", all_modules)

        console.print("\nCommon view IDs:")
        common_views = [
            "base.view_partner_form",
            "project.edit_project",
            "sale.view_order_form",
            "stock.view_move_form",
            "Custom (enter manually)"
        ]

        view_id_choice = prompt_for_choice("Select view to extend:", common_views)

        if view_id_choice == "Custom (enter manually)":
            view_id = prompt_for_text("Enter view ID (e.g., 'base.view_partner_form'):")
        else:
            view_id = view_id_choice

        model_name = prompt_for_text("Enter model name (e.g., 'res.partner', 'project.project'):")
        field_name = prompt_for_text("Enter field name to add:")
        xpath_expr = prompt_for_text("Enter XPath expression:", default="//field[@name='name']")
        position = prompt_for_choice("Select position:", ["after", "before", "inside", "replace"])

        try:
            result = subprocess.run([
                "uv", "run", "odoo-cli", "extend", "view",
                "--module", module, "--view-id", view_id, "--model", model_name,
                "--field", field_name, "--xpath", xpath_expr, "--position", position,
                "--addons-path", str(addons_path)
            ], capture_output=True, text=True, cwd=addons_path)

            if result.returncode == 0:
                console.print(f"[bold green]✓ Successfully extended view '{view_id}'[/]")
            else:
                console.print(f"[bold red]✗ Error: {result.stderr}[/]")
        except Exception as e:
            console.print(f"[bold red]✗ Error: {e}[/]")

    elif choice in ["Create Menu Item", "Create Action"]:
        module = prompt_for_choice("Select target module:", all_modules)

        if choice == "Create Action":
            model_name = prompt_for_text("Enter model name (e.g., 'project.task'):")
            try:
                result = subprocess.run([
                    "uv", "run", "otk", "add", "action", "action", model_name,
                    "--module", module, "--addons-path", str(addons_path)
                ], capture_output=True, text=True, cwd=addons_path)

                if result.returncode == 0:
                    console.print(f"[bold green]✓ Successfully created action for '{model_name}'[/]")
                else:
                    console.print(f"[bold red]✗ Error: {result.stderr}[/]")
            except Exception as e:
                console.print(f"[bold red]✗ Error: {e}[/]")

        elif choice == "Create Menu Item":
            menu_name = prompt_for_text("Enter menu name (e.g., 'My Custom Menu'):")
            action_ref = prompt_for_text("Enter action reference (e.g., 'module.action_model'):")
            parent_menu = prompt_for_text("Enter parent menu (e.g., 'base.menu_administration')", default="")

            cmd_args = ["uv", "run", "otk", "add", "menu", "menu", menu_name, "--module", module, "--action", action_ref, "--addons-path", str(addons_path)]
            if parent_menu:
                cmd_args.extend(["--parent", parent_menu])

            try:
                result = subprocess.run(cmd_args, capture_output=True, text=True, cwd=addons_path)
                if result.returncode == 0:
                    console.print(f"[bold green]✓ Successfully created menu '{menu_name}'[/]")
                else:
                    console.print(f"[bold red]✗ Error: {result.stderr}[/]")
            except Exception as e:
                console.print(f"[bold red]✗ Error: {e}[/]")

    console.print("\n[yellow]Press Enter to continue...[/]")
    input()

@app.command()
def guide(
    topic: str = typer.Argument(None, help="Reference topic: form, list, search, widgets, patterns"),
    subtopic: str = typer.Argument(None, help="Specific subtopic (optional)"),
    interactive: bool = typer.Option(False, "-i", "--interactive", help="Start interactive guide mode")
):
    """Interactive quick reference guide for Odoo development patterns and examples.
    
    Examples:
        uv run otk guide --interactive (start interactive mode)
        uv run otk guide form basic_field
        uv run otk guide list optional_field  
        uv run otk guide search filter
        uv run otk guide widgets text_widgets
        uv run otk guide patterns modern_attrs
    """
    if interactive or (not topic and not subtopic):
        start_interactive_guide()
    elif topic and topic in ['form', 'list', 'search', 'widgets', 'patterns']:
        show_reference(topic, subtopic)
    else:
        show_help()

if __name__ == "__main__":
    app()
