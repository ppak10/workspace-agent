"""Shared pytest fixtures for workspace folder tests."""

import shutil
from pathlib import Path

import pytest

from wa.models import Workspace


@pytest.fixture
def temp_workspaces_path(tmp_path: Path) -> Path:
    """Create a temporary workspaces folder for testing."""
    workspaces_path = tmp_path / "workspaces"
    workspaces_path.mkdir(parents=True, exist_ok=True)
    return workspaces_path


@pytest.fixture
def sample_workspace_name() -> str:
    """Provide a sample workspace name for testing."""
    return "test_workspace"


@pytest.fixture
def sample_workspace(
    temp_workspaces_path: Path, sample_workspace_name: str
) -> Workspace:
    """Create a sample workspace for testing."""
    workspace = Workspace(
        name=sample_workspace_name,
        workspaces_folder_path=temp_workspaces_path,
    )
    workspace.save()
    return workspace


@pytest.fixture
def cleanup_workspace(temp_workspaces_path: Path):
    """Cleanup fixture to remove test workspaces after tests."""
    yield
    if temp_workspaces_path.exists():
        shutil.rmtree(temp_workspaces_path)
