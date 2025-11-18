from __future__ import annotations

from pathlib import Path
from pydantic import BaseModel, Field, field_validator, model_validator

from . import __version__
from .utils import get_project_root

from wa.utils import create_pathname


class WorkspaceModel(BaseModel):
    name: str
    path: Path = Path("")
    folders: dict[str, WorkspaceFolder] = {}
    files: list[str] = Field(default_factory=list)

    @field_validator("name", mode="before")
    @classmethod
    def normalize_and_sanitize_name(cls, name: str) -> str:
        return create_pathname(name)

    @field_validator("folders", mode="before")
    @classmethod
    def parse_folders(cls, v):
        """Convert list of WorkspaceFolder objects to dict keyed by name."""
        if isinstance(v, dict):
            return v

        if isinstance(v, list):
            result = {}
            for folder in v:
                if isinstance(folder, WorkspaceFolder):
                    result[folder.name] = folder
                elif isinstance(folder, dict):
                    result[folder["name"]] = folder
                elif isinstance(folder, str):
                    result[folder] = WorkspaceFolder(name=folder)
            return result

        else:
            return {}


class WorkspaceFolder(WorkspaceModel):
    """
    Recursive Folder class.
    """

    def initialize(self, force: bool = False):
        self.path.mkdir(exist_ok=force)
        for name, folder in self.folders.items():
            folder.path = self.path / name
            folder.initialize(force=force)


class Workspace(WorkspaceModel):
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

    def initialize_folder(
        self,
        folder: WorkspaceFolder,
        force: bool = False,
    ) -> WorkspaceFolder:
        """
        Assigns path to folder and initializes folder inside workspace.
        If a folder with the same name already exists, merges the nested folders.

        Args:
            folder: Workspace folder object.
            force: Overwrite existing folder.

        Returns:
            Path: The path of the created folder (deepest nested path if nested).
        """
        # Check if this top-level folder already exists
        if folder.name in self.folders:
            existing = self.folders[folder.name]
            # Merge the new subfolders into the existing subfolder
            self._merge_folders(existing, folder, force=force)
        else:
            folder.path = self.path / folder.name
            folder.initialize(force=force)
            self.folders[folder.name] = folder

        self.save()

        # Return the deepest nested path
        def get_deepest_folder(folder: WorkspaceFolder) -> WorkspaceFolder:
            if folder.folders:
                # Get the first (and should be only) nested subfolder
                nested = next(iter(folder.folders.values()))
                return get_deepest_folder(nested)
            return folder

        return get_deepest_folder(folder)

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
