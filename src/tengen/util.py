import datetime
import typing as t

import numpy as np
import pandas as pd
import pint
import xarray as xr

from . import __version__

# CF Standard Name Table Version 77, 19 January 2021
_SSI_ATTRS = {
    "standard_name": "solar_irradiance_per_unit_wavelength",
    "long_name": "solar spectral irradiance",
    "units": "W/m^2/nm",
}

_W_ATTRS = {
    "standard_name": "radiation_wavelength",
    "long_name": "wavelength",
    "units": "nm",
}

_T_ATTRS = {"standard_name": "time", "long_name": "time"}


def to_data_set(
    ssi: pint.Quantity,
    w: pint.Quantity,
    url: str,
    t: t.Optional[pd.DatetimeIndex] = None,
    attrs: t.Optional[t.MutableMapping[str, str]] = None,
) -> xr.Dataset:
    """Make a data set from variables values.

    Parameters
    ----------
    ssi: :class:`~pint.Quantity`
        Solar spectral irradiance.

    w: :class:`~pint.Quantity`
        Wavelength.

    url: str
        URL.

    t: :class:`~pandas.DatetimeIndex`, optional
        Time stamps.

    attrs: dict, optional
        Attributes.

    Returns
    -------
    :class:`~xarray.Dataset`
        Solar irradiance spectrum data set.
    """
    coords: t.Dict[t.Hashable, t.Any] = {"w": ("w", w.m_as("nm"), _W_ATTRS)}

    if t is not None:
        coords["t"] = ("t", t, _T_ATTRS)
        data_vars: t.Dict[t.Hashable, t.Any] = {"ssi": (("t", "w"), ssi, _SSI_ATTRS)}
    else:
        coords["t"] = ("t", np.empty(0), _T_ATTRS)
        data_vars = {"ssi": ("w", ssi.m_as("W/m^2/nm"), _SSI_ATTRS)}

    utcnow = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

    if attrs is None:
        attrs = dict(
            Conventions="CF-1.8",
            title="unknown",
            institution="unknown",
            source="unknown",
            references="unknown",
        )

    attrs["history"] = f"{utcnow} - data set creation - tengen, version {__version__}"

    attrs["url"] = f"original data available at {url} (last accessed on {utcnow})"

    ds = xr.Dataset(data_vars=data_vars, coords=coords, attrs=attrs)

    # The time units cannot be added in 'attrs'
    # see https://github.com/pydata/xarray/issues/1324
    # Instead, we add it to 'encoding'
    if t is not None:
        ds.t.encoding["units"] = f"days since {str(t[0].date())}"

    return ds
