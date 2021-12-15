"""Test cases for the resources module."""
import typing as t

import pytest
import requests
import xarray as xr

from tengen.resources import Coddington2021Resolution
from tengen.resources import coddington_2021_url
from tengen.resources import THUILLIER_2003_URL
from tengen.resources import transform_coddington_2021
from tengen.resources import transform_thuillier_2003
from tengen.resources import Resource
from tengen.cache import remove_cache, init_cache, list_cache_content


@pytest.fixture
def test_resource() -> Resource:
    """Resource fixture."""

    def transform(url: str):
        r = requests.get(url)
        return xr.Dataset()

    return Resource(
        name="test_resource",
        url="https://github.com/nollety/tengen.git",
        transform=transform,
    )


def test_resource_fetch_from_web(test_resource: Resource) -> None:
    """Returns a Dataset."""
    ds = test_resource.fetch_from_web()
    ds.close()
    assert isinstance(ds, xr.Dataset)


def test_resource_fetch_from_web_writes_to_cache(test_resource: Resource) -> None:
    """Dataset is written to cache."""
    remove_cache()
    init_cache()
    ds = test_resource.fetch_from_web()
    ds.close()
    assert test_resource.in_cache


def test_resource_fetch_from_cache(test_resource: Resource) -> None:
    """Returns a Dataset."""
    ds = test_resource.fetch_from_web()  # populate the cache
    ds.close()
    ds = test_resource.fetch_from_cache()
    ds.close()
    assert isinstance(ds, xr.Dataset)


def test_resource_fetch_from_cache_raise(test_resource: Resource) -> None:
    """Raises when dataset is not in cache."""
    remove_cache()  # cache is empty
    init_cache()
    with pytest.raises(ValueError):
        test_resource.fetch_from_cache()


class MockConnectionError:
    """ConnectionError mock."""

    def __init__(self, *args: t.Any, **kwargs: t.Any) -> None:
        raise requests.exceptions.ConnectionError


def test_resources_get_connection_error_in_cache(
    monkeypatch: pytest.MonkeyPatch, test_resource: Resource
) -> None:
    """ """
    ds = test_resource.fetch_from_web()  # populate cache
    ds.close()
    monkeypatch.setattr("requests.get", MockConnectionError)
    ds = test_resource.get()
    ds.close()
    assert isinstance(ds, xr.Dataset)


def test_transform_thuillier_2003() -> None:
    """Returns a Dataset."""
    ds = transform_thuillier_2003(url=THUILLIER_2003_URL)
    ds.close()
    assert isinstance(ds, xr.Dataset)


@pytest.mark.parametrize("resolution", [x for x in Coddington2021Resolution])
def test_coddington_2021_url(resolution: Coddington2021Resolution) -> None:
    """Returns a str."""
    assert isinstance(coddington_2021_url(resolution), str)


@pytest.mark.parametrize(
    "url", [coddington_2021_url(x) for x in Coddington2021Resolution]
)
def test_transform_coddington_2021(url: str) -> None:
    """Returns a Dataset."""
    ds = transform_coddington_2021(url=url)
    ds.close()
    assert isinstance(ds, xr.Dataset)
