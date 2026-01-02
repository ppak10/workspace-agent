from __future__ import annotations

from pathlib import Path
from pydantic import Field, model_validator

from wa import __version__
from wa.utils import get_project_root

from .workspace_base_model import WorkspaceBaseModel
from .workspace_folder import WorkspaceFolder


class Workspace(WorkspaceBaseModel):
    """
    Metadata for workspace.
    """

    version: str = Field(default_factory=lambda: __version__)
    workspaces_path: Path = Path("")
    config_file: str = "workspace.json"

    @model_validator(mode="after")
    def populate_missing_paths(self) -> "Workspace":
        if not self.workspaces_path:
            self.workspaces_path = get_project_root() / "workspaces"

        if self.path == Path(""):
            self.path = self.workspaces_path / self.name

        return self

    def _merge_folders(
        self,
        existing: WorkspaceFolder,
        new: WorkspaceFolder,
        force: bool = False,
    ) -> None:
        """
        Recursively merge new folder structure into existing folder.

        Args:
            existing: The existing WorkspaceFolder to merge into.
            new: The new WorkspaceFolder to merge from.
            force: Whether to overwrite existing folders.
        """
        # Merge the nested subfolders from new into existing
        for index, (name, new_nested) in enumerate(new.folders.items()):
            if name in existing.folders:
                # Copy path from existing folder to new folder
                new_nested.path = existing.folders[name].path
                # Recursively merge if nested subfolder already exists
                # TODO: Add in overwrite check.
                self._merge_folders(existing.folders[name], new_nested, force=force)
            else:
                # Add the new nested subfolder
                new_nested.path = existing.path / name
                new_nested.initialize(force=force)
                existing.folders[name] = new_nested

    def _get_deepest_folder(self, folder: WorkspaceFolder) -> WorkspaceFolder:
        """
        Get the deepest nested folder in a folder hierarchy.

        Args:
            folder: The folder to start from.

        Returns:
            The deepest nested folder.
        """
        if folder.folders:
            # Get the first (and should be only) nested subfolder
            nested = next(iter(folder.folders.values()))
            return self._get_deepest_folder(nested)
        return folder

    def create_folder(
        self,
        name_or_path: str | Path | list[str],
        append_timestamp: bool = False,
        force: bool = False,
        **kwargs,
    ) -> WorkspaceFolder:
        """
        Create a folder inside this workspace.

        Args:
            name_or_path: Folder name, Path (relative to workspace), or list of folder names for nested structure.
            append_timestamp: Whether to append timestamp to the folder name.
            force: Overwrite existing folder.
            **kwargs: Additional arguments to pass to WorkspaceFolder.

        Returns:
            WorkspaceFolder: The created folder (deepest nested folder if nested).
        """
        from wa.utils import append_timestamp_to_name_or_path

        if append_timestamp:
            name_or_path = append_timestamp_to_name_or_path(name_or_path)

        # Build WorkspaceFolder from name_or_path
        if isinstance(name_or_path, str):
            workspace_folder = WorkspaceFolder(name=name_or_path, **kwargs)
        elif isinstance(name_or_path, Path):
            relative_path = self.path / name_or_path
            workspace_folder = WorkspaceFolder(name=str(relative_path), **kwargs)
        elif isinstance(name_or_path, list):
            folder_names = name_or_path.copy()
            folder_names.reverse()

            for index, name in enumerate(folder_names):
                if index == 0:
                    workspace_folder = WorkspaceFolder(name=name, **kwargs)
                else:
                    folders = {
                        workspace_folder.name: workspace_folder,
                    }
                    workspace_folder = WorkspaceFolder(
                        name=name, folders=folders, **kwargs
                    )

        # Initialize folder logic
        # Check if this top-level folder already exists
        if workspace_folder.name in self.folders:
            existing = self.folders[workspace_folder.name]
            # Merge the new subfolders into the existing subfolder
            self._merge_folders(existing, workspace_folder, force=force)
        else:
            workspace_folder.path = self.path / workspace_folder.name
            workspace_folder.initialize(force=force)
            self.folders[workspace_folder.name] = workspace_folder

        self.save()

        # Return the deepest nested path
        return self._get_deepest_folder(workspace_folder)

    def save(self, path: Path | None = None) -> Path:
        """
        Save the configuration to a YAML file.
        If no path is given, saves to '<workspace.path>/workspace.json'.
        """
        if path is None:
            path = self.path / self.config_file

        path.parent.mkdir(parents=True, exist_ok=True)
        _ = path.write_text(self.model_dump_json(indent=2))

        return path

    @classmethod
    def load(cls: type["Workspace"], path: Path) -> "Workspace":
        if not path.exists():
            raise FileNotFoundError(f"Workspace file not found at {path}")

        return cls.model_validate_json(path.read_text())
