from pathlib import Path
from typing import List, Union

PathLike = Union[str, Path]


def create_directory(path: PathLike) -> str:
    """Create `path` (and parents) if needed and return its absolute path."""
    path = Path(path)
    path.mkdir(parents=True, exist_ok=True)
    return str(path.resolve())


def check_existing_file(path: PathLike) -> bool:
    return Path(path).is_file()


def find_config_files(path: PathLike) -> List[Path]:
    """Return the experiment YAML files at `path`.

    `path` may be a single YAML file or a folder; folders are scanned (non
    recursively) for `*.yaml` / `*.yml` and the result is sorted.
    """
    path = Path(path)
    if path.is_file():
        return [path]
    if not path.is_dir():
        raise FileNotFoundError(f"Config path not found: {path}")

    files = sorted(
        p for p in path.iterdir() if p.is_file() and p.suffix.lower() in (".yaml", ".yml")
    )
    if not files:
        raise FileNotFoundError(f"No .yaml/.yml experiment files found in: {path}")
    return files
