"""
Odoo development quick reference guide for CLI dry runs.
"""

from rich.console import Console
from rich.markdown import Markdown
from rich.syntax import Syntax
from rich.panel import Panel
from rich.text import Text
from typing import Dict, List, Optional
from otk.interactive import prompt_for_choice

console = Console()

FORM_VIEW_EXAMPLES = {
    "basic_field": {
        "description": "Add a basic field to form view",
        "example": '<field name="field_name" string="Custom Label"/>',
        "notes": "Basic field with custom label. Most common use case."
    },
    "readonly_field": {
        "description": "Add readonly field with conditions",
        "example": '<field name="field_name" readonly="state in [\'done\', \'cancel\']"/>',
        "notes": "Modern syntax using Python expressions instead of deprecated attrs."
    },
    "required_field": {
        "description": "Add required field with conditions", 
        "example": '<field name="field_name" required="field_a and not field_b"/>',
        "notes": "Conditional requirements based on other field values."
    },
    "invisible_field": {
        "description": "Add field with conditional visibility",
        "example": '<field name="field_name" invisible="state == \'draft\'"/>',
        "notes": "Hide/show fields based on conditions. Use direct invisible attribute."
    },
    "widget_field": {
        "description": "Add field with specific widget",
        "example": '<field name="email" widget="email"/>',
        "notes": "Common widgets: email, url, phone, monetary, percentage, many2many_tags"
    },
    "monetary_field": {
        "description": "Add monetary field with currency",
        "example": "<field name=\"amount\" widget=\"monetary\" options=\"{'currency_field': 'currency_id'}\"/>",
        "notes": "Requires currency_id field to be present in the view or model."
    },
    "many2one_field": {
        "description": "Add many2one field with options",
        "example": "<field name=\"partner_id\" options=\"{'no_create': True, 'no_quick_create': True}\"/>",
        "notes": "Control creation options for relational fields."
    },
    "many2many_tags": {
        "description": "Add many2many field as tags",
        "example": "<field name=\"tag_ids\" widget=\"many2many_tags\" options=\"{'color_field': 'color'}\"/>",
        "notes": "Displays many2many as colored tags. Requires color field in related model."
    },
    "image_field": {
        "description": "Add image field with preview",
        "example": "<field name=\"image\" widget=\"image\" options=\"{'size': [100, 100]}\"/>",
        "notes": "Shows image preview with specified dimensions."
    },
    "group": {
        "description": "Group fields in columns",
        "example": '''<group string="Contact Information">
    <field name="name"/>
    <field name="email"/>
    <field name="phone"/>
</group>''',
        "notes": "Default 2 columns. Use col='4' for custom column count."
    },
    "notebook": {
        "description": "Add tabbed sections",
        "example": '''<notebook>
    <page string="General" name="general">
        <group>
            <field name="name"/>
        </group>
    </page>
    <page string="Details" name="details">
        <group>
            <field name="description"/>
        </group>
    </page>
</notebook>''',
        "notes": "Organize content in tabs. Pages can have conditional visibility."
    },
    "button": {
        "description": "Add action button",
        "example": '<button type="object" name="action_confirm" string="Confirm" class="btn-primary"/>',
        "notes": "Common types: object, action. Classes: btn-primary, btn-secondary, btn-danger."
    },
    "status_bar": {
        "description": "Add status bar in header",
        "example": '''<header>
    <field name="state" widget="statusbar" statusbar_visible="draft,confirm,done"/>
</header>''',
        "notes": "Shows workflow states. Use statusbar_visible to control visible states."
    }
}

LIST_VIEW_EXAMPLES = {
    "basic_field": {
        "description": "Add field to list view",
        "example": '<field name="field_name" string="Custom Header"/>',
        "notes": "Basic field with custom column header."
    },
    "optional_field": {
        "description": "Add optional field (user can toggle)",
        "example": '<field name="field_name" optional="show"/>',
        "notes": "Use 'show' to display by default, 'hide' to hide by default."
    },
    "sum_field": {
        "description": "Add field with sum total",
        "example": '<field name="amount" sum="Total:"/>',
        "notes": "Shows sum at bottom. Also available: avg='Average:'"
    },
    "widget_field": {
        "description": "Add field with widget",
        "example": '<field name="priority" widget="priority"/>',
        "notes": "Common widgets: priority, many2many_tags, badge, boolean_button."
    },
    "decorated_field": {
        "description": "Add field with text decoration",
        "example": '<field name="name" decoration-bf="priority == \'high\'"/>',
        "notes": "Decorations: bf(bold), it(italic), info, warning, danger, success, muted."
    },
    "button": {
        "description": "Add button to list view",
        "example": '<button type="object" name="action_toggle" icon="fa-star"/>',
        "notes": "Use icon attribute for icon-only buttons. No string needed."
    },
    "editable_list": {
        "description": "Make list editable inline",
        "example": '<list editable="bottom">',
        "notes": "Use 'top' or 'bottom'. Allows inline editing of records."
    },
    "multi_edit": {
        "description": "Enable bulk field editing",
        "example": '<list multi_edit="1">',
        "notes": "Allows editing multiple records at once for specific fields."
    },
    "row_decoration": {
        "description": "Add row decorations based on conditions",
        "example": '<list decoration-danger="state == \'error\'" decoration-success="state == \'done\'">',
        "notes": "Applies styles to entire row based on field values."
    }
}

