from json import loads
from pathlib import Path


def read_file_to_json(path: Path) -> dict:
    """Read a file and parse it as JSON."""
    with open(path) as f:
        data = loads(f.read())
        return data["abi"] if isinstance(data, dict) and "abi" in data else data
