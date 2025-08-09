import typer
from pathlib import Path
from rich.console import Console
from typing import Optional

from otk.discovery import find_project_root, find_addons_paths
from otk.templating import render_template, get_template_env
from otk.commands import add_xml
from otk.interactive import prompt_for_choice, prompt_for_text

app = typer.Typer()
console = Console()

app.add_typer(add_xml.app, name="action")
app.add_typer(add_xml.app, name="menu")

def _to_class_name(name: str) -> str:
    """Converts a model name like 'project.task' to 'ProjectTask'."""
    return ''.join(part.capitalize() for part in name.split('.'))

@app.command()
def module(
    name: str = typer.Argument(..., help="The technical name of the module."),
    addons_path_str: str = typer.Option(".", "--addons-path", help="The path to the addons directory."),
):
    """Creates a new Odoo module."""
    console.print(f"[bold green]Creating new Odoo module:[/] [bold cyan]{name}[/]")
    
    addons_path = Path(addons_path_str).resolve()
    module_path = addons_path / name
    
    if module_path.exists():
        console.print(f"[bold red]Error:[/] Module directory already exists at: {module_path}")
        raise typer.Exit(1)
    
    # Create module directory structure
    module_path.mkdir(parents=True)
    (module_path / 'models').mkdir()
    (module_path / 'views').mkdir() 
    (module_path / 'security').mkdir()
    (module_path / 'data').mkdir()
    (module_path / 'demo').mkdir()
    (module_path / 'wizard').mkdir()
    (module_path / 'static' / 'description').mkdir(parents=True)
    (module_path / 'static' / 'src' / 'js').mkdir(parents=True)
    (module_path / 'static' / 'src' / 'css').mkdir(parents=True)
    
    # Context for templates
    module_context = {
        "module_name": name,
        "summary": f"A brief description of {name}",
        "description": f"Long description of {name}",
        "author": "Your Company",
        "website": "https://www.yourcompany.com",
        "category": "Uncategorized",
        "license": "LGPL-3", 
        "sequence": 100,
        "depends": [],  # Will default to ['base'] in template
        "is_application": True,
        "auto_install": False,
    }
    
    # Create __manifest__.py
    manifest_path = module_path / '__manifest__.py'
    render_template("module/__manifest__.py.j2", module_context, manifest_path)
    console.print(f"  [green]✓[/] Created manifest file: {manifest_path.relative_to(addons_path.parent)}")
    
    # Create __init__.py
    init_path = module_path / '__init__.py'
    render_template("module/__init__.py.j2", {}, init_path)
    console.print(f"  [green]✓[/] Created init file: {init_path.relative_to(addons_path.parent)}")
    
    # Create models/__init__.py
    models_init_path = module_path / 'models' / '__init__.py'
    models_init_path.write_text("")
    console.print(f"  [green]✓[/] Created models init file: {models_init_path.relative_to(addons_path.parent)}")
    
    console.print(f"\n[bold green]Successfully created module {name}! ✨[/]")
    console.print(f"Module created at: {module_path}")
    console.print("\n[bold blue]Next steps:[/]")
    console.print("• Add models to the models/ directory")
    console.print("• Create views in the views/ directory") 
    console.print("• Configure security in security/ir.model.access.csv")
    console.print("• Update the __manifest__.py file with your data files")

