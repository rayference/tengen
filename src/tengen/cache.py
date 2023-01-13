"""Cache module."""
import os
import pathlib
import shutil
import typing as t

# cache directory
TENGEN_CACHE_DIR = os.environ.get(
    "TENGEN_CACHE_DIR",
    pathlib.Path.home() / ".tengen",
)

# raw data directory
RAW_DATA_DIR = TENGEN_CACHE_DIR / "raw"

# formatted data directory
FORMATTED_DATA_DIR = TENGEN_CACHE_DIR / "formatted"


def init_cache() -> None:
    """Initialise cache."""
    TENGEN_CACHE_DIR.mkdir(parents=True, exist_ok=True)
    RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)
    FORMATTED_DATA_DIR.mkdir(parents=True, exist_ok=True)


def list_cache_content() -> t.List[str]:
    """List cache content."""
    return [file.name for file in TENGEN_CACHE_DIR.glob("*.nc")]


def remove_cache() -> None:
    """Remove the cache."""
    try:
        shutil.rmtree(TENGEN_CACHE_DIR)
    except OSError as e:
        raise ValueError(f"Could not remove cache at {TENGEN_CACHE_DIR}") from e
