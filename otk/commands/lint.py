import typer
from pathlib import Path
from rich.console import Console
from typing import List, Optional, Dict, Set
from lxml import etree
import requests
import tempfile
import os

from otk.discovery import find_project_root, find_addons_paths

app = typer.Typer()
console = Console()

# RNG schema URLs for Odoo view validation
RNG_SCHEMA_URLS = {
    'common': 'https://raw.githubusercontent.com/odoo/odoo/ba15d2f79b5762b280a7a74d7e4cb202543e2898/odoo/addons/base/rng/common.rng',
    'list': 'https://raw.githubusercontent.com/odoo/odoo/ba15d2f79b5762b280a7a74d7e4cb202543e2898/odoo/addons/base/rng/list_view.rng',
    'search': 'https://raw.githubusercontent.com/odoo/odoo/ba15d2f79b5762b280a7a74d7e4cb202543e2898/odoo/addons/base/rng/search_view.rng',
    'graph': 'https://raw.githubusercontent.com/odoo/odoo/ba15d2f79b5762b280a7a74d7e4cb202543e2898/odoo/addons/base/rng/graph_view.rng',
    'pivot': 'https://raw.githubusercontent.com/odoo/odoo/ba15d2f79b5762b280a7a74d7e4cb202543e2898/odoo/addons/base/rng/pivot_view.rng',
    'calendar': 'https://raw.githubusercontent.com/odoo/odoo/ba15d2f79b5762b280a7a74d7e4cb202543e2898/odoo/addons/base/rng/calendar_view.rng',
    'activity': 'https://raw.githubusercontent.com/odoo/odoo/ba15d2f79b5762b280a7a74d7e4cb202543e2898/odoo/addons/base/rng/activity_view.rng'
}

# Cache for downloaded RNG schemas
_schema_cache = {}

def download_rng_schema(schema_type: str) -> Optional[str]:
    """Download RNG schema content and cache it."""
    if schema_type in _schema_cache:
        return _schema_cache[schema_type]
    
    if schema_type not in RNG_SCHEMA_URLS:
        return None
    
    try:
        response = requests.get(RNG_SCHEMA_URLS[schema_type], timeout=10)
        response.raise_for_status()
        schema_content = response.text
        _schema_cache[schema_type] = schema_content
        return schema_content
    except Exception as e:
        console.print(f"[yellow]Warning:[/] Failed to download {schema_type} schema: {e}")
        return None

def get_view_type_from_xml(root: etree._Element) -> Optional[str]:
    """Determine view type from XML content."""
    # Check for view records with arch field
    for record in root.xpath("//record[@model='ir.ui.view']"):
        arch_field = record.xpath(".//field[@name='arch']")
        if arch_field:
            arch_content = arch_field[0]
            # Look for view type elements in the arch
            for view_type in ['list', 'tree', 'form', 'search', 'kanban', 'graph', 'pivot', 'calendar', 'activity']:
                if arch_content.xpath(f".//{view_type}"):
                    # Map 'tree' to 'list' for modern validation
                    return 'list' if view_type == 'tree' else view_type
    
    # Direct view type detection
    for view_type in ['list', 'tree', 'form', 'search', 'kanban', 'graph', 'pivot', 'calendar', 'activity']:
        if root.xpath(f".//{view_type}"):
            return 'list' if view_type == 'tree' else view_type
    
    return None

def extract_view_elements_for_rng(root: etree._Element, view_type: str) -> List[etree._Element]:
    """Extract view elements from Odoo XML structure for RNG validation."""
    view_elements = []
    
    # Find view elements in arch fields
    for record in root.xpath("//record[@model='ir.ui.view']"):
        arch_field = record.xpath(".//field[@name='arch']")
        if arch_field:
            arch_content = arch_field[0]
            # Extract the specific view type elements
            elements = arch_content.xpath(f".//{view_type}")
            view_elements.extend(elements)
    
    # Also check for direct view elements (not in records)
    direct_elements = root.xpath(f".//{view_type}")
    view_elements.extend(direct_elements)
    
    return view_elements