SEARCH_VIEW_EXAMPLES = {
    "search_field": {
        "description": "Add searchable field",
        "example": '<field name="name" string="Name" filter_domain="[(\'name\', \'ilike\', self)]"/>',
        "notes": "filter_domain defines how the search is performed."
    },
    "filter": {
        "description": "Add filter button",
        "example": '<filter string="Active" name="active" domain="[(\'active\', \'=\', True)]"/>',
        "notes": "Creates clickable filter. Use domain to define filter conditions."
    },
    "date_filter": {
        "description": "Add date-based filter",
        "example": '<filter string="This Month" name="this_month" domain="[(\'date\', \'>=\', context_today().replace(day=1).strftime(\'%Y-%m-%d\'))]"/>',
        "notes": "Use context_today() for dynamic date filters."
    },
    "my_records_filter": {
        "description": "Add 'My Records' filter",
        "example": '<filter string="My Records" name="my" domain="[(\'user_id\', \'=\', uid)]"/>',
        "notes": "Common pattern to filter records assigned to current user."
    },
    "group_by": {
        "description": "Add group by option",
        "example": '''<group expand="0" string="Group By">
    <filter string="Status" name="group_status" context="{'group_by': 'state'}"/>
    <filter string="Assigned To" name="group_user" context="{'group_by': 'user_id'}"/>
</group>''',
        "notes": "Groups records by field value. expand='0' means collapsed by default."
    },
    "date_group_by": {
        "description": "Add date-based group by",
        "example": '<filter string="Month" name="group_month" context="{\'group_by\': \'date:month\'}"/>',
        "notes": "Group by date periods: :day, :week, :month, :quarter, :year."
    },
    "separator": {
        "description": "Add visual separator",
        "example": '<separator/>',
        "notes": "Adds visual separator between filters for better organization."
    }
}

WIDGET_EXAMPLES = {
    "text_widgets": {
        "description": "Text and character field widgets",
        "examples": [
            ('email', '<field name="email" widget="email"/>'),
            ('url', '<field name="website" widget="url"/>'),
            ('phone', '<field name="phone" widget="phone"/>'),
            ('text', '<field name="description" widget="text"/>'),
            ('html', '<field name="content" widget="html"/>'),
        ],
        "notes": "Text widgets provide validation and formatting."
    },
    "numeric_widgets": {
        "description": "Numeric field widgets",
        "examples": [
            ('monetary', '<field name="amount" widget="monetary"/>'),
            ('percentage', '<field name="progress" widget="percentage"/>'),
            ('float', '<field name="weight" widget="float"/>'),
            ('handle', '<field name="sequence" widget="handle"/>'),
        ],
        "notes": "Handle widget enables drag-and-drop ordering in one2many."
    },
    "selection_widgets": {
        "description": "Selection and boolean field widgets", 
        "examples": [
            ('radio', '<field name="state" widget="radio"/>'),
            ('statusbar', '<field name="state" widget="statusbar"/>'),
            ('boolean_button', '<field name="active" widget="boolean_button"/>'),
            ('priority', '<field name="priority" widget="priority"/>'),
        ],
        "notes": "Radio shows selection as radio buttons instead of dropdown."
    },
    "relational_widgets": {
        "description": "Relational field widgets",
        "examples": [
            ('many2many_tags', '<field name="tag_ids" widget="many2many_tags"/>'),
            ('many2many_checkboxes', '<field name="category_ids" widget="many2many_checkboxes"/>'),
            ('one2many_list', '<field name="line_ids" widget="one2many_list"/>'),
        ],
        "notes": "Tags widget shows many2many as colored tags."
    },
    "binary_widgets": {
        "description": "Binary and file field widgets",
        "examples": [
            ('image', '<field name="image" widget="image"/>'),
            ('binary', '<field name="attachment" widget="binary"/>'),
            ('pdf_viewer', '<field name="document" widget="pdf_viewer"/>'),
        ],
        "notes": "Image widget shows preview, binary for file downloads."
    },
    "special_widgets": {
        "description": "Special purpose widgets",
        "examples": [
            ('color', '<field name="color" widget="color"/>'),
            ('statinfo', '<field name="total_amount" widget="statinfo"/>'),
            ('badge', '<field name="state" widget="badge"/>'),
        ],
        "notes": "Color widget provides color picker, statinfo for statistics display."
    }
}

