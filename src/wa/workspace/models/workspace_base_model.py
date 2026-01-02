from __future__ import annotations

from pathlib import Path
from pydantic import BaseModel, Field, field_validator

from wa import __version__
from wa.utils import create_pathname


class WorkspaceBaseModel(BaseModel):
    name: str
    path: Path = Path("")
    folders: dict[str, "WorkspaceFolder"] = {}
    files: list[str] = Field(default_factory=list)

    @field_validator("name", mode="before")
    @classmethod
    def normalize_and_sanitize_name(cls, name: str) -> str:
        return create_pathname(name)

    @field_validator("folders", mode="before")
    @classmethod
    def parse_folders(cls, v):
        """Convert list of WorkspaceFolder objects to dict keyed by name."""
        from .workspace_folder import WorkspaceFolder

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
