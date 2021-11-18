import typing as t

import numpy as np
import pandas as pd
import xarray as xr

from .units import ureg

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


@ureg.wraps(
    ret=None,
    args=("nm", "W * m^-2 * nm^-1", None, None, None, None, None, None, None, None),
    strict=False,
)
def make_data_set(
    w: t.Union[ureg.Quantity, np.ndarray],
    ssi: t.Union[ureg.Quantity, np.ndarray],
    title: str,
    institution: str,
    source: str,
    history: str,
    references: str,
    comment: t.Optional[str] = None,
    url_info: t.Optional[t.Tuple[str, str]] = None,
    t: t.Optional[pd.DatetimeIndex] = None,
) -> xr.Dataset:
    """Make a data set from variables values.

    Parameters
    ----------
    w: :class:`~pint.Quantity` or :class:`~numpy.ndarray`
        Wavelength [nm].

    ssi: :class:`~pint.Quantity` or :class:`~numpy.ndarray`
        Solar spectral irradiance [W/m^2/s].

    title: str
        Dataset title.

    institution: str
        Where the original data was produced.

    source: str
        The method of production of the original data.

    history: str
        Audit trail for modifications to the original data.

    references: str
        Published or web-based references that describe the data or methods
        used to produce it.

    comment: str, optional
        Comment.

    url_info: tuple of str, optional
        URL where the data is freely available, last accessed date.
        Provide the date in the format: ``yyyy-mm-dd``, e.g. ``2020-07-31``.

    t: :class:`~pandas.DatetimeIndex`, optional
        Time stamps [days].

    Returns
    -------
    :class:`~xarray.Dataset`
        Solar irradiance spectrum data set.
    """
    coords: t.Dict[t.Hashable, t.Any] = {"w": ("w", w, _W_ATTRS)}

    if t is not None:
        coords["t"] = ("t", t, _T_ATTRS)
        data_vars: t.Dict[t.Hashable, t.Any] = {"ssi": (("t", "w"), ssi, _SSI_ATTRS)}
    else:
        coords["t"] = ("t", np.empty(0), _T_ATTRS)
        data_vars = {"ssi": ("w", ssi, _SSI_ATTRS)}

    attrs: t.Dict[t.Hashable, t.Any] = dict(
        Conventions="CF-1.8",
        title=title,
        institution=institution,
        source=source,
        history=history,
        references=references,
    )

    if comment is not None:
        attrs["comment"] = comment

    if url_info is not None:
        url, date = url_info
        attrs["url"] = f"original data available at {url} (last accessed on {date})"

    ds = xr.Dataset(data_vars=data_vars, coords=coords, attrs=attrs)

    # The time units cannot be added in 'attrs'
    # see https://github.com/pydata/xarray/issues/1324
    # Instead, we add it to 'encoding'
    if t is not None:
        ds.t.encoding["units"] = f"days since {str(t[0].date())}"

    return ds
