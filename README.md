[![claude-code](https://github.com/ppak10/workspace-agent/actions/workflows/claude-code.yml/badge.svg)](https://github.com/ppak10/workspace-agent/actions/workflows/claude-code.yml)
[![gemini-cli](https://github.com/ppak10/workspace-agent/actions/workflows/gemini-cli.yml/badge.svg)](https://github.com/ppak10/workspace-agent/actions/workflows/gemini-cli.yml)
[![codex](https://github.com/ppak10/workspace-agent/actions/workflows/codex.yml/badge.svg)](https://github.com/ppak10/workspace-agent/actions/workflows/codex.yml)
[![pytest](https://github.com/ppak10/workspace-agent/actions/workflows/pytest.yml/badge.svg)](https://github.com/ppak10/workspace-agent/actions/workflows/pytest.yml)
[![codecov](https://codecov.io/github/ppak10/workspace-agent/graph/badge.svg?token=BJBTFCWMR4)](https://codecov.io/github/ppak10/workspace-agent)

# workspace-agent

 Workspace management package for `workspaces` folder shared between different packages.

<p align="center">
  <img src="./icon.svg" alt="Logo" width="50%">
</p>

## Getting Started
### Installation
```bash
uv add workspace-agent 
```

## Usage
### Command Line Interface (CLI)
1. Create Workspace (along with folders and subfolders)
```bash
> workspace create test-workspace

# Expected Output
✅ Workspace created at: /Users/ppak/GitHub/workspace-agent/workspaces/test-workspace

> workspace create test-workspace test-folder

# Expected Output
✅ Workspace folder created at: /Users/ppak/GitHub/workspace-agent/workspaces/test-workspace/test-folder

> workspace create test-workspace test-folder test-subfolder

# Expected Output
✅ Workspace folder created at: /Users/ppak/GitHub/workspace-agent/workspaces/test-workspace/test-folder/test-subfolder
```

2. Read Workspace
```bash
> workspace read test-workspace

# Expected Output
Workspace(
    name='test-workspace',
    path=PosixPath('/Users/ppak/GitHub/workspace-agent/workspaces/test-workspace'),
    folders={
        'test-folder': WorkspaceFolder(
            name='test-folder',
            path=PosixPath('/Users/ppak/GitHub/workspace-agent/workspaces/test-workspace/test-folder'),
            folders={'test-subfolder': WorkspaceFolder(name='test-subfolder', path=PosixPath('/Users/ppak/GitHub/workspace-agent/workspaces/test-workspace/test-folder/test-subfolder'), folders={}, files=[])},
            files=[]
        )
    },
    version='0.0.2',
    workspaces_path=PosixPath('/Users/ppak/GitHub/workspace-agent/workspaces'),
    config_file='workspace.json'
)

> workspace read test-workspace test-folder

# Expected Output
WorkspaceFolder(
    name='test-folder',
    path=PosixPath('/Users/ppak/GitHub/workspace-agent/workspaces/test-workspace/test-folder'),
    folders={'test-subfolder': WorkspaceFolder(name='test-subfolder', path=PosixPath('/Users/ppak/GitHub/workspace-agent/workspaces/test-workspace/test-folder/test-subfolder'), folders={}, files=[])},
    files=[]
)

> workspace read test-workspace test-folder test-subfolder

# Expected Output
WorkspaceFolder(name='test-subfolder', path=PosixPath('/Users/ppak/GitHub/workspace-agent/workspaces/test-workspace/test-folder/test-subfolder'), folders={}, files=[])
```

### Model Context Protocol (MCP)
1. Install MCP tools and Agent (defaults to `claude-code`)
```bash
> workspace mcp install
```

- Explicit methods include `claude-code`, `codex`, and `gemini-cli`
  ```bash
  > workspace mcp install claude-code
  > workspace mcp install codex
  > workspace mcp install gemini-cli 
  ```

- If updating, you will need to remove the previously existing MCP tools
  ```bash
  > workspace mcp uninstall claude-code
  > workspace mcp uninstall codex
  > workspace mcp uninstall gemini-cli 
  ```