@app.command()
def model(
    name: Optional[str] = typer.Argument(None, help="The name of the model (e.g., 'res.partner')."),
    module: Optional[str] = typer.Option(None, "--module", help="The technical name of the module to add the model to."),
    model_type: Optional[str] = typer.Option("Model", "--type", help="Type of model: Model, TransientModel, or AbstractModel."),
    inherit: Optional[str] = typer.Option(None, "--inherit", help="Model to inherit from (e.g., 'mail.thread')."),
    addons_path_str: str = typer.Option(".", "--addons-path", help="The path to the addons directory."),
):
    """Creates a new model in an existing Odoo module."""
    project_root = find_project_root(Path(addons_path_str))
    addons_path = Path(addons_path_str).resolve()
    
    if project_root:
        all_addons_paths = find_addons_paths(project_root)
        all_modules = [p.name for p in all_addons_paths]
    else:
        # If no project root found, scan the provided addons path directly
        all_modules = []
        for item in addons_path.iterdir():
            if item.is_dir() and (item / '__manifest__.py').exists():
                all_modules.append(item.name)

    if not module:
        module = prompt_for_choice("In which module would you like to create the new model?", all_modules)
    
    if not name:
        name = prompt_for_text("What is the name of the new model? (e.g., 'res.partner')")

    # Interactive model type selection
    if not model_type:
        model_type_choice = prompt_for_choice(
            "What type of model do you want to create?", 
            ["Model (Standard persistent model)", "TransientModel (Wizard/temporary)", "AbstractModel (For inheritance)"],
            default='0'
        )
        if "TransientModel" in model_type_choice:
            model_type = "TransientModel"
        elif "AbstractModel" in model_type_choice:
            model_type = "AbstractModel"
        else:
            model_type = "Model"

    console.print(f"[bold green]Creating new {model_type}:[/] {name} in module [bold cyan]{module}[/]")

    module_path = addons_path / module

    if not module_path.is_dir():
        console.print(f"[bold red]Error:[/] Module not found at: {module_path}")
        raise typer.Exit(1)

    model_name_snake = name.replace('.', '_')
    model_file_path = module_path / 'models' / f'{model_name_snake}.py'

    if model_file_path.exists():
        console.print(f"[bold red]Error:[/] Model file already exists: {model_file_path}")
        raise typer.Exit(1)

    # Select appropriate template based on model type
    template_name = "model/model.py.j2"  # Default template handles all types
    if model_type == "TransientModel":
        # Check if specialized template exists
        try:
            get_template_env().get_template("model/transient_model.py.j2")
            template_name = "model/transient_model.py.j2"
        except:
            pass  # Fall back to default
    elif model_type == "AbstractModel":
        try:
            get_template_env().get_template("model/abstract_model.py.j2")  
            template_name = "model/abstract_model.py.j2"
        except:
            pass  # Fall back to default

    # 1. Create the model's .py file from template
    model_context = {
        "class_name": _to_class_name(name),
        "model_name": name,
        "description": f"{model_type} {name}",
        "model_type": model_type,
        "inherit": inherit,
        "api_decorators": model_type in ["TransientModel", "AbstractModel"],
    }
    
    # Add type-specific context
    if model_type == "TransientModel":
        model_context.update({
            "fields": [
                {"name": "name", "type": "Char", "string": "Name", "required": True}
            ]
        })
    elif model_type == "AbstractModel":
        model_context.update({
            "fields": [
                {"name": "name", "type": "Char", "string": "Name", "required": True}
            ]
        })

    render_template(template_name, model_context, model_file_path)
    console.print(f"  [green]✓[/] Created model file: {model_file_path.relative_to(addons_path.parent)}")

    # 2. Update models/__init__.py
    init_py_path = module_path / 'models' / '__init__.py'
    with open(init_py_path, 'a') as f:
        f.write(f"\nfrom . import {model_name_snake}\n")
    console.print(f"  [green]✓[/] Updated {init_py_path.relative_to(addons_path.parent)}")

    # 3. Create or update ir.model.access.csv (only for persistent models)
    if model_type != "AbstractModel":
        access_csv_path = module_path / 'security' / 'ir.model.access.csv'
        access_context = {"model_name_snake": model_name_snake}
        if not access_csv_path.exists():
            render_template("model/ir.model.access.csv.j2", access_context, access_csv_path)
            console.print(f"  [green]✓[/] Created security file: {access_csv_path.relative_to(addons_path.parent)}")
        else:
            # Just append the rule, skipping the header
            env = get_template_env()
            template = env.get_template("model/ir.model.access.csv.j2")
            rendered_content = template.render(access_context)
            rule_line = rendered_content.splitlines()[1]
            with open(access_csv_path, 'a') as f:
                f.write(f"\n{rule_line}")
            console.print(f"  [green]✓[/] Appended access rule to: {access_csv_path.relative_to(addons_path.parent)}")

    console.print(f"\n[bold green]Successfully created {model_type} {name}! ✨[/]")
    
    if model_type != "AbstractModel":
        console.print("Don't forget to add the security file to your __manifest__.py if it's not already there:")
        console.print(f"    'data': [\n        'security/ir.model.access.csv',\n        ...\n    ],", style="yellow")
    
    if model_type == "TransientModel":
        console.print("\n[bold blue]Next steps for your wizard:[/]")
        console.print("• Add wizard fields to the model")
        console.print("• Create a wizard form view")
        console.print("• Add an action to open the wizard")
        console.print("• Implement the wizard logic in action_confirm()")
        
    elif model_type == "AbstractModel":
        console.print("\n[bold blue]Next steps for your abstract model:[/]")
        console.print("• Add common fields and methods")
        console.print("• Create concrete models that inherit from this abstract model")
        console.print("• Use _inherit = '{}' in other models".format(name))