COMMON_PATTERNS = {
    "modern_attrs": {
        "description": "Modern attribute syntax (Odoo 17+)",
        "examples": [
            "Instead of attrs=\"{'invisible': 1}\" use invisible=\"True\"",
            "Instead of attrs=\"{'readonly': [('state', '=', 'done')]}\" use readonly=\"state == 'done'\"",
            "Instead of attrs=\"{'required': [('type', '=', 'important')]}\" use required=\"type == 'important'\"",
            "Use 'and' and 'or' operators: invisible=\"state == 'done' or type == 'draft'\""
        ],
        "notes": "Direct attributes are cleaner and more performant than deprecated attrs."
    },
    "python_expressions": {
        "description": "Available variables in Python expressions",
        "examples": [
            "Field values: field_name (current record values)",
            "Current user: uid (user ID)",
            "Current date: today (YYYY-MM-DD format)",
            "Current datetime: now (YYYY-MM-DD hh:mm:ss format)", 
            "Context variables: context.get('key')",
            "Parent record: parent.field_name (in subviews)"
        ],
        "notes": "Use these variables in invisible, readonly, required expressions."
    },
    "performance": {
        "description": "Performance best practices",
        "examples": [
            "Use column_invisible instead of invisible for list view columns",
            "Limit fields in list views to essential ones only",
            "Use optional='hide' for non-critical list fields",
            "Prefer direct field access over computed expressions"
        ],
        "notes": "Following these patterns improves view loading performance."
    }
}

def show_reference(topic: str, subtopic: Optional[str] = None) -> None:
    """Show reference information for a specific topic."""
    
    if topic == "form":
        console.print("\n[bold blue]📝 Form View Reference[/]\n")
        
        if subtopic and subtopic in FORM_VIEW_EXAMPLES:
            example = FORM_VIEW_EXAMPLES[subtopic]
            console.print(f"[bold green]{example['description']}[/]")
            console.print("\n[dim]Example:[/]")
            syntax = Syntax(example['example'], "xml", theme="ansi_dark", line_numbers=False, background_color="default")
            console.print(syntax)
            console.print(f"\n[dim]💡 {example['notes']}[/]")
        else:
            console.print("Available form view examples:")
            for key, example in FORM_VIEW_EXAMPLES.items():
                console.print(f"  [cyan]{key}[/]: {example['description']}")
            console.print(f"\n[dim]Usage: uv run otk guide form <example_name>[/]")
            
    elif topic == "list":
        console.print("\n[bold blue]📊 List View Reference[/]\n")
        
        if subtopic and subtopic in LIST_VIEW_EXAMPLES:
            example = LIST_VIEW_EXAMPLES[subtopic]
            console.print(f"[bold green]{example['description']}[/]")
            console.print("\n[dim]Example:[/]")
            syntax = Syntax(example['example'], "xml", theme="ansi_dark", line_numbers=False, background_color="default")
            console.print(syntax)
            console.print(f"\n[dim]💡 {example['notes']}[/]")
        else:
            console.print("Available list view examples:")
            for key, example in LIST_VIEW_EXAMPLES.items():
                console.print(f"  [cyan]{key}[/]: {example['description']}")
            console.print(f"\n[dim]Usage: uv run otk guide list <example_name>[/]")
            
    elif topic == "search":
        console.print("\n[bold blue]🔍 Search View Reference[/]\n")
        
        if subtopic and subtopic in SEARCH_VIEW_EXAMPLES:
            example = SEARCH_VIEW_EXAMPLES[subtopic]
            console.print(f"[bold green]{example['description']}[/]")
            console.print("\n[dim]Example:[/]")
            syntax = Syntax(example['example'], "xml", theme="ansi_dark", line_numbers=False, background_color="default")
            console.print(syntax)
            console.print(f"\n[dim]💡 {example['notes']}[/]")
        else:
            console.print("Available search view examples:")
            for key, example in SEARCH_VIEW_EXAMPLES.items():
                console.print(f"  [cyan]{key}[/]: {example['description']}")
            console.print(f"\n[dim]Usage: uv run otk guide search <example_name>[/]")
            
    elif topic == "widgets":
        console.print("\n[bold blue]🎛️  Widget Reference[/]\n")
        
        if subtopic and subtopic in WIDGET_EXAMPLES:
            widget_group = WIDGET_EXAMPLES[subtopic]
            console.print(f"[bold green]{widget_group['description']}[/]")
            console.print("\n[dim]Examples:[/]")
            for widget_name, example in widget_group['examples']:
                console.print(f"\n[yellow]{widget_name}:[/]")
                syntax = Syntax(example, "xml", theme="ansi_dark", line_numbers=False, background_color="default")
                console.print(syntax)
            console.print(f"\n[dim]💡 {widget_group['notes']}[/]")
        else:
            console.print("Available widget categories:")
            for key, widget_group in WIDGET_EXAMPLES.items():
                console.print(f"  [cyan]{key}[/]: {widget_group['description']}")
            console.print(f"\n[dim]Usage: uv run otk guide widgets <category_name>[/]")
            
    elif topic == "patterns":
        console.print("\n[bold blue]⚡ Common Patterns & Best Practices[/]\n")
        
        if subtopic and subtopic in COMMON_PATTERNS:
            pattern = COMMON_PATTERNS[subtopic]
            console.print(f"[bold green]{pattern['description']}[/]")
            console.print("\n[dim]Examples:[/]")
            for example in pattern['examples']:
                console.print(f"  • {example}")
            console.print(f"\n[dim]💡 {pattern['notes']}[/]")
        else:
            console.print("Available patterns:")
            for key, pattern in COMMON_PATTERNS.items():
                console.print(f"  [cyan]{key}[/]: {pattern['description']}")
            console.print(f"\n[dim]Usage: uv run otk guide patterns <pattern_name>[/]")
            
    else:
        show_help()

