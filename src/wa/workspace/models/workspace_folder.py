from .workspace_base_model import WorkspaceBaseModel


class WorkspaceFolder(WorkspaceBaseModel):
    """
    Recursive Workspace Folder class.
    """

    def initialize(self, force: bool = False):
        self.path.mkdir(exist_ok=force)
        for name, folder in self.folders.items():
            folder.path = self.path / name
            folder.initialize(force=force)