@app.command()
def view(
    model_name: Optional[str] = typer.Argument(None, help="The model to create views for (e.g., 'res.partner')."),
    module: Optional[str] = typer.Option(None, "--module", help="The technical name of the module to add the views to."),
    view_type: Optional[str] = typer.Option("form,list", "--type", help="View types to create (form,list,search,kanban)."),
    layout: Optional[str] = typer.Option("sheet", "--layout", help="Form layout type (sheet or simple)."),
    addons_path_str: str = typer.Option(".", "--addons-path", help="The path to the addons directory."),
):
    """Creates views for a model with enhanced options."""
    project_root = find_project_root(Path(addons_path_str))
    addons_path = Path(addons_path_str).resolve()
    
    if project_root:
        all_addons_paths = find_addons_paths(project_root)
        all_modules = [p.name for p in all_addons_paths]
    else:
        # If no project root found, scan the provided addons path directly
        all_modules = []
        for item in addons_path.iterdir():
            if item.is_dir() and (item / '__manifest__.py').exists():
                all_modules.append(item.name)

    if not module:
        module = prompt_for_choice("In which module would you like to create the views?", all_modules)
    
    if not model_name:
        model_name = prompt_for_text("What is the model name? (e.g., 'res.partner')")

    # Parse view types
    view_types = [vt.strip() for vt in view_type.split(',')]
    
    console.print(f"[bold green]Creating views for model:[/] {model_name} in module [bold cyan]{module}[/]")
    console.print(f"[bold blue]View types:[/] {', '.join(view_types)}")

    module_path = addons_path / module

    if not module_path.is_dir():
        console.print(f"[bold red]Error:[/] Module not found at: {module_path}")
        raise typer.Exit(1)

    model_name_snake = model_name.replace('.', '_')
    model_human_name = model_name.replace('.', ' ').replace('_', ' ').title()
    
    # Create views directory if it doesn't exist
    views_dir = module_path / 'views'
    views_dir.mkdir(exist_ok=True)

    views_file_path = views_dir / f'{model_name_snake}_views.xml'

    # Prepare context for view generation
    view_context = {
        "model_name": model_name,
        "model_name_snake": model_name_snake,
        "model_human_name": model_human_name,
        "has_title": True,
        "has_statusbar": False,
        "is_wizard": False,
        "layout": layout,
    }

    # Generate views based on type
    rendered_views = []
    
    for vtype in view_types:
        if vtype == 'form':
            template_name = "view/form_view.xml.j2" if Path(__file__).parent.parent.joinpath("templates/view/form_view.xml.j2").exists() else "view/views.xml.j2"
            rendered_views.append(render_template(template_name, view_context, None))
        elif vtype in ['list', 'tree']:
            template_name = "view/list_view.xml.j2" if Path(__file__).parent.parent.joinpath("templates/view/list_view.xml.j2").exists() else "view/views.xml.j2"
            rendered_views.append(render_template(template_name, view_context, None))
        elif vtype == 'search':
            template_name = "view/search_view.xml.j2" if Path(__file__).parent.parent.joinpath("templates/view/search_view.xml.j2").exists() else "view/views.xml.j2" 
            rendered_views.append(render_template(template_name, view_context, None))
        elif vtype == 'kanban':
            view_context["template_type"] = "simple"
            template_name = "view/kanban_view.xml.j2" if Path(__file__).parent.parent.joinpath("templates/view/kanban_view.xml.j2").exists() else "view/views.xml.j2"
            rendered_views.append(render_template(template_name, view_context, None))

    # Combine all views into one file
    if len(rendered_views) == 1:
        # Single view, wrap in proper XML structure if needed
        content = rendered_views[0].strip()
        if not content.startswith('<odoo>'):
            combined_content = '<odoo>\n' + content + '\n</odoo>'
        else:
            combined_content = content
        with open(views_file_path, 'w', encoding='utf-8') as f:
            f.write(combined_content)
    else:
        # Multiple views, combine them
        combined_content = '<odoo>\n'
        for view_content in rendered_views:
            content = view_content.strip()
            # Extract content between <data> tags if present
            if '<data>' in content:
                data_start = content.find('<data>') + len('<data>')
                data_end = content.rfind('</data>')
                extracted_content = content[data_start:data_end].strip()
                if extracted_content:
                    combined_content += extracted_content + '\n\n'
            # If no <data> tag, extract content between <odoo> tags
            elif '<odoo>' in content:
                odoo_start = content.find('<odoo>') + len('<odoo>')
                odoo_end = content.rfind('</odoo>')
                extracted_content = content[odoo_start:odoo_end].strip()
                if extracted_content:
                    combined_content += extracted_content + '\n\n'
            # If neither tag, assume it's raw record content
            else:
                if content:
                    combined_content += content + '\n\n'
        combined_content += '</odoo>'
        
        with open(views_file_path, 'w', encoding='utf-8') as f:
            f.write(combined_content)

    console.print(f"  [green]✓[/] Created views file: {views_file_path.relative_to(addons_path.parent)}")

    # Update __manifest__.py
    console.print(f"\n[bold green]Successfully created views for {model_name}! ✨[/]")
    console.print("Don't forget to add the views file to your __manifest__.py:")
    console.print(f"    'data': [\n        'views/{model_name_snake}_views.xml',\n        ...\n    ],", style="yellow")