def validate_view_with_rng(xml_content: str, view_type: str) -> List[str]:
    """Validate XML content against RNG schema."""
    errors = []
    
    # Download required schemas
    common_schema = download_rng_schema('common')
    view_schema = download_rng_schema(view_type)
    
    if not common_schema or not view_schema:
        errors.append(f"Could not download RNG schemas for {view_type} view validation")
        return errors
    
    try:
        # Parse the full XML to extract view elements
        root = etree.fromstring(xml_content)
        view_elements = extract_view_elements_for_rng(root, view_type)
        
        if not view_elements:
            return errors  # No view elements of this type to validate
        
        # Create temporary files for schemas
        with tempfile.NamedTemporaryFile(mode='w', suffix='.rng', delete=False) as common_file:
            common_file.write(common_schema)
            common_schema_path = common_file.name
        
        # Replace the include reference with actual path
        view_schema_content = view_schema.replace(
            'include href="common.rng"',
            f'include href="{common_schema_path}"'
        )
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.rng', delete=False) as view_file:
            view_file.write(view_schema_content)
            view_schema_path = view_file.name
        
        # Parse RNG schema
        rng_doc = etree.parse(view_schema_path)
        rng = etree.RelaxNG(rng_doc)
        
        # Validate each view element separately
        for view_element in view_elements:
            if not rng.validate(view_element):
                for error in rng.error_log:
                    source_line = getattr(view_element, 'sourceline', error.line)
                    errors.append(f"RNG Validation Error (Line {source_line}): {error.message}")
        
        # Cleanup temp files
        os.unlink(common_schema_path)
        os.unlink(view_schema_path)
        
    except Exception as e:
        errors.append(f"RNG validation failed: {e}")
    
    return errors

def get_attrs_replacement_suggestion(attrs_value: str) -> str:
    """Generate a suggestion for replacing deprecated attrs attribute."""
    suggestions = []
    
    # Parse different attribute types in the attrs
    if "invisible" in attrs_value:
        if "'invisible': 1" in attrs_value or "'invisible': True" in attrs_value:
            suggestions.append("invisible=\"True\"")
        elif "'invisible': 0" in attrs_value or "'invisible': False" in attrs_value:
            suggestions.append("invisible=\"False\"")
        elif "[(" in attrs_value:
            # Try to extract simple domain patterns
            if "state" in attrs_value and "=" in attrs_value:
                suggestions.append("invisible=\"state == 'value'\"")
            else:
                suggestions.append("invisible=\"condition\"")
    
    if "readonly" in attrs_value:
        if "'readonly': 1" in attrs_value or "'readonly': True" in attrs_value:
            suggestions.append("readonly=\"True\"")
        elif "'readonly': 0" in attrs_value or "'readonly': False" in attrs_value:
            suggestions.append("readonly=\"False\"")
        elif "[(" in attrs_value:
            if "state" in attrs_value and "!=" in attrs_value:
                suggestions.append("readonly=\"state != 'draft'\"")
            elif "state" in attrs_value and "=" in attrs_value:
                suggestions.append("readonly=\"state == 'value'\"")
            else:
                suggestions.append("readonly=\"condition\"")
    
    if "required" in attrs_value:
        if "'required': 1" in attrs_value or "'required': True" in attrs_value:
            suggestions.append("required=\"True\"")
        elif "'required': 0" in attrs_value or "'required': False" in attrs_value:
            suggestions.append("required=\"False\"")
        elif "[(" in attrs_value:
            suggestions.append("required=\"condition\"")
    
    # Handle OR/AND operations in domains
    if "|" in attrs_value:
        if suggestions:
            suggestions.append("(Note: Use 'or' for '|' operators)")
    if "&" in attrs_value:
        if suggestions:
            suggestions.append("(Note: Use 'and' for '&' operators)")
    
    if suggestions:
        return " ".join(suggestions)
    
    return "Use direct attributes (invisible, readonly, required, column_invisible)"

