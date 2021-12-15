"""Test cases for the resources module."""
import typing as t

import pytest
import requests
import xarray as xr
from tengen.cache import init_cache, remove_cache
from tengen.resources import (
    MEFTAH_2018_URL,
    SOLID_2017_URL,
    THUILLIER_2003_URL,
    WHI_2008_URL,
    Coddington2021Resolution,
    Resource,
    coddington_2021_url,
    transform_coddington_2021,
    transform_meftah_2018,
    transform_solid_2017,
    transform_thuillier_2003,
    transform_whi_2008,
)


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
    """Fetch from cache if connection error."""
    ds = test_resource.fetch_from_web()  # populate cache
    ds.close()
    monkeypatch.setattr("requests.get", MockConnectionError)
    ds = test_resource.get()
    ds.close()
    assert isinstance(ds, xr.Dataset)


def test_resources_get_connection_error_not_in_cache(
    monkeypatch: pytest.MonkeyPatch, test_resource: Resource
) -> None:
    """Raises ValueError when dataset could not be fetched from web nor cache."""
    remove_cache()  # cache is empty
    init_cache()
    monkeypatch.setattr("requests.get", MockConnectionError)
    with pytest.raises(ValueError):
        test_resource.get()


# ------------------------------------------------------------------------------
#                                Thuillier (2003)
# ------------------------------------------------------------------------------


def test_transform_thuillier_2003() -> None:
    """Returns a Dataset."""
    ds = transform_thuillier_2003(url=THUILLIER_2003_URL)
    ds.close()
    assert isinstance(ds, xr.Dataset)


# ------------------------------------------------------------------------------
#                                WHI (2008)
# ------------------------------------------------------------------------------


def test_transform_whi_2008() -> None:
    """Returns a Dataset."""
    with transform_whi_2008(identifier="sunspot active")(url=WHI_2008_URL) as ds:
        assert isinstance(ds, xr.Dataset)


# ------------------------------------------------------------------------------
#                                Meftah (2017)
# ------------------------------------------------------------------------------


def test_transform_meftah_2018() -> None:
    """Returns a Dataset."""
    with transform_meftah_2018(url=MEFTAH_2018_URL) as ds:
        assert isinstance(ds, xr.Dataset)


# ------------------------------------------------------------------------------
#                                SOLID (2017)
# ------------------------------------------------------------------------------


@pytest.mark.slow
def test_transform_solid_2017() -> None:
    """Returns a Dataset."""
    with transform_solid_2017(url=SOLID_2017_URL) as ds:
        assert isinstance(ds, xr.Dataset)


# ------------------------------------------------------------------------------
#                                Coddington (2021)
# ------------------------------------------------------------------------------


@pytest.mark.parametrize("resolution", [x for x in Coddington2021Resolution])
def test_coddington_2021_url(resolution: Coddington2021Resolution) -> None:
    """Returns a str."""
    assert isinstance(coddington_2021_url(resolution), str)


@pytest.mark.slow
@pytest.mark.parametrize(
    "url", [coddington_2021_url(x) for x in Coddington2021Resolution]
)
def test_transform_coddington_2021(url: str) -> None:
    """Returns a Dataset."""
    ds = transform_coddington_2021(url=url)
    ds.close()
    assert isinstance(ds, xr.Dataset)
