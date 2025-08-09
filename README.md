# OTK (Odoo ToolKit)

A comprehensive CLI toolkit for Odoo development, scaffolding, and validation. OTK streamlines the development process with modern code generation, intelligent validation, and interactive guidance.

## Features

🚀 **Code Generation**
- Create modules, models, views, actions, and menus with modern templates
- Support for inheritance patterns and wizard models
- Smart template resolution with fallback mechanisms

🔍 **Enhanced Validation**
- RNG schema validation against official Odoo specifications
- Modern syntax checking (Odoo 17+ best practices)
- Deprecated pattern detection with intelligent suggestions

📚 **Interactive Development Guide**
- Quick reference for forms, lists, search views, and widgets
- Copy-paste ready examples with best practices
- Menu-driven exploration of Odoo development patterns

⚡ **Modern Standards**
- Uses current Odoo conventions (`list` instead of deprecated `tree`)
- Clean XML generation without unnecessary wrapper tags
- Python expressions instead of deprecated `attrs` syntax

## Installation

### Using uv (Recommended)

```bash
# Clone the repository
git clone <repository-url>
cd otk

# Install with uv
uv sync

# Run directly
uv run otk --help
```

### Using pip

```bash
pip install -e .
otk --help
```

## Quick Start

### Interactive Mode

Start the interactive menu-driven interface:

```bash
uv run otk
# or
uv run otk interactive
```

### Direct Commands

```bash
# Create a new module
uv run otk add module my_custom_module

# Add a model with inheritance
uv run otk add model sale.order --module my_custom_module --inherit sale.order

# Generate modern views
uv run otk add view sale.order --module my_custom_module --type form,list,search,kanban

# Create a wizard
uv run otk add wizard order.bulk.update --module my_custom_module

# Add actions and menus
uv run otk add action action sale.order --module my_custom_module
uv run otk add menu menu "Custom Orders" --module my_custom_module --action my_custom_module.action_sale_order

# Extend existing views
uv run otk extend view --module my_custom_module --view-id sale.view_order_form --field custom_field

# Validate with RNG schemas
uv run otk lint views my_custom_module/views/

# Interactive development guide
uv run otk guide
uv run otk guide form readonly_field
uv run otk guide widgets many2many_tags
```

## Commands

### `add` - Create New Components

#### Modules
```bash
uv run otk add module <module_name>
```

#### Models
```bash
# Standard model
uv run otk add model <model_name> --module <module>

# With inheritance
uv run otk add model <model_name> --module <module> --inherit <base_model>

# Wizard/TransientModel
uv run otk add wizard <wizard_name> --module <module>
```

#### Views
```bash
# Generate multiple view types
uv run otk add view <model_name> --module <module> --type form,list,search,kanban

# Single view type
uv run otk add view <model_name> --module <module> --type form
```

#### Actions and Menus
```bash
# Window action
uv run otk add action action <model_name> --module <module>

# Menu item
uv run otk add menu menu "<Menu Name>" --module <module> --action <action_ref> --parent <parent_menu>
```

### `extend` - Modify Existing Components

```bash
# Add field to existing view
uv run otk extend view --module <module> --view-id <view_id> --field <field_name> --xpath "//field[@name='existing_field']" --position after
```

### `lint` - Enhanced Validation

```bash
# Full validation with RNG schemas
uv run otk lint views <path>

# Skip RNG download for faster validation
uv run otk lint views <path> --skip-rng

# Legacy XML syntax check
uv run otk lint xml <file>
```

### `guide` - Interactive Development Reference

```bash
# Interactive mode
uv run otk guide
uv run otk guide --interactive

# Direct access
uv run otk guide form
uv run otk guide form readonly_field
uv run otk guide widgets text_widgets
uv run otk guide patterns modern_attrs
```

## Project Structure

```
otk/
├── otk/                         # Main package
│   ├── commands/               # CLI command modules
│   │   ├── add.py             # Component creation
│   │   ├── add_xml.py         # XML generation utilities
│   │   ├── extend.py          # View inheritance
│   │   └── lint.py            # Enhanced validation
│   ├── templates/             # Jinja2 templates
│   │   ├── model/            # Model templates
│   │   ├── view/             # View templates (modern structure)
│   │   ├── action/           # Action templates
│   │   ├── menu/             # Menu templates
│   │   └── module/           # Module structure templates
│   ├── discovery.py          # Project and module discovery
│   ├── interactive.py        # User interaction utilities
│   ├── templating.py         # Template rendering engine
│   ├── reference_guide.py    # Interactive development guide
│   └── main.py              # CLI entry point
└── documentation/           # Framework documentation analysis
```

## Modern XML Standards

OTK generates code following modern Odoo best practices:

### Before (Deprecated)
```xml
<odoo>
    <data>
        <record id="view_model_tree" model="ir.ui.view">
            <field name="arch" type="xml">
                <tree string="Model">
                    <field name="name" attrs="{'readonly': [('state', '=', 'done')]}"/>
                </tree>
            </field>
        </record>
    </data>
</odoo>
```

### After (Modern)
```xml
<odoo>
    <record id="view_model_list" model="ir.ui.view">
        <field name="arch" type="xml">
            <list string="Model">
                <field name="name" readonly="state == 'done'"/>
            </list>
        </field>
    </record>
</odoo>
```

## Key Modernizations

- **`tree` → `list`**: Updated view elements and IDs
- **Direct attributes**: `invisible="True"` instead of `attrs` syntax
- **Python expressions**: Natural conditions instead of domain syntax
- **Clean structure**: Removed unnecessary `<data>` wrappers

## Validation Features

### RNG Schema Validation
- Downloads official Odoo schemas for validation
- Supports list, search, graph, pivot, calendar, and activity views
- Provides line-specific error reporting

### Modern Syntax Detection
- Identifies deprecated `attrs` and `states` attributes
- Suggests modern Python expression alternatives
- Detects deprecated `<tree>` elements

### Convention Checking
- Missing required view record fields
- Fields without `name` attributes
- Missing `string` attributes for better UX

## Development Workflow

1. **Generate**: Create modules and components with modern templates
2. **Validate**: Check code quality with comprehensive linting
3. **Learn**: Use the interactive guide for quick reference
4. **Extend**: Modify existing components with inheritance

```bash
# Complete workflow example
uv run otk add module sales_enhancement
uv run otk add model sale.enhancement --module sales_enhancement
uv run otk add view sale.enhancement --module sales_enhancement --type form,list
uv run otk guide form monetary_field  # Learn about monetary fields
uv run otk lint views sales_enhancement/  # Validate generated code
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes following the existing patterns
4. Add tests if applicable
5. Submit a pull request

## Requirements

- Python 3.8+
- Dependencies: typer, rich, jinja2, lxml, inquirer, requests

## License

MIT

## Author

**Hoang Tran** - thhoang.tr@gmail.com

---

For detailed documentation and examples, use the interactive guide:

```bash
uv run otk guide
```
