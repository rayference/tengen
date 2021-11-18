"""Core module."""
import xarray as xr

from .coddington_2021 import coddington_2021
from .thuillier_2003 import thuillier_2003

RESOURCE = {
    "thuillier_2003": thuillier_2003,
    "coddington_2021": coddington_2021,
}


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
    return RESOURCE[identifier].get()
