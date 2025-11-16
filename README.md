[![pytest](https://github.com/ppak10/workspace-agent/actions/workflows/pytest.yml/badge.svg)](https://github.com/ppak10/workspace-agent/actions/workflows/pytest.yml)
[![Claude Code](https://github.com/ppak10/workspace-agent/actions/workflows/claude-code.yml/badge.svg)](https://github.com/ppak10/workspace-agent/actions/workflows/claude-code.yml)
[![codecov](https://codecov.io/github/ppak10/workspace-agent/graph/badge.svg?token=BJBTFCWMR4)](https://codecov.io/github/ppak10/workspace-agent)

# workspace-agent

 Workspace management package for `out` folder shared between different packages.

<p align="center">
  <img src="./icon.svg" alt="Logo" width="50%">
</p>

## Getting Started
### Installation
```bash
uv add workspace-agent 
```

### Agent
#### Claude Code
1. Install MCP tools and Agent
```bash
workspace mcp install
```

- Defaults to claude code but other options include `codex` and `gemini-cli`
```bash
workspace mcp install --client claude-code
workspace mcp install --client codex
workspace mcp install --client gemini-cli 
```

- If updating, you will need to remove the previously existing MCP tools
```bash
workspace mcp uninstall
```

```bash
workspace mcp uninstall --client claude-code
workspace mcp uninstall --client codex
workspace mcp uninstall --client gemini-cli 
```
