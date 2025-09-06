"""Tengen."""

import pint

from ._version import __version__
from .cache import (
    FORMATTED_DATA_DIR,
    RAW_DATA_DIR,
    init_cache,
    list_cache_content,
    remove_cache,
)
from .dataset import to_dataset

unit_registry = pint.UnitRegistry()

pint.set_application_registry(unit_registry)

__all__ = [
    "__version__",
    "init_cache",
    "unit_registry",
    "to_dataset",
    "list_cache_content",
    "remove_cache",
    "RAW_DATA_DIR",
    "FORMATTED_DATA_DIR",
]

init_cache()
