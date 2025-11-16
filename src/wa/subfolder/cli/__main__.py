import typer

app = typer.Typer(
    name="subfolder",
    help="Manage workspace subfolders",
    add_completion=False,
    no_args_is_help=True,
)
