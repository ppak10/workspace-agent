import shutil
import subprocess

from importlib.resources import files
from pathlib import Path
from rich import print as rprint

from wa import data


def install(path: Path, client: str, include_agent: bool = True) -> None:
    match client:
        case "claude-code":
            cmd = [
                "claude",
                "mcp",
                "add-json",
                "workspace",
                f'{{"command": "uv", "args": ["--directory", "{path}", "run", "-m", "wa.mcp"]}}',
            ]

            if include_agent:
                # Copies premade agent configuration to `.claude/agents`
                agent_file = files(data) / "mcp" / "agent.md"
                claude_agents_path = path / ".claude" / "agents"
                claude_agents_path.mkdir(parents=True, exist_ok=True)
                claude_agent_config_path = claude_agents_path / "workspace.md"
                with (
                    agent_file.open("rb") as src,
                    open(claude_agent_config_path, "wb") as dst,
                ):
                    shutil.copyfileobj(src, dst)
                rprint(
                    f"[bold green]Installed agent under path:[/bold green] {claude_agent_config_path}"
                )

        case "gemini-cli":
            cmd = [
                "gemini",
                "mcp",
                "add",
                "workspace",
                "uv",
                "--directory",
                f"{path}",
                "run",
                "-m",
                "wa.mcp",
            ]

        case "codex":
            cmd = [
                "codex",
                "mcp",
                "add",
                "workspace",
                "uv",
                "--directory",
                f"{path}",
                "run",
                "-m",
                "wa.mcp",
            ]

        case _:
            rprint(
                "[yellow]No client provided.[/yellow]\n"
                "[bold]Please specify where to install with one of the following:[/bold]\n"
                "  • [green]--client claude-code[/green] to install for Claude Code\n"
                "  • Other options coming soon..."
            )

    try:
        rprint(f"[blue]Running command:[/blue] {' '.join(cmd)}")
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        rprint(f"[red]Command failed with return code {e.returncode}[/red]")
        rprint(f"[red]Error output: {e.stderr}[/red]" if e.stderr else "")
    except Exception as e:
        rprint(f"[red]Unexpected error running command:[/red] {e}")
