"""Test cases for the util module."""
import datetime

import numpy as np
import pandas as pd
import xarray as xr

from tengen.units import ureg
from tengen.dataset import to_dataset


def test_to_data_set() -> None:
    """Returns a data set."""
    ds = to_dataset(
        w=np.linspace(1, 2) * ureg.nm,
        ssi=np.random.random(50) * ureg.watt / ureg.m**2 / ureg.nm,
        url="imaginary url",
    )
    assert isinstance(ds, xr.Dataset)


def test_to_data_set_attrs() -> None:
    """Returns a data set."""
    ds = to_dataset(
        w=np.linspace(1, 2) * ureg.nm,
        ssi=np.random.random(50) * ureg.watt / ureg.m**2 / ureg.nm,
        url="imaginary url",
        attrs=dict(
            title="test",
            institution="test",
            source="test",
            history="test",
            references="test",
        ),
    )
    assert isinstance(ds, xr.Dataset)


def test_to_data_set_t_not_none() -> None:
    """Returns a data set when t is not None."""
    ds = to_dataset(
        w=np.linspace(1, 2) * ureg.nm,
        ssi=np.random.random((31, 50)) * ureg.watt / ureg.m**2 / ureg.nm,
        url="imaginary url",
        t=pd.date_range(
            start=datetime.date(2021, 1, 1), end=datetime.date(2021, 1, 31)
        ),
        attrs=dict(
            title="test",
            institution="test",
            source="test",
            history="test",
            references="test",
        ),
    )
    assert isinstance(ds, xr.Dataset)
