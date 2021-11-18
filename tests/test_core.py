"""Test cases for the core module."""
import datetime

import numpy as np
import pandas as pd
import pytest
import xarray as xr

from tengen.core import make, make_data_set


def test_make() -> None:
    """Returns a xr.Dataset."""
    print("hello from test_make")
    for identifier in ["thuillier_2003", "coddington_2021"]:
        ds = make(identifier=identifier)
        assert isinstance(ds, xr.Dataset)


def test_make_raises() -> None:
    """Raises a ValueError when the identifier is unknown."""
    with pytest.raises(ValueError):
        make(identifier="unknown")


def test_make_data_set() -> None:
    """Returns a data set."""
    ds = make_data_set(
        w=np.linspace(1, 2),
        ssi=np.random.random(50),
        title="test",
        institution="test",
        source="test",
        history="test",
        references="test",
    )
    assert isinstance(ds, xr.Dataset)


def test_make_data_set_t_not_none() -> None:
    """Returns a data set when t is not None."""
    ds = make_data_set(
        w=np.linspace(1, 2),
        ssi=np.random.random((31, 50)),
        t=pd.date_range(
            start=datetime.date(2021, 1, 1), end=datetime.date(2021, 1, 31)
        ),
        title="test",
        institution="test",
        source="test",
        history="test",
        references="test",
    )
    assert isinstance(ds, xr.Dataset)


def test_make_data_set_comment_not_none() -> None:
    """Returns a data set when comment is not None."""
    ds = make_data_set(
        w=np.linspace(1, 2),
        ssi=np.random.random(50),
        title="test",
        institution="test",
        source="test",
        history="test",
        references="test",
        comment="test",
    )
    assert isinstance(ds, xr.Dataset)


def test_make_data_set_url_info_not_none() -> None:
    """Returns a data set when url_info is not None."""
    ds = make_data_set(
        w=np.linspace(1, 2),
        ssi=np.random.random(50),
        title="test",
        institution="test",
        source="test",
        history="test",
        references="test",
        url_info=("test", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
    )
    assert isinstance(ds, xr.Dataset)
