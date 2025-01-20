from json import loads
from pathlib import Path
from typing import Any


def read_file_to_json(path: Path) -> dict[Any, Any]:
    """Read a file and parse it as JSON."""
    with open(path) as f:
        data = loads(f.read())
        return data["abi"] if isinstance(data, dict) and "abi" in data else {}
