"""Thuillier (2003) module."""
import datetime
import io

import numpy as np
import requests
import xarray as xr

from . import __version__
from .util import make_data_set
from .resource import Resource
from .units import ureg


def transform(response: requests.Response) -> xr.Dataset:
    """Transform function for Thuillier (2003).

    Transform the HTTP response to :class:`xarray.Dataset` for the Thuillier
    (2003) solar irradiance spectrum data set.

    Parameters
    ----------
    response: :class:`~requests.Response`
        HTTPS response.

    Returns
    -------
    :class:`xarray.Dataset`
        Thuillier (2003) solar irradiance spectrum data set.
    """
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    data = np.loadtxt(io.BytesIO(response.content), comments=["/", "!"])
    wavelength_values = data[:, 0]
    spectral_irradiance_values = ureg.Quantity(data[:, 1], "microwatt/cm^2/nm")

    return make_data_set(  # type: ignore
        w=wavelength_values,
        ssi=spectral_irradiance_values,
        title="Thuillier (2003) solar irradiance spectrum",
        institution=(
            "Service d'Aéronomie du CNRS, F91371, Verrières-le-Buisson, France.",
        ),
        source=(
            "Combined observations from the SOLSPEC instrument during "
            "the ATLAS-1 mission (from 1992-03-24 to 1992-04-02) and the SOSP "
            "instrument onboard the EURECA satellite (from 1992-8-7 to "
            "1993-7-1), with the Kurucz and Bell (1995) synthetic "
            "spectrum"
        ),
        history=f"{now} - data set creation - tengen, version {__version__}",
        references="https://doi.org/10.1023/A:1024048429145",
    )


thuillier_2003 = Resource(
    name="thuillier_2003",
    url="https://oceancolor.gsfc.nasa.gov/docs/rsr/f0.txt",
    transform=transform,
)
