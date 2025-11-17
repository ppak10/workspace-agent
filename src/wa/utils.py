import importlib.util
import re

from pathlib import Path


def get_project_root(parents_index: int = 4) -> Path:
    """Find project root based on package installation location."""
    try:
        spec = importlib.util.find_spec("wa")
        if spec and spec.origin:
            package_path = Path(spec.origin).parent
            parent_folder = package_path.parent.name
            if parent_folder == "src":
                # Local Development
                # package_path: /.../workspace-agent/src/wa
                # package_path.parent.parent: /.../workspace-agent
                return package_path.parent.parent
            else:
                # PyPI Install
                # package_path: /.../workspace-agent/.venv/lib/python3.13/site-packages/wa
                # package_path.parents[parents_index]: /.../workspace-agent
                return package_path.parents[parents_index]
    except ImportError:
        pass
    return Path.cwd()


def create_pathname(name: str) -> str:
    """
    Sanitizes name to use for file or folder name
    """

    name = name.replace(" ", "_")
    name = re.sub(r'[<>:"/\\|?*\x00-\x1F]', "", name)

    return name[:255]
