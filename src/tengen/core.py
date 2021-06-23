"""Command-line interface."""
import datetime
import io
from typing import Any
from typing import Dict
from typing import Hashable
from typing import Optional
from typing import Tuple
from typing import Union

import numpy as np
import pandas as pd
import requests
import xarray as xr

from tengen import ureg


def make(identifier: str) -> xr.Dataset:
    """Make solar irradiance spectrum data set.

    Parameters
    ----------
    identifier: str,
        Data set identifier.

    Returns
    -------
    :class:`~xarray.Dataset`
        Solar irradiance spectrum.

    Raises
    ------
    ValueError:
        If ``identifier`` is unknown.
    """
    if identifier == "coddington_2021":
        url = (
            "https://lasp.colorado.edu/lisird/resources/lasp/hsrs/"
            "hybrid_reference_spectrum_c2021-03-04_with_unc.nc"
        )
        response = requests.get(url)
        return xr.open_dataset(io.BytesIO(response.content), engine="h5netcdf")  # type: ignore
    elif identifier == "thuillier_2003":
        # alternative url:
        # "media.libsyn.com/media/npl1/Solar_irradiance_Thuillier_2002.xls"
        url = "https://oceancolor.gsfc.nasa.gov/docs/rsr/f0.txt"
        response = requests.get(url)
        data = np.loadtxt(io.BytesIO(response.content), comments=["/", "!"])
        wavelength_values = data[:, 0]
        spectral_irradiance_values = ureg.Quantity(data[:, 1], "microwatt/cm^2/nm")
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        return make_data_set(  # type: ignore
            w=wavelength_values,
            ssi=spectral_irradiance_values,
            title="Thuillier (2003) solar irradiance spectrum",
            institution="Service d'Aéronomie du CNRS, F91371, "
            "Verrières-le-Buisson, France.",
            source="Combined observations from the SOLSPEC instrument during "
            "the ATLAS-1 "
            "mission (from 1992-03-24 to 1992-04-02) and the SOSP "
            "instrument onboard the EURECA satellite (from 1992-8-7 to "
            "1993-7-1), with the Kurucz and Bell (1995) synthetic "
            "spectrum",
            history=f"{now} - data set creation - tengen --identifer={identifier}",
            references="https://doi.org/10.1023/A:1024048429145",
        )
    else:
        raise ValueError(f"Unknown data set identifier '{identifier}'")


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
    w: Union[ureg.Quantity, np.ndarray],
    ssi: Union[ureg.Quantity, np.ndarray],
    title: str,
    institution: str,
    source: str,
    history: str,
    references: str,
    comment: Optional[str] = None,
    url_info: Optional[Tuple[str, str]] = None,
    t: Optional[pd.DatetimeIndex] = None,
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
    """
    coords: Dict[Hashable, Any] = {"w": ("w", w, _W_ATTRS)}

    if t is not None:
        coords["t"] = ("t", t, _T_ATTRS)
        data_vars: Dict[Hashable, Any] = {"ssi": (("t", "w"), ssi, _SSI_ATTRS)}
    else:
        coords["t"] = ("t", np.empty(0), _T_ATTRS)
        data_vars = {"ssi": ("w", ssi, _SSI_ATTRS)}

    attrs: Dict[Hashable, Any] = dict(
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
