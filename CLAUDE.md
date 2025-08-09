# OTK (Odoo ToolKit) - Claude Documentation

This document provides an overview of the OTK (Odoo ToolKit) structure, template system, modern code generation capabilities, and enhanced validation features.

## Project Structure

```
otk/
├── otk/                         # Main package
│   ├── commands/               # CLI command modules
│   │   ├── add.py             # Add new components (models, views, actions)
│   │   ├── add_xml.py         # XML generation utilities
│   │   ├── extend.py          # Extend existing views with inheritance
│   │   └── lint.py            # Enhanced validation with RNG schemas and modern syntax checking
│   ├── templates/             # Jinja2 template directory
│   │   ├── model/            # Model templates
│   │   ├── view/             # View templates (modern structure)
│   │   ├── action/           # Action templates
│   │   ├── menu/             # Menu templates
│   │   └── module/           # Module structure templates
│   ├── discovery.py          # Project and module discovery
│   ├── interactive.py        # User interaction utilities
│   ├── templating.py         # Template rendering engine
│   ├── reference_guide.py    # Interactive development guide and examples
│   └── main.py              # CLI entry point with guide command
└── documentation/           # Odoo framework documentation analysis
```

## Command Structure

### Core Commands

1. **`add`** - Create new Odoo components
   - `add module <name>` - Create new module structure
   - `add model <name>` - Add model to existing module
   - `add view <model>` - Generate views for model
   - `add wizard <name>` - Create TransientModel wizard
   - `add action action <model>` - Create window action
   - `add menu menu <name>` - Create menu item

2. **`extend`** - Modify existing components
   - `extend view` - Add fields to inherited views using XPath

3. **`lint`** - Enhanced validation and code quality
   - `lint views` - Comprehensive view validation with RNG schemas
   - `lint xml` - Basic XML syntax validation (legacy)

4. **`guide`** - Interactive quick reference for Odoo development
   - `guide` - Start interactive guide mode
   - `guide <topic>` - Direct access to specific examples
   - `guide <topic> <subtopic>` - Specific example with copy-paste ready code

## Modern Template System

### Template Architecture

The CLI uses a modern, hierarchical template system located in `otk/templates/`:

#### **1. View Templates** (`view/`)
- **`form_view.xml.j2`** - Clean form view generation
- **`list_view.xml.j2`** - Modern list views (replaces deprecated tree)
- **`search_view.xml.j2`** - Search and filter views
- **`kanban_view.xml.j2`** - Card-based kanban views
- **`inherited_view.xml.j2`** - View inheritance with XPath
- **`xpath_field.xml.j2`** - XPath field additions

#### **2. Model Templates** (`model/`)
- **`model.py.j2`** - Standard persistent models
- **`abstract_model.py.j2`** - Abstract model templates
- **`transient_model.py.j2`** - Wizard/temporary models
- **`ir.model.access.csv.j2`** - Security access rules

#### **3. Action Templates** (`action/`)
- **`window_action.xml.j2`** - Window actions for CRUD operations

#### **4. Menu Templates** (`menu/`)
- **`menuitem.xml.j2`** - Menu item definitions

#### **5. Module Templates** (`module/`)
- **`__manifest__.py.j2`** - Module manifest files
- **`__init__.py.j2`** - Module initialization

### Modern XML Structure

**Before (Deprecated)**:
```xml
<odoo>
    <data>
        <record id="view_model_tree" model="ir.ui.view">
            <field name="arch" type="xml">
                <tree string="Model">
                    <field name="name"/>
                </tree>
            </field>
        </record>
    </data>
</odoo>
```

**After (Modern)**:
```xml
<odoo>
    <record id="view_model_list" model="ir.ui.view">
        <field name="arch" type="xml">
            <list string="Model">
                <field name="name"/>
            </list>
        </field>
    </record>
</odoo>
```

### Key Modernizations

1. **Deprecated `tree` → Modern `list`**
   - Updated view elements: `<tree>` → `<list>`
   - Updated view IDs: `view_*_tree` → `view_*_list`
   - Updated action view_mode: `tree,form` → `list,form`

2. **Modern Attribute Syntax (Odoo 17+)**
   - Direct attributes: `invisible="True"` instead of `attrs="{'invisible': 1}"`
   - Python expressions: `readonly="state == 'done'"` instead of domain syntax
   - Logical operators: `invisible="state == 'done' or type == 'draft'"`

