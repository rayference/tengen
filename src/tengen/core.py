"""Core module."""
import xarray as xr

from .resources import (
    thuillier_2003,
    solid_2017,
    whi_2008_sunspot_active,
    whi_2008_faculae_active,
    whi_2008_quiet_sun,
    coddington_2021_high_resolution,
    coddington_2021_p005,
    coddington_2021_p025,
    coddington_2021_p1,
    coddington_2021_1,
)


RESOURCE = {
    "thuillier_2003": thuillier_2003,
    "whi_2008_sunspot_active": whi_2008_sunspot_active,
    "whi_2008_faculae_active": whi_2008_faculae_active,
    "whi_2008_quiet_sun": whi_2008_quiet_sun,
    "solid_2017": solid_2017,
    "coddington_2021-high_resolution": coddington_2021_high_resolution,
    "coddington_2021-p005": coddington_2021_p005,
    "coddington_2021-p025": coddington_2021_p025,
    "coddington_2021-p1": coddington_2021_p1,
    "coddington_2021-1": coddington_2021_1,
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
