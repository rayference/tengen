"""Test cases for the cache module."""

from tengen.cache import CACHE_DIR, init_cache, list_cache_content


def test_init_cache() -> None:
    init_cache()
    assert CACHE_DIR.exists()


def test_list_cache_content() -> None:
    assert isinstance(list_cache_content(), list)
