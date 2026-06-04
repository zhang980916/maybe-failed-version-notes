from __future__ import annotations

import os
from pathlib import Path


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def data_dir() -> Path:
    """Return the writable data directory.

    ASRL_DATA_DIR can point to a private local data folder. When unset, demo
    commands write to ./data, which is intentionally gitignored.
    """
    return Path(os.environ.get("ASRL_DATA_DIR", repo_root() / "data")).resolve()


def ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