def show_help() -> None:
    """Show available dry run options."""
    console.print("\n[bold blue]🚀 OTK Quick Reference[/]\n")
    
    console.print("[bold]Available Topics:[/]")
    console.print("  [cyan]form[/]     - Form view examples (fields, widgets, layout)")
    console.print("  [cyan]list[/]     - List view examples (fields, decorations, buttons)")  
    console.print("  [cyan]search[/]   - Search view examples (filters, group by)")
    console.print("  [cyan]widgets[/]  - Available widgets for different field types")
    console.print("  [cyan]patterns[/] - Common patterns and best practices")
    
    console.print(f"\n[bold]Usage Examples:[/]")
    console.print("  [dim]uv run otk guide --interactive[/]")
    console.print("  [dim]uv run otk guide form basic_field[/]")
    console.print("  [dim]uv run otk guide list optional_field[/]") 
    console.print("  [dim]uv run otk guide search filter[/]")
    console.print("  [dim]uv run otk guide widgets text_widgets[/]")
    console.print("  [dim]uv run otk guide patterns modern_attrs[/]")
    
    console.print(f"\n[bold]Quick Examples:[/]")
    console.print("  [dim]# Start interactive mode[/]")
    console.print("  [dim]uv run otk guide[/]")
    console.print("  [dim]# Show all form examples[/]")
    console.print("  [dim]uv run otk guide form[/]")
    console.print("  [dim]# Show specific widget info[/]")
    console.print("  [dim]uv run otk guide widgets relational_widgets[/]")

