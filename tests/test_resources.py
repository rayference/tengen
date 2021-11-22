"""Test cases for the resources module."""
import pytest
import xarray as xr

from tengen.resources import Coddington2021Resolution
from tengen.resources import coddington_2021_url
from tengen.resources import THUILLIER_2003_URL
from tengen.resources import transform_coddington_2021
from tengen.resources import transform_thuillier_2003


def test_transform_thuillier_2003() -> None:
    """Returns a Dataset."""
    ds = transform_thuillier_2003(url=THUILLIER_2003_URL)
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
    assert isinstance(ds, xr.Dataset)