def validate_odoo_view_conventions(root: etree._Element, view_type: str) -> List[str]:
    """Validate Odoo-specific view conventions."""
    errors = []
    
    # Check for deprecated 'tree' views (should be 'list')
    if view_type == 'list':
        tree_elements = root.xpath("//tree")
        if tree_elements:
            for tree_elem in tree_elements:
                line = getattr(tree_elem, 'sourceline', 'unknown')
                errors.append(f"L{line}: Deprecated '<tree>' element found. Use '<list>' instead for modern Odoo versions.")
    
    # Check for deprecated 'attrs' and 'states' attributes (deprecated since Odoo 17)
    for element in root.xpath("//*[@attrs or @states]"):
        line = getattr(element, 'sourceline', 'unknown')
        element_tag = element.tag
        
        if element.get('attrs'):
            attrs_value = element.get('attrs')
            suggestion = get_attrs_replacement_suggestion(attrs_value)
            errors.append(f"L{line}: Deprecated 'attrs' attribute found in <{element_tag}>. "
                         f"Since Odoo 17+, use direct attributes instead. Suggestion: {suggestion}")
        
        if element.get('states'):
            states_value = element.get('states')
            errors.append(f"L{line}: Deprecated 'states' attribute found in <{element_tag}>. "
                         f"Since Odoo 17+, use direct attributes like 'readonly', 'invisible', etc. instead of states='{states_value}'")
    
    # Check for required attributes in view records
    for record in root.xpath("//record[@model='ir.ui.view']"):
        record_id = record.get('id')
        if not record_id:
            line = getattr(record, 'sourceline', 'unknown')
            errors.append(f"L{line}: View record missing required 'id' attribute")
        
        # Check for required fields
        required_fields = ['name', 'model', 'arch']
        for field_name in required_fields:
            field_elem = record.xpath(f".//field[@name='{field_name}']")
            if not field_elem:
                line = getattr(record, 'sourceline', 'unknown')
                errors.append(f"L{line}: View record '{record_id}' missing required field '{field_name}'")
    
    # Check for proper string attributes in views
    for view_elem in root.xpath("//list | //tree | //form | //search | //kanban | //graph | //pivot | //calendar | //activity"):
        if not view_elem.get('string') and view_elem.tag not in ['search']:
            line = getattr(view_elem, 'sourceline', 'unknown')
            errors.append(f"L{line}: <{view_elem.tag}> element should have a 'string' attribute for better UX")
    
    # Check for field elements without name attribute
    for field_elem in root.xpath("//field"):
        if not field_elem.get('name'):
            line = getattr(field_elem, 'sourceline', 'unknown')
            errors.append(f"L{line}: <field> element missing required 'name' attribute")
    
    return errors

def lint_xml_file(file_path: Path, validate_views: bool = True, skip_rng: bool = False) -> List[str]:
    """Lints a single XML file and returns a list of error messages."""
    errors = []
    try:
        parser = etree.XMLParser(resolve_entities=False)
        tree = etree.parse(str(file_path), parser)
        root = tree.getroot()

        # Basic XML validation
        # Check for unescaped ampersands in text content
        for element in root.iter():
            if element.text and '&' in element.text and '&amp;' not in element.text:
                errors.append(f"L{element.sourceline}: Unescaped '&' found in element <{element.tag}>. Use '&amp;' instead.")
        
        # View-specific validation if enabled
        if validate_views:
            view_type = get_view_type_from_xml(root)
            if view_type:
                # Always validate against Odoo conventions
                convention_errors = validate_odoo_view_conventions(root, view_type)
                errors.extend(convention_errors)
                
                # RNG schema validation for supported view types (unless skipped)
                if not skip_rng and view_type in RNG_SCHEMA_URLS:
                    xml_content = etree.tostring(root, encoding='unicode')
                    rng_errors = validate_view_with_rng(xml_content, view_type)
                    errors.extend(rng_errors)

    except etree.XMLSyntaxError as e:
        errors.append(f"XML Syntax Error: {e}")
    
    return errors