def start_interactive_guide():
    """Start interactive guide mode with menu-driven interface."""
    
    # Welcome screen
    welcome_text = Text()
    welcome_text.append("📚 Odoo Development Guide 📚\n", style="bold blue")
    welcome_text.append("Interactive reference for views, widgets, and patterns", style="dim cyan")

    console.print(Panel.fit(
        welcome_text,
        border_style="blue",
        padding=(1, 2)
    ))

    while True:
        try:
            # Main menu
            console.print("\n" + "="*60)
            menu_content = Text()
            menu_content.append("🚀 ", style="bold blue")
            menu_content.append("Quick Reference Guide", style="bold cyan")
            menu_content.append(" 🚀", style="bold blue")

            console.print(Panel.fit(menu_content, border_style="cyan", padding=(1, 2)))

            main_choices = [
                "📝 Form Views - Fields, widgets, layout components",
                "📊 List Views - Fields, decorations, buttons",
                "🔍 Search Views - Filters, group by, search fields",
                "🎛️  Widgets - Available widgets for different field types",
                "⚡ Patterns & Best Practices - Modern Odoo conventions",
                "❓ Help - Show all available options",
                "🚪 Exit"
            ]

            choice = prompt_for_choice("What would you like to explore?", main_choices)

            if "Form Views" in choice:
                handle_form_guide()
            elif "List Views" in choice:
                handle_list_guide()
            elif "Search Views" in choice:
                handle_search_guide()
            elif "Widgets" in choice:
                handle_widgets_guide()
            elif "Patterns" in choice:
                handle_patterns_guide()
            elif "Help" in choice:
                show_help()
                console.print("\n[yellow]Press Enter to continue...[/]")
                input()
            elif "Exit" in choice:
                console.print("\n[bold green]👋 Happy coding![/]")
                break

        except KeyboardInterrupt:
            console.print("\n\n[bold yellow]Guide cancelled by user.[/]")
            break
        except Exception as e:
            console.print(f"\n[bold red]Error: {e}[/]")
            console.print("[yellow]Press Enter to continue...[/]")
            input()

def handle_form_guide():
    """Handle form view interactive guide."""
    console.print(Panel.fit("[bold green]📝 Form View Guide[/]", border_style="green"))

    choices = []
    for key, example in FORM_VIEW_EXAMPLES.items():
        choices.append(f"{key}: {example['description']}")
    choices.append("🔙 Back to Main Menu")

    choice = prompt_for_choice("Select a form view example:", choices)

    if "Back to Main Menu" in choice:
        return

    # Extract the key from the choice
    example_key = choice.split(":")[0]
    if example_key in FORM_VIEW_EXAMPLES:
        show_reference("form", example_key)
        console.print("\n[yellow]Press Enter to continue...[/]")
        input()

def handle_list_guide():
    """Handle list view interactive guide."""
    console.print(Panel.fit("[bold yellow]📊 List View Guide[/]", border_style="yellow"))

    choices = []
    for key, example in LIST_VIEW_EXAMPLES.items():
        choices.append(f"{key}: {example['description']}")
    choices.append("🔙 Back to Main Menu")

    choice = prompt_for_choice("Select a list view example:", choices)

    if "Back to Main Menu" in choice:
        return

    example_key = choice.split(":")[0]
    if example_key in LIST_VIEW_EXAMPLES:
        show_reference("list", example_key)
        console.print("\n[yellow]Press Enter to continue...[/]")
        input()

def handle_search_guide():
    """Handle search view interactive guide."""
    console.print(Panel.fit("[bold cyan]🔍 Search View Guide[/]", border_style="cyan"))

    choices = []
    for key, example in SEARCH_VIEW_EXAMPLES.items():
        choices.append(f"{key}: {example['description']}")
    choices.append("🔙 Back to Main Menu")

    choice = prompt_for_choice("Select a search view example:", choices)

    if "Back to Main Menu" in choice:
        return

    example_key = choice.split(":")[0]
    if example_key in SEARCH_VIEW_EXAMPLES:
        show_reference("search", example_key)
        console.print("\n[yellow]Press Enter to continue...[/]")
        input()

def handle_widgets_guide():
    """Handle widgets interactive guide."""
    console.print(Panel.fit("[bold magenta]🎛️  Widget Guide[/]", border_style="magenta"))

    choices = []
    for key, widget_group in WIDGET_EXAMPLES.items():
        choices.append(f"{key}: {widget_group['description']}")
    choices.append("🔙 Back to Main Menu")

    choice = prompt_for_choice("Select a widget category:", choices)

    if "Back to Main Menu" in choice:
        return

    example_key = choice.split(":")[0]
    if example_key in WIDGET_EXAMPLES:
        show_reference("widgets", example_key)
        console.print("\n[yellow]Press Enter to continue...[/]")
        input()

def handle_patterns_guide():
    """Handle patterns interactive guide."""
    console.print(Panel.fit("[bold red]⚡ Patterns & Best Practices[/]", border_style="red"))

    choices = []
    for key, pattern in COMMON_PATTERNS.items():
        choices.append(f"{key}: {pattern['description']}")
    choices.append("🔙 Back to Main Menu")

    choice = prompt_for_choice("Select a pattern or best practice:", choices)

    if "Back to Main Menu" in choice:
        return

    example_key = choice.split(":")[0]
    if example_key in COMMON_PATTERNS:
        show_reference("patterns", example_key)
        console.print("\n[yellow]Press Enter to continue...[/]")
        input()