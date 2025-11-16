from __future__ import annotations

import re

from pathlib import Path
from pydantic import BaseModel, Field, field_validator, model_validator

from . import __version__
from .utils import get_project_root


class WorkspaceSubfolder(BaseModel):
    name: str
    path: Path = Path("")
    subfolders: dict[str, WorkspaceSubfolder] = {}

    @field_validator("name", mode="before")
    @classmethod
    def normalize_and_sanitize_name(cls, v: str) -> str:
        v = v.replace(" ", "_")
        v = re.sub(r'[<>:"/\\|?*\x00-\x1F]', "", v)
        return v[:255]

    @field_validator("subfolders", mode="before")
    @classmethod
    def convert_list_to_dict(cls, v):
        """Convert list of WorkspaceSubfolder objects to dict keyed by name."""
        if isinstance(v, list):
            result = {}
            for subfolder in v:
                if isinstance(subfolder, WorkspaceSubfolder):
                    result[subfolder.name] = subfolder
                elif isinstance(subfolder, dict):
                    result[subfolder["name"]] = subfolder
            return result
        return v

    def initialize(self, force: bool = False):
        self.path.mkdir(exist_ok=force)
        for name, subfolder in self.subfolders.items():
            subfolder.path = self.path / name
            subfolder.initialize(force=force)


class Workspace(BaseModel):
    """
    Metadata for workspace.
    """

    name: str
    version: str = Field(default_factory=lambda: __version__)
    path: Path = Path("")
    workspaces_folder_path: Path = Path("")
    subfolders: dict[str, WorkspaceSubfolder] = {}
    config_file: str = "workspace.json"

    @field_validator("name", mode="before")
    @classmethod
    def normalize_and_sanitize_name(cls, v: str) -> str:
        v = v.replace(" ", "_")
        v = re.sub(r'[<>:"/\\|?*\x00-\x1F]', "", v)
        return v[:255]

    @field_validator("subfolders", mode="before")
    @classmethod
    def convert_list_to_dict(cls, v):
        """Convert list of WorkspaceSubfolder objects to dict keyed by name."""
        if isinstance(v, list):
            result = {}
            for subfolder in v:
                if isinstance(subfolder, WorkspaceSubfolder):
                    result[subfolder.name] = subfolder
                elif isinstance(subfolder, dict):
                    result[subfolder["name"]] = subfolder
            return result
        return v

    @model_validator(mode="after")
    def populate_missing_paths(self) -> "Workspace":
        if not self.workspaces_folder_path:
            self.workspaces_folder_path = get_project_root() / "workspaces"

        if self.path == Path(""):
            self.path = self.workspaces_folder_path / self.name

        return self

    def _merge_subfolders(
        self,
        existing: WorkspaceSubfolder,
        new: WorkspaceSubfolder,
        force: bool = False,
    ) -> None:
        """
        Recursively merge new subfolder structure into existing subfolder.

        Args:
            existing: The existing WorkspaceSubfolder to merge into.
            new: The new WorkspaceSubfolder to merge from.
            force: Whether to overwrite existing folders.
        """
        # Merge the nested subfolders from new into existing
        for name, new_nested in new.subfolders.items():
            if name in existing.subfolders:
                # Recursively merge if nested subfolder already exists
                self._merge_subfolders(
                    existing.subfolders[name], new_nested, force=force
                )
            else:
                # Add the new nested subfolder
                new_nested.path = existing.path / name
                new_nested.initialize(force=force)
                existing.subfolders[name] = new_nested

    def initialize_subfolder(
        self,
        subfolder: WorkspaceSubfolder,
        force: bool = False,
    ) -> Path:
        """
        Assigns path to subfolder and initializes subfolder inside workspace.
        If a subfolder with the same name already exists, merges the nested subfolders.

        Args:
            subfolder: Workspace subfolder object.
            force: Overwrite existing subfolder.

        Returns:
            Path: The path of the created subfolder (deepest nested path if nested).
        """
        # Check if this top-level subfolder already exists
        if subfolder.name in self.subfolders:
            existing = self.subfolders[subfolder.name]
            # Merge the new subfolders into the existing subfolder
            self._merge_subfolders(existing, subfolder, force=force)
            subfolder = existing
        else:
            subfolder.path = self.path / subfolder.name
            subfolder.initialize(force=force)
            self.subfolders[subfolder.name] = subfolder

        self.save()

        # Return the deepest nested path
        def get_deepest_path(sf: WorkspaceSubfolder) -> Path:
            if sf.subfolders:
                # Get the first (and should be only) nested subfolder
                nested = next(iter(sf.subfolders.values()))
                return get_deepest_path(nested)
            return sf.path

        return get_deepest_path(subfolder)

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