@app.command()
def wizard(
    name: Optional[str] = typer.Argument(None, help="The name of the wizard (e.g., 'import.wizard')."),
    module: Optional[str] = typer.Option(None, "--module", help="The technical name of the module to add the wizard to."),
    addons_path_str: str = typer.Option(".", "--addons-path", help="The path to the addons directory."),
):
    """Creates a complete wizard (TransientModel + Form View + Action)."""
    project_root = find_project_root(Path(addons_path_str))
    addons_path = Path(addons_path_str).resolve()
    
    if project_root:
        all_addons_paths = find_addons_paths(project_root)
        all_modules = [p.name for p in all_addons_paths]
    else:
        # If no project root found, scan the provided addons path directly
        all_modules = []
        for item in addons_path.iterdir():
            if item.is_dir() and (item / '__manifest__.py').exists():
                all_modules.append(item.name)

    if not module:
        module = prompt_for_choice("In which module would you like to create the wizard?", all_modules)
    
    if not name:
        name = prompt_for_text("What is the name of the wizard? (e.g., 'import.wizard')")

    console.print(f"[bold green]Creating wizard:[/] {name} in module [bold cyan]{module}[/]")

    module_path = addons_path / module

    if not module_path.is_dir():
        console.print(f"[bold red]Error:[/] Module not found at: {module_path}")
        raise typer.Exit(1)

    model_name_snake = name.replace('.', '_')
    class_name = _to_class_name(name)

    # 1. Create the wizard model
    model_file_path = module_path / 'wizard' / f'{model_name_snake}.py'
    model_file_path.parent.mkdir(exist_ok=True)

    wizard_context = {
        "class_name": class_name,
        "model_name": name,
        "description": f"{class_name} Wizard",
        "fields": [
            {"name": "name", "type": "Char", "string": "Name", "required": True}
        ]
    }
    
    render_template("model/transient_model.py.j2", wizard_context, model_file_path)
    console.print(f"  [green]✓[/] Created wizard model: {model_file_path.relative_to(addons_path.parent)}")

    # 2. Update wizard/__init__.py
    init_py_path = module_path / 'wizard' / '__init__.py'
    if not init_py_path.exists():
        init_py_path.write_text("")
    with open(init_py_path, 'a') as f:
        f.write(f"\nfrom . import {model_name_snake}\n")
    console.print(f"  [green]✓[/] Updated {init_py_path.relative_to(addons_path.parent)}")

    # 3. Update main __init__.py to include wizard
    main_init_path = module_path / '__init__.py'
    if main_init_path.exists():
        content = main_init_path.read_text()
        if 'from . import wizard' not in content:
            with open(main_init_path, 'a') as f:
                f.write("\nfrom . import wizard\n")
            console.print(f"  [green]✓[/] Updated main __init__.py")

    # 4. Create wizard form view
    views_dir = module_path / 'wizard'
    wizard_view_path = views_dir / f'{model_name_snake}_views.xml'

    view_context = {
        "model_name": name,
        "model_name_snake": model_name_snake,
        "model_human_name": name.replace('.', ' ').replace('_', ' ').title(),
        "is_wizard": True,
        "has_title": False,
        "layout": "simple",
    }
    
    render_template("view/form_view.xml.j2", view_context, wizard_view_path)
    console.print(f"  [green]✓[/] Created wizard view: {wizard_view_path.relative_to(addons_path.parent)}")

    # 5. Create window action for wizard
    action_context = {
        "action_name": f"{name}_action",
        "model_name": name,
        "view_mode": "form",
        "target": "new",
        "action_type": "ir.actions.act_window"
    }
    
    action_path = module_path / 'wizard' / f'{model_name_snake}_action.xml'
    render_template("action/window_action.xml.j2", action_context, action_path)
    console.print(f"  [green]✓[/] Created wizard action: {action_path.relative_to(addons_path.parent)}")

    console.print(f"\n[bold green]Successfully created wizard {name}! ✨[/]")
    console.print("Don't forget to add the wizard files to your __manifest__.py:")
    console.print(f"    'data': [", style="yellow")
    console.print(f"        'wizard/{model_name_snake}_views.xml',", style="yellow")
    console.print(f"        'wizard/{model_name_snake}_action.xml',", style="yellow")
    console.print(f"        ...", style="yellow")
    console.print(f"    ],", style="yellow")
    console.print("\n[bold blue]Next steps:[/]")
    console.print("• Add wizard fields to the model")
    console.print("• Implement the wizard logic in action_confirm()")
    console.print("• Add menu item or button to open the wizard")
    console.print(f"• Action XML ID: {module}.{name}_action")
