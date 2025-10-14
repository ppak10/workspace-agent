[![pytest](https://github.com/ppak10/workspace-agent/actions/workflows/pytest.yml/badge.svg)](https://github.com/ppak10/workspace-agent/actions/workflows/pytest.yml)
[![codecov](https://codecov.io/github/ppak10/workspace-agent/graph/badge.svg?token=BJBTFCWMR4)](https://codecov.io/github/ppak10/workspace-agent)

# workspace-agent

 Workspace management package for `out` folder shared between different packages.

<div style="display: flex; justify-content: center;">
  <img src="./icon.svg" alt="Logo" width="50%">
</div>

## Getting Started
### Installation
```bash
uv add workspace-agent 
```

### Agent
#### Claude Code
1. Install MCP tools and Agent
- Defaults to claude code
```bash
wa mcp install
```

- If updating, you will need to remove the previously existing MCP tools
```bash
claude mcp remove wa
```
