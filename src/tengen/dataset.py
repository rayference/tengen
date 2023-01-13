"""Utility module."""
from datetime import datetime
import typing as t

import numpy as np
import pandas as pd
import pint
import xarray as xr

from .__version__ import __version__

# CF Standard Name Table Version 77, 19 January 2021
ATTRS = {
    "ssi": {
        "standard_name": "solar_irradiance_per_unit_wavelength",
        "long_name": "solar spectral irradiance",
        "units": "W/m^2/nm",
    },
    "w": {
        "standard_name": "radiation_wavelength",
        "long_name": "wavelength",
        "units": "nm",
    },
    "t": {
        "standard_name": "time",
        "long_name": "time",
    },
}


def to_dataset(
    ssi: pint.Quantity,
    w: pint.Quantity,
    data_url: str,
    t: t.Optional[pd.DatetimeIndex] = None,
    attrs: t.Optional[t.Dict[str, str]] = None,
) -> xr.Dataset:
    """Make a data set from variables values.

    Args:
        ssi: solar spectral irradiance.
        w: radiation wavelength.
        data_url: raw data url.
        t: time stamps.
        attrs: dataset attributes.

    Returns:
        Solar irradiance spectrum data set.
    """
    # Prepare data coordinates and variables
    coords = {"w": ("w", w.m_as(ATTRS["w"]["units"]), ATTRS["w"])}

    if t is not None:
        coords["t"] = ("t", t, ATTRS["t"])
        data_vars = {
            "ssi": (("t", "w"), ssi.m_as(ATTRS["ssi"]["units"]), ATTRS["ssi"]),
        }
    else:
        coords["t"] = ("t", np.empty(0), ATTRS["t"])
        data_vars = {
            "ssi": ("w", ssi.m_as(ATTRS["ssi"]["units"]), ATTRS["ssi"]),
        }

    # Prepare attributes
    utcnow = datetime.utcnow().replace(microsecond=0).isoformat()

    _attrs = dict(
        Conventions="CF-1.10",
        title="unknown",
        institution="unknown",
        source="unknown",
        references="unknown",
    )

    if attrs is not None:
        _attrs.update(attrs)

    author = f"tengen, version {__version__}"
    _attrs.update(
        {
            "history": f"{utcnow} - data set creation by {author}",
            "data_url": data_url,
            "data_url_datetime": utcnow,
        }
    )

    # Create data set
    ds = xr.Dataset(
        data_vars=data_vars,
        coords=coords,
        attrs=_attrs,
    )

    # The time units cannot be added in 'attrs'
    # see https://github.com/pydata/xarray/issues/1324
    # Instead, we add it to 'encoding'
    if t is not None:
        ds.t.encoding["units"] = f"days since {str(t[0].date())}"

    return ds