3. **Simplified XML Structure**
   - Removed unnecessary `<data>` wrapper tags
   - Cleaner indentation and formatting
   - Modern `<odoo>` only structure

4. **Template Resolution Logic**
   - Smart template detection in `add.py`
   - Fallback to generic templates when specific ones don't exist
   - Proper path resolution: `otk/templates/`

## Template Variables System

### Model Template Variables
```python
{
    "class_name": "ProductModel",           # PascalCase class name
    "model_name": "product.model",          # Technical model name
    "description": "Product Model",         # Human readable description
    "model_type": "Model",                  # Model|TransientModel|AbstractModel
    "inherit": "mail.thread",              # Optional inheritance
    "fields": [                            # Field definitions
        {
            "name": "name",
            "type": "Char",
            "string": "Name",
            "required": True
        }
    ]
}
```

### View Template Variables
```python
{
    "model_name": "product.model",          # Technical model name
    "model_name_snake": "product_model",    # Snake_case for IDs
    "model_human_name": "Product Model",    # Human readable name
    "layout": "sheet",                      # Form layout type
    "has_title": True,                      # Include title section
    "template_type": "simple"               # Kanban template style
}
```

### Action Template Variables
```python
{
    "model_name": "product.model",          # Target model
    "model_name_snake": "product_model",    # For ID generation
    "action_name": "ProductModel",          # Display name
    "view_mode": "list,form"               # Modern view modes
}
```

## Enhanced Validation System

### RNG Schema Validation (`lint.py`)

The CLI now includes comprehensive view validation using official Odoo RNG schemas:

#### **Supported View Types**
- **List Views**: `list_view.rng` - Field attributes, decorations, controls
- **Search Views**: `search_view.rng` - Filters, group by, search fields
- **Graph Views**: `graph_view.rng` - Chart configurations and data presentation
- **Pivot Views**: `pivot_view.rng` - Pivot table structures and grouping
- **Calendar Views**: `calendar_view.rng` - Calendar-specific attributes
- **Activity Views**: `activity_view.rng` - Activity timeline configurations

#### **Validation Features**
1. **RNG Schema Compliance**
   - Downloads official schemas from Odoo repository
   - Validates XML structure against formal specifications
   - Provides line-specific error reporting

2. **Modern Syntax Checking**
   - Detects deprecated `attrs` attribute usage (Odoo 17+)
   - Detects deprecated `states` attribute usage
   - Suggests modern replacements with Python expressions

3. **Convention Validation**
   - Deprecated `<tree>` elements → suggests `<list>`
   - Missing required view record fields (id, name, model, arch)
   - Missing `string` attributes for better UX
   - Fields without `name` attributes

#### **Usage Examples**
```bash
# Full validation with RNG schemas and convention checks
uv run otk lint views path/to/views/

# Fast validation (conventions only, skip RNG download)
uv run otk lint views path/to/views/ --skip-rng

# Validate specific file
uv run otk lint views my_view.xml

# Legacy XML syntax validation
uv run otk lint xml my_file.xml
```

#### **Validation Output**
```
✗ sale_stage/views/sale_stage_views.xml
  - L15: Deprecated 'attrs' attribute found in <field>. Since Odoo 17+, use direct attributes instead. Suggestion: invisible="True"
  - L21: Deprecated '<tree>' element found. Use '<list>' instead for modern Odoo versions.
  - L45: View record 'view_invalid' missing required field 'model'
  - RNG Validation Error (Line 52): Element field failed to validate attributes

Validation finished with 4 errors in 1 files.
```

## Interactive Development Guide

### Guide Command (`guide.py`)

The CLI provides an interactive reference system for quick Odoo development lookups:

#### **Guide Topics**
1. **Form Views** (`guide form`)
   - Basic fields, readonly/required/invisible conditions
   - Widgets (monetary, many2one, many2many_tags, images)
   - Layout components (groups, notebooks, buttons, status bars)

2. **List Views** (`guide list`)
   - Field options (optional, sum, decorations)
   - Inline editing and bulk operations
   - Row decorations and styling

3. **Search Views** (`guide search`)
   - Search fields and filters
   - Date-based filters and "My Records" patterns
   - Group by options (including date grouping)

