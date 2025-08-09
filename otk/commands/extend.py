import typer
from pathlib import Path
from rich.console import Console
from typing import Optional
from lxml import etree

from otk.discovery import find_project_root, find_addons_paths
from otk.interactive import prompt_for_choice, prompt_for_text
from otk.templating import render_template

app = typer.Typer()
console = Console()

def _find_and_update_view_file(module_path: Path, view_id: str, new_xpath_str: str) -> bool:
    """Finds a view file inheriting from view_id and appends the new xpath. Returns True if found and updated."""
    views_path = module_path / 'views'
    if not views_path.is_dir():
        return False

    parser = etree.XMLParser(remove_blank_text=True)
    for xml_file in views_path.glob('*.xml'):
        try:
            tree = etree.parse(str(xml_file), parser)
            root = tree.getroot()
            # Find records with ir.ui.view model
            for record in root.findall(".//record[@model='ir.ui.view']"):
                # Check if this record has an inherit_id field with the matching ref
                inherit_field = record.find("field[@name='inherit_id']")
                if inherit_field is not None and inherit_field.get('ref') == view_id:
                    match = record
                    break
            else:
                match = None

            if match is not None:
                console.print(f"  -> Found existing inherited view in [bold yellow]{xml_file.name}[/]. Appending new xpath.")
                arch_field = match.find(".//field[@name='arch']")
                if arch_field is not None:
                    new_xpath_element = etree.fromstring(new_xpath_str)
                    arch_field.append(new_xpath_element)
                    tree.write(str(xml_file), pretty_print=True, xml_declaration=True, encoding='utf-8')
                    return True
        except etree.XMLSyntaxError:
            continue
    return False

@app.command()
def view(
    module: Optional[str] = typer.Option(None, "--module", help="The technical name of the module to add the extension to."),
    view_id: Optional[str] = typer.Option(None, "--view-id", help="The external XML ID of the view to inherit."),
    model_name: Optional[str] = typer.Option(None, "--model", help="The technical name of the model (e.g. res.partner, project.project)."),
    field: Optional[str] = typer.Option(None, "--field", help="The name of the field to add."),
    xpath_expr: Optional[str] = typer.Option(None, "--xpath", help="The XPath expression to locate the insertion point."),
    position: Optional[str] = typer.Option(None, "--position", help="Position relative to the XPath expression (after, before, inside, replace)."),
    addons_path_str: str = typer.Option(".", "--addons-path", help="The path to the addons directory."),
):
    """Extends an existing Odoo view to add a new field."""
    console.print("[bold green]Extend an Odoo View[/]")

    # Use the provided addons path directly, or try to find project root
    addons_path = Path(addons_path_str).resolve()
    project_root = find_project_root(addons_path) or addons_path
    
    # Find all addons paths, starting with the provided one
    if project_root == addons_path:
        # If no project root found, treat the addons_path as the single addons directory
        all_addons_paths = [addons_path]
    else:
        all_addons_paths = find_addons_paths(project_root)
    all_modules = [p.name for p in all_addons_paths]

    if not module:
        module = prompt_for_choice("In which module should this view extension be created?", all_modules)
    
    if not view_id:
        view_id = prompt_for_text("What is the External XML ID of the view to extend?", default="base.view_partner_form")

    if not model_name:
        model_name = prompt_for_text("What is the technical name of the model?", default="res.partner")

    if not field:
        field = prompt_for_text("What is the name of the new field to add?")

    if not xpath_expr:
        xpath_expr = prompt_for_text("Enter the XPath expression to target an element", default="//field[@name='vat']")

    if not position:
        position = prompt_for_choice("Select a position for the new field", choices=['after', 'before', 'inside', 'replace'], default='1')

    module_path = next((p / module for p in all_addons_paths if (p / module).is_dir()), None)
    if not module_path:
        console.print(f"[bold red]Error:[/] Could not find module '{module}' in any addons path.")
        raise typer.Exit(1)

    context = {
        "xpath_expr": xpath_expr,
        "position": position,
        "field_name": field
    }
    xpath_str = render_template("view/xpath_field.xml.j2", context, None)

    updated = _find_and_update_view_file(module_path, view_id, xpath_str)

    if not updated:
        console.print("  -> No existing view found. Creating a new file.")
        view_name_part = view_id.split('.')[-1]
        new_view_context = {
            "view_id": view_id,
            "inherit_view_id": f"{module}.{view_name_part}_inherit_{Path(module_path).name}",
            "module_name": module,
            "model_name": model_name,
            "xpath_snippet": xpath_str
        }
        new_file_name = f"{view_name_part}_inherited_views.xml"
        output_path = module_path / 'views' / new_file_name
        render_template('view/inherited_view.xml.j2', new_view_context, output_path)
        console.print(f"  -> Created new view file: [bold yellow]{output_path.relative_to(project_root)}[/]")
        console.print("[yellow]Don't forget to add this file to your __manifest__.py![/]")

    console.print("\n[bold green]Success![/]")
