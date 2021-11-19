"""Tengen."""
__version__ = "0.1.1"

from .cache import init_cache
from .core import make

__all__ = ["make", "__version__"]

init_cache()