4. **Widgets** (`guide widgets`)
   - Text widgets (email, url, phone, html)
   - Numeric widgets (monetary, percentage, handle)
   - Selection widgets (radio, statusbar, priority)
   - Relational widgets (many2many_tags, checkboxes)
   - Binary widgets (image, file, PDF viewer)

5. **Patterns & Best Practices** (`guide patterns`)
   - Modern Odoo 17+ syntax vs deprecated attrs
   - Python expressions and available variables
   - Performance optimization tips

#### **Usage Modes**

**Interactive Mode** (Menu-driven):
```bash
# Start interactive guide (default)
uv run otk guide

# Explicit interactive mode
uv run otk guide --interactive
uv run otk guide -i
```

**Direct Access** (Command-line):
```bash
# Show all examples for a topic
uv run otk guide form
uv run otk guide widgets

# Show specific example
uv run otk guide form readonly_field
uv run otk guide search my_records_filter
uv run otk guide patterns modern_attrs
```

#### **Example Output**
```
📝 Form View Reference

Add readonly field with conditions

Example:
<field name="field_name" readonly="state in ['done', 'cancel']"/>

💡 Modern syntax using Python expressions instead of deprecated attrs.
```

#### **Interactive Menu Structure**
```
📚 Odoo Development Guide 📚
├── 📝 Form Views - Fields, widgets, layout components
├── 📊 List Views - Fields, decorations, buttons
├── 🔍 Search Views - Filters, group by, search fields
├── 🎛️  Widgets - Available widgets for different field types
├── ⚡ Patterns & Best Practices - Modern Odoo conventions
├── ❓ Help - Show all available options
└── 🚪 Exit
```

## Command Logic Flow

### View Generation Process

1. **Template Selection** (`add.py:292-304`):
   ```python
   # Smart template detection with fallback
   if vtype == 'form':
       template_name = "view/form_view.xml.j2" if exists() else "view/views.xml.j2"
   elif vtype in ['list', 'tree']:
       template_name = "view/list_view.xml.j2" if exists() else "view/views.xml.j2"
   ```

2. **Context Preparation**:
   - Model name processing (snake_case, human-readable)
   - Layout and styling preferences
   - Field definitions and attributes

3. **Template Rendering**:
   - Individual view templates for single types
   - Combined rendering for multiple view types
   - Clean XML output without excessive whitespace

### View Inheritance Process

1. **Discovery** (`extend.py:52-61`):
   - Find existing inherited views in module
   - Detect target base view ID
   - Locate appropriate insertion points

2. **XPath Generation**:
   - Create XPath expressions for field placement
   - Support for `before`, `after`, `inside`, `replace` positions
   - Proper field attribute handling

3. **File Management**:
   - Append to existing inherited view files
   - Create new inherited view files when needed
   - Maintain clean XML structure

## CLI Usage Examples

### Creating Complete Module
```bash
# Create module structure
uv run otk add module sale_customization

# Add model with inheritance
uv run otk add model sale.order --module sale_customization --inherit sale.order

# Generate modern views (list, form, search, kanban)
uv run otk add view sale.order --module sale_customization --type form,list,search,kanban

# Create wizard for bulk operations
uv run otk add wizard order.bulk.update --module sale_customization

# Add action and menu
uv run otk add action action sale.order --module sale_customization
uv run otk add menu menu "Sale Orders" --module sale_customization --action sale_customization.action_sale_order --parent sale.sale_menu_root
```

### Extending Existing Views
```bash
# Add field to existing form view
uv run otk extend view --module sale_customization --view-id sale.view_order_form --field custom_stage_id --xpath "//field[@name='state']" --position after

# Add field to list view
uv run otk extend view --module sale_customization --view-id sale.view_quotation_tree --field priority --xpath "//field[@name='amount_total']" --position before
```

### Enhanced Validation Workflow
```bash
# Validate all views with RNG schemas and modern syntax checks
uv run otk lint views sale_customization/views/

# Quick validation (skip RNG download for faster checks)
uv run otk lint views sale_customization/ --skip-rng

# Validate specific view file
uv run otk lint views sale_customization/views/sale_order_views.xml
```

