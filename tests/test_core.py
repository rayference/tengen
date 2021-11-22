"""Test cases for the core module."""
import pytest
import xarray as xr

from tengen.core import make


def test_make() -> None:
    """Returns a xr.Dataset."""
    for identifier in ["thuillier_2003", "coddington_2021-high_resolution"]:
        ds = make(identifier=identifier)
        assert isinstance(ds, xr.Dataset)


def test_make_raises() -> None:
    """Raises a ValueError when the identifier is unknown."""
    with pytest.raises(KeyError):
        make(identifier="unknown")
