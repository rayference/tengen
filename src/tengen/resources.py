"""Resources module."""
import enum
import io
import pathlib
import typing as t
from io import BytesIO

import attr
import numpy as np
import requests
import xarray as xr

from .units import format_missing_carats_units, ureg
from .util import to_data_set


@attr.s
class Resource:
    """
    Resource class.

    This class represents a data set publicly available on the Web.
    The class provides a link between the Web resource and the actual data set.
    It provides methods to:

    * save the data set in a cache
    * fetch the data set from the cache
    * fetch the data set from the Web
    """

    name: str = attr.ib()
    url: str = attr.ib()
    transform: t.Callable[[requests.Response], xr.Dataset] = attr.ib()

    @property
    def cache_path(self) -> pathlib.Path:
        """
        Path to data set in cache.
        """
        cache_dir = pathlib.Path(".tengen_cache/")
        filename = f"{self.name}.nc"
        return cache_dir / filename

    @property
    def in_cache(self) -> bool:
        """
        ``True`` if the resource is in the cache, ``False`` otherwise.
        """
        return self.cache_path.exists()

    def fetch_from_web(self) -> xr.Dataset:
        """
        Fetch the data set from the Web.

        If the data set is not already in the cache, it is added to the cache.

        Returns
        -------
        :class:`~xarray.Dataset`:
            Data set.
        """
        response = requests.get(self.url)
        dataset = self.transform(response)
        if not self.in_cache:
            dataset.to_netcdf(self.cache_path)
        return dataset

    def fetch_from_cache(self) -> xr.Dataset():
        """
        Fetch the data set from the cache.

        Returns
        -------
        :class:`~xarray.Dataset`:
            Data set.
        """
        if self.in_cache:
            return xr.open_dataset(self.cache_path)
        else:
            raise ValueError("data set is not in the cache.")

    def push_to_cache(self, force: t.Optional[bool] = False):
        """
        Save the data set in the cache.

        If the data set is already in the cache, no action will be taken unless
        ``force=True`` is used.

        Parameters
        ----------
        force: bool, optional
            If ``True``, override the data set if it is already in the cache.

        """
        if force is True or not self.in_cache:
            dataset = self.fetch_from_web()
            dataset.to_netcdf(self.cache_path)

    def get(self) -> xr.Dataset:
        """
        Get the data set.

        Try to fetch the resource from the Web.
        In case of a connection error, fetch from the cache.

        Returns
        -------
        :class:`~xarray.Dataset`:
            Data set.
        """
        try:
            return self.fetch_from_web()
        except requests.ConnectionError:
            if self.in_cache:
                return self.fetch_from_cache()
            else:
                raise ValueError(
                    "could not fetch data set from the Web and could not fetch "
                    "from the cache because data set is in not in the cache"
                )


# ------------------------------------------------------------------------------
#                                Thuillier (2003)
# ------------------------------------------------------------------------------


def transform_thuillier_2003(response: requests.Response) -> xr.Dataset:
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
    data = np.loadtxt(io.BytesIO(response.content), comments=["/", "!"])
    w = data[:, 0] * ureg.nm
    ssi = ureg.Quantity(data[:, 1], "microwatt/cm^2/nm")

    attrs = dict(
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
        references="https://doi.org/10.1023/A:1024048429145",
    )

    return to_data_set(  # type: ignore
        w=w,
        ssi=ssi,
        attrs=attrs,
        url=response.url,
    )


thuillier_2003 = Resource(
    name="thuillier_2003",
    url="https://oceancolor.gsfc.nasa.gov/docs/rsr/f0.txt",
    transform=transform_thuillier_2003,
)


# ------------------------------------------------------------------------------
#                                Coddington (2021)
# ------------------------------------------------------------------------------


def transform_coddington_2021(response):
    raw = xr.open_dataset(BytesIO(response.content), engine="h5netcdf")  # type: ignore
    w = ureg.Quantity(raw["Vacuum Wavelength"].values, raw["Vacuum Wavelength"].units)
    ssi = ureg.Quantity(
        raw["SSI"].values, format_missing_carats_units(raw["SSI"].units)
    )
    attrs = dict(
        title="TSIS-1 Hybrid Solar Reference Spectrum (HSRS)",
        institution="Laboratory for Atmospheric and Space Physics",
        source="TSIS-1 Spectral Irradiance Monitor (SIM), CubeSat Compact SIM (CSIM), Air Force Geophysical Laboratory ultraviolet solar irradiance balloon observations, ground-based Quality Assurance of Spectral Ultraviolet Measurements In Europe Fourier transform spectrometer solar irradiance observations, Kitt Peak National Observatory solar transmittance atlas and the semi-empirical Solar Pseudo-Transmittance Spectrum atlas.",
        references="https://doi.org/10.1029/2020GL091709",
    )

    return to_data_set(w=w, ssi=ssi, attrs=attrs, url=response.url)


class Coddington2021Resolution(enum.Enum):
    HIGH_RESOLUTION = ""
    ZP005 = "p005nm_resolution_"
    ZP025 = "p025nm_resolution_"
    ZP1 = "p1nm_resolution_"
    Z1 = "1nm_resolution_"


def coddington_2021_url(
    resolution: Coddington2021Resolution = Coddington2021Resolution.HIGH_RESOLUTION,
):

    root_url = "https://lasp.colorado.edu/lisird/resources/lasp/hsrs"
    return f"{root_url}/hybrid_reference_spectrum_{resolution.value}c2021-03-04_with_unc.nc"


coddington_2021_high_resolution = Resource(
    name="coddington_2021-high_resolution",
    url=coddington_2021_url(resolution=Coddington2021Resolution.HIGH_RESOLUTION),
    transform=transform_coddington_2021,
)

coddington_2021_p005 = Resource(
    name="coddington_2021-p005",
    url=coddington_2021_url(resolution=Coddington2021Resolution.ZP005),
    transform=transform_coddington_2021,
)

coddington_2021_p025 = Resource(
    name="coddington_2021-p025",
    url=coddington_2021_url(resolution=Coddington2021Resolution.ZP025),
    transform=transform_coddington_2021,
)

coddington_2021_p1 = Resource(
    name="coddington_2021-p1",
    url=coddington_2021_url(resolution=Coddington2021Resolution.ZP1),
    transform=transform_coddington_2021,
)

coddington_2021_1 = Resource(
    name="coddington_2021-1",
    url=coddington_2021_url(resolution=Coddington2021Resolution.Z1),
    transform=transform_coddington_2021,
)