@app.command()
def views(
    path: Optional[Path] = typer.Argument(None, help="The path to a specific file or directory to lint. If not provided, lints all modules."),
    addons_path_str: str = typer.Option(".", "--addons-path", help="The path to the addons directory."),
    skip_rng: bool = typer.Option(False, "--skip-rng", help="Skip RNG schema validation (faster, basic checks only)"),
):
    """Validate Odoo XML view files using RNG schemas and convention checks."""
    console.print("[bold green]Validating Odoo View Files[/]")
    
    if skip_rng:
        console.print("[yellow]Note:[/] Skipping RNG schema validation (--skip-rng enabled)")
    
    files_to_lint = []
    if path:
        if path.is_dir():
            files_to_lint.extend(path.rglob('*.xml'))
        elif path.is_file():
            files_to_lint.append(path)
    else:
        project_root = find_project_root(Path(addons_path_str))
        if not project_root:
            console.print("[bold red]Error:[/] Could not find Odoo project root.")
            raise typer.Exit(1)
        
        for addons_path in find_addons_paths(project_root):
            views_path = addons_path / 'views'
            if views_path.is_dir():
                files_to_lint.extend(views_path.rglob('*.xml'))

    total_errors = 0
    files_with_errors = 0
    for xml_file in files_to_lint:
        errors = lint_xml_file(xml_file, validate_views=True, skip_rng=skip_rng)
        if errors:
            files_with_errors += 1
            total_errors += len(errors)
            try:
                relative_path = xml_file.relative_to(Path.cwd())
            except ValueError:
                relative_path = xml_file
            console.print(f"\n[bold red]✗[/] {relative_path}")
            for error in errors:
                console.print(f"  - {error}")
    
    if total_errors > 0:
        console.print(f"\n[bold red]Validation finished with {total_errors} errors in {files_with_errors} files.[/]")
        raise typer.Exit(1)
    else:
        console.print(f"\n[bold green]✓ Validation finished. No errors found in {len(files_to_lint)} files.[/]")

@app.command()
def xml(
    path: Optional[Path] = typer.Argument(None, help="The path to a specific file or directory to lint. If not provided, lints all modules."),
    addons_path_str: str = typer.Option(".", "--addons-path", help="The path to the addons directory."),
):
    """Lints Odoo XML files for basic syntax errors (legacy command)."""
    console.print("[bold green]Linting Odoo XML Files (Basic)[/]")
    
    files_to_lint = []
    if path:
        if path.is_dir():
            files_to_lint.extend(path.rglob('*.xml'))
        elif path.is_file():
            files_to_lint.append(path)
    else:
        project_root = find_project_root(Path(addons_path_str))
        if not project_root:
            console.print("[bold red]Error:[/] Could not find Odoo project root.")
            raise typer.Exit(1)
        
        for addons_path in find_addons_paths(project_root):
            views_path = addons_path / 'views'
            if views_path.is_dir():
                files_to_lint.extend(views_path.rglob('*.xml'))

    total_errors = 0
    files_with_errors = 0
    for xml_file in files_to_lint:
        errors = lint_xml_file(xml_file, validate_views=False)
        if errors:
            files_with_errors += 1
            total_errors += len(errors)
            try:
                relative_path = xml_file.relative_to(Path.cwd())
            except ValueError:
                relative_path = xml_file
            console.print(f"\n[bold red]✗[/] {relative_path}")
            for error in errors:
                console.print(f"  - {error}")
    
    if total_errors > 0:
        console.print(f"\n[bold red]Linting finished with {total_errors} errors in {files_with_errors} files.[/]")
        raise typer.Exit(1)
    else:
        console.print(f"\n[bold green]✓ Linting finished. No errors found in {len(files_to_lint)} files.[/]")