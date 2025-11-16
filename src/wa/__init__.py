from importlib.metadata import version, PackageNotFoundError

__author__: str = "Peter Pak"
__email__: str = "ppak10@gmail.com"
__version__: str

try:
    __version__ = version("workspace-agent")
except PackageNotFoundError:
    __version__ = "unknown"
