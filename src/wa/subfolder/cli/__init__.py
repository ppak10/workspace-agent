from .__main__ import app
from .create import register_workspace_subfolder_create
from .read import register_workspace_subfolder_read

_ = register_workspace_subfolder_create(app)
_ = register_workspace_subfolder_read(app)

__all__ = ["app"]