### Interactive Development Guide Usage
```bash
# Start interactive guide for quick reference
uv run otk guide

# Quick lookup for specific examples
uv run otk guide form readonly_field
uv run otk guide list editable_list
uv run otk guide search my_records_filter
uv run otk guide widgets many2many_tags
uv run otk guide patterns modern_attrs

# Browse all examples for a topic
uv run otk guide form
uv run otk guide widgets
```

### Complete Development Workflow
```bash
# 1. Create and scaffold module
uv run otk add module sales_enhancement
uv run otk add model sale.enhancement --module sales_enhancement

# 2. Generate views
uv run otk add view sale.enhancement --module sales_enhancement --type form,list,search

# 3. Use guide for customization ideas
uv run otk guide form monetary_field  # Learn about monetary fields
uv run otk guide list decorated_field # Learn about list decorations

# 4. Validate generated code
uv run otk lint views sales_enhancement/views/

# 5. Extend existing views if needed
uv run otk extend view --module sales_enhancement --view-id sale.view_order_form --field enhancement_notes

# 6. Final validation
uv run otk lint views sales_enhancement/
```

## Key Features

### Smart Template Resolution
- Detects available specialized templates
- Falls back gracefully to generic templates
- Maintains backward compatibility

### Modern Code Generation
- Follows current Odoo best practices
- Uses non-deprecated view elements
- Clean, readable XML structure
- Proper naming conventions

### Intelligent View Inheritance
- Finds and updates existing inherited views
- Creates new inheritance files when needed
- Supports multiple XPath additions per view
- Maintains proper XML formatting

### Comprehensive Module Generation
- Complete module directory structure
- Security access rules generation
- Manifest file management
- Proper import/export handling

### Enhanced Validation & Quality Assurance
- **RNG Schema Validation**: Official Odoo schema compliance checking
- **Modern Syntax Detection**: Identifies deprecated patterns (attrs, states, tree elements)
- **Intelligent Suggestions**: Context-aware recommendations for modern alternatives
- **Performance Optimization**: Validates against performance best practices

### Interactive Development Guide
- **Menu-Driven Interface**: Easy exploration of Odoo development patterns
- **Copy-Paste Ready Examples**: Immediately usable code snippets
- **Comprehensive Coverage**: Forms, lists, search views, widgets, and best practices
- **Context-Aware Help**: Examples include common use cases and gotchas
- **Modern Standards Focus**: Emphasizes Odoo 17+ best practices

## Integration Notes

OTK (Odoo ToolKit) is designed to:

1. **Follow Modern Standards**: Uses current Odoo conventions and non-deprecated elements
2. **Maintain Clean Code**: Generates properly formatted, readable XML and Python
3. **Support Incremental Development**: Allows extending existing modules and views
4. **Provide Smart Defaults**: Generates sensible default configurations
5. **Enable Rapid Prototyping**: Quickly scaffold complete module structures
6. **Ensure Code Quality**: Comprehensive validation against official schemas and best practices
7. **Accelerate Learning**: Interactive guide system for immediate reference and examples
8. **Promote Best Practices**: Built-in guidance for modern Odoo 17+ development patterns

## Developer Workflow Integration

OTK creates an optimal development workflow by integrating three key components:

### 1. **Code Generation** (`add`, `extend` commands)
- Scaffolds modules, models, views, and actions
- Uses modern templates with current best practices
- Supports view inheritance and customization

### 2. **Quality Validation** (`lint` command)
- **Finds Issues**: RNG schema validation and deprecated pattern detection
- **Provides Context**: Line-specific errors with clear explanations
- **Suggests Fixes**: Modern alternatives for deprecated syntax

### 3. **Learning & Reference** (`guide` command)
- **Immediate Help**: Quick lookup for "how do I add a readonly field?"
- **Copy-Paste Ready**: Production-ready examples with explanations
- **Best Practices**: Modern syntax and performance optimization tips

### Integrated Workflow Example
```bash
# Generate code
uv run otk add view sale.order --type form,list

# Validate quality
uv run otk lint views # → finds deprecated attrs usage

# Learn modern syntax
uv run otk guide patterns modern_attrs # → shows how to fix

# Apply fixes and validate again
uv run otk lint views # → clean code ✓
```

The template system ensures generated code follows official Odoo documentation guidelines while the validation and guide systems help developers maintain quality and learn modern practices throughout the development process.
