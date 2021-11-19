import pathlib
import shutil

CACHE_DIR = pathlib.Path(".tengen_cache")


def init_cache():
    """
    Initialise cache.
    """
    CACHE_DIR.mkdir(parents=True, exist_ok=True)


def list_cache_content():
    """
    List cache content.
    """
    return [file.name for file in CACHE_DIR.glob("*.nc")]


def remove_cache():  # pragma: no cover
    """
    Remove the cache.
    """
    try:
        shutil.rmtree(CACHE_DIR)
    except OSError as e:
        raise ValueError(f"Could not remove cache at {CACHE_DIR}") from e
