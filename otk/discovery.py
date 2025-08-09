import os
from pathlib import Path
from typing import Optional, List

def find_project_root(start_path: Path = Path('.')) -> Optional[Path]:
    """Find the project root by searching for a .git directory or odoo.conf."""
    path = start_path.resolve()
    while path.parent != path:
        if (path / '.git').is_dir() or (path / 'odoo.conf').is_file():
            return path
        path = path.parent
    return None

def find_addons_paths(project_root: Path) -> List[Path]:
    """Find all directories containing Odoo modules."""
    addons_paths = []
    for root, dirs, files in os.walk(project_root):
        if '__manifest__.py' in files:
            addons_path = Path(root).parent
            if addons_path not in addons_paths:
                addons_paths.append(addons_path)
    return addons_paths
