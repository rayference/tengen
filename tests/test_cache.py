"""Test cases for the cache module."""
from tengen.cache import CACHE_DIR
from tengen.cache import init_cache
from tengen.cache import list_cache_content


def test_init_cache() -> None:
    """Cache directory exists after 'init_cache' is called."""
    init_cache()
    assert CACHE_DIR.exists()


def test_list_cache_content() -> None:
    """Returns a list of str."""
    assert isinstance(list_cache_content(), list)
    assert all([isinstance(x, str) for x in list_cache_content()])
