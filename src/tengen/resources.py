"""Resources module."""
import datetime
import enum
import os
import pathlib
import shutil
import typing as t
import urllib.request as request
from contextlib import closing
from io import BytesIO

import attr
import numpy as np
import pandas as pd
import requests
import xarray as xr

from .units import format_missing_carats_units
from .units import ureg
from .util import to_data_set


@attr.s
class Resource:
    """Resource class.

    This class represents a data set publicly available on the Web.
    The class provides a link between the Web resource and the actual data set.
    It provides methods to:

    * save the data set in a cache
    * fetch the data set from the cache
    * fetch the data set from the Web
    """

    name: str = attr.ib()
    url: t.Union[str, t.List[str]] = attr.ib()  # may be one or multiple URLs
    transform: t.Callable[[t.Union[str, t.List[str]]], xr.Dataset] = attr.ib()

    @property
    def cache_path(self) -> pathlib.Path:
        """Path to data set in cache."""
        cache_dir = pathlib.Path(".tengen_cache/")
        filename = f"{self.name}.nc"
        return cache_dir / filename

    @property
    def in_cache(self) -> bool:
        """``True`` if the resource is in the cache, ``False`` otherwise."""
        return self.cache_path.exists()

    def fetch_from_web(self) -> xr.Dataset:
        """Fetch the data set from the Web.

        If the data set is not already in the cache, it is added to the cache.

        Returns
        -------
        :class:`~xarray.Dataset`:
            Data set.
        """
        dataset = self.transform(self.url)
        if not self.in_cache:
            dataset.to_netcdf(self.cache_path)
        return dataset

    def fetch_from_cache(self) -> xr.Dataset:
        """Fetch the data set from the cache.

        Returns
        -------
        :class:`~xarray.Dataset`:
            Data set.
        """
        if self.in_cache:
            ds = xr.open_dataset(self.cache_path)  # type: ignore[no-untyped-call]
            return ds  # type: ignore[no-any-return]
        else:
            raise ValueError("data set is not in the cache.")

    def get(self) -> xr.Dataset:
        """Get the data set.

        Try to fetch the resource from the Web.
        In case of a connection error, fetch from the cache.

        Raises
        ------
        ValueError
            If the data set could not be fetched neither from the Web
            nor from the cache.
            This can happen for example when the data set could not fetched
            from the Web due to a connection error with a cache that does
            not already include the data set.

        Returns
        -------
        :class:`~xarray.Dataset`:
            Data set.
        """
        try:
            return self.fetch_from_web()
        except requests.ConnectionError as e:
            if self.in_cache:
                return self.fetch_from_cache()
            else:
                raise ValueError(
                    "could not fetch data set from the Web and could not fetch "
                    "from the cache because data set is in not in the cache"
                ) from e


# ------------------------------------------------------------------------------
#                                Thuillier (2003)
# ------------------------------------------------------------------------------

THUILLIER_2003_URL = "https://oceancolor.gsfc.nasa.gov/docs/rsr/f0.txt"


def transform_thuillier_2003(url: t.Union[str, t.List[str]]) -> xr.Dataset:
    """Transform function for Thuillier (2003).

    Transform the HTTP response to :class:`xarray.Dataset` for the Thuillier
    (2003) solar irradiance spectrum data set.

    Parameters
    ----------
    url: str or list of str
        URL.

    Returns
    -------
    :class:`xarray.Dataset`
        Thuillier (2003) solar irradiance spectrum data set.
    """
    response = requests.get(str(url))
    data = np.loadtxt(  # type: ignore[no-untyped-call]
        fname=BytesIO(response.content),
        comments=["/", "!"],
    )
    w = data[:, 0] * ureg.nm
    ssi = ureg.Quantity(data[:, 1], "microwatt/cm^2/nm")

    attrs = dict(
        title="Thuillier (2003) solar irradiance spectrum",
        institution=(
            "Service d'Aéronomie du CNRS, F91371, Verrières-le-Buisson, France."
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

    return to_data_set(
        w=w,
        ssi=ssi,
        attrs=attrs,
        url=str(url),
    )


thuillier_2003 = Resource(
    name="thuillier_2003",
    url=THUILLIER_2003_URL,
    transform=transform_thuillier_2003,
)


# ------------------------------------------------------------------------------
#                                WHI (2008)
# ------------------------------------------------------------------------------

WHI_2008_URL = (
    "https://lasp.colorado.edu/lisird/resources/whi_ref_spectra/data/"
    "ref_solar_irradiance_whi-2008_ver2.dat"
)

WHI_2008_TIME_PERIOD = {
    "sunspot active": (datetime.date(2008, 3, 25), datetime.date(2008, 3, 29)),
    "faculae active": (datetime.date(2008, 3, 29), datetime.date(2008, 4, 4)),
    "quiet sun": (datetime.date(2008, 4, 10), datetime.date(2008, 4, 16)),
}


def transform_whi_2008(
    identifier: str,
) -> t.Callable[[t.Union[str, t.List[str]]], xr.Dataset]:
    """Creates the WHI (2008) transform method.

    .. list-table::
       :widths: 1 1
       :header-rows: 1

       * - Time period
         - File name
       * - 2008-03-25 - 2008-03-29
         - ``whi_2008_1``
       * - 2008-03-29 - 2008-04-04
         - ``whi_2008_2``
       * - 2008-04-10 - 2008-04-16
         - ``whi_2008_3``

    Parameters
    ----------
    identifier: str
        WHI (2008) spectrum variant identifier.

    Returns
    -------
    callable
        Associated transform method.
    """

    def f(url: t.Union[str, t.List[str]]) -> xr.Dataset:
        r = requests.get(url)
        data = np.loadtxt(  # type: ignore[no-untyped-call]
            fname=BytesIO(r.content),
            comments=";",
            skiprows=142,
        )
        wavelength = data[:, 0]
        mask = wavelength > 116.0

        time_period = WHI_2008_TIME_PERIOD[identifier]
        start, end = time_period

        time_period_index = list(WHI_2008_TIME_PERIOD.keys()).index(identifier)

        return to_data_set(
            ssi=ureg.Quantity(data[mask, time_period_index], "W/m^2/nm"),
            w=ureg.Quantity(wavelength[mask], "nm"),
            url=WHI_2008_URL,
            attrs=dict(
                title=f"Whole Heliosphere Interval (WHI) solar "
                f"irradiance reference spectrum (2008) for time p"
                f"eriod {time_period} ('{identifier}' spectrum)",
                source=f"Combination of satellite observations from "
                f"the SEE and SORCE instruments (from {start} to {end}) "
                f"onboard the TIMED satellite and a prototype EVE "
                f"instrument onboard a sounding rocket launched on "
                f"2008-04-14.",
                ref="https://doi.org/10.1029/2008GL036373",
                observation_period=" to ".join(
                    [x.strftime("%Y-%m-%d") for x in [start, end]]
                ),
                comment="The original data covers the range from 0.05 to 2399.95 "
                "nm, the present dataset includes only the part of the "
                "original data where the wavelength > 116 nm.",
            ),
        )

    return f


whi_2008_sunspot_active = Resource(
    name="whi_2008_sunspot_active",
    url=WHI_2008_URL,
    transform=transform_whi_2008(identifier="sunspot active"),
)

whi_2008_faculae_active = Resource(
    name="whi_2008_faculae_active",
    url=WHI_2008_URL,
    transform=transform_whi_2008(identifier="faculae active"),
)

whi_2008_quiet_sun = Resource(
    name="whi_2008_quiet_sun",
    url=WHI_2008_URL,
    transform=transform_whi_2008(identifier="quiet sun"),
)

# ------------------------------------------------------------------------------
#                                Meftah (2017)
# ------------------------------------------------------------------------------

MEFTAH_2018_URL = "http://cdsarc.u-strasbg.fr/ftp/J/A+A/611/A1/spectrum.dat.gz"


def transform_meftah_2018(url: t.Union[str, t.List[str]]) -> xr.Dataset:
    """Transform function for Meftah (2018).

    Transform the HTTP response to :class:`xarray.Dataset` for the Meftah
    (2018) solar irradiance spectrum data set.

    Parameters
    ----------
    url: str or list of str
        URL.

    Returns
    -------
    :class:`xarray.Dataset`
        Meftah (2018) solar irradiance spectrum data set.
    """
    filename = "spectrum.dat.gz"
    with closing(request.urlopen(str(url))) as r:  # noqa: S310
        with open(filename, "wb") as f:
            shutil.copyfileobj(r, f)

    data = np.genfromtxt(  # type: ignore[no-untyped-call]
        fname=filename,
        missing_values="---",
        filling_values=np.nan,
    )

    wavelength = data[:, 0]
    spectral_irradiance = data[:, 1]

    # The raw data covers the 0.5 to 3000.10 nm range whereas the range
    # indicated by Meftah (2018) in:
    # https://doi.org/10.1051/0004-6361/201731316
    # is 165 to 3000 nm.
    # Therefore, we ignore wavelengthes < 165, and keep the 3000.10 nm point.
    mask = wavelength >= 165.0

    start = datetime.date(2008, 4, 5)
    end = datetime.date(2016, 12, 31)

    ds = to_data_set(
        ssi=ureg.Quantity(spectral_irradiance[mask], "W/m^2/nm"),
        w=ureg.Quantity(wavelength[mask], "nm"),
        url=MEFTAH_2018_URL,
        attrs=dict(
            title="Meftah et al (2018) solar irradiance reference spectrum",
            source=(
                "Observations from the SOLSPEC instrument of the SOLAR payload "
                "onboard the international space station"
            ),
            ref="https://doi.org/10.1051/0004-6361/201731316",
            observation_period=" to ".join(
                [x.strftime("%Y-%m-%d") for x in [start, end]]
            ),
        ),
    )

    os.remove(filename)

    return ds


meftah_2018 = Resource(
    name="meftah_2018",
    url=MEFTAH_2018_URL,
    transform=transform_meftah_2018,
)

# ------------------------------------------------------------------------------
#                                SOLID (2017)
# ------------------------------------------------------------------------------


SOLID_2017_FTP_FOLDER = (
    "ftp://ftp.pmodwrc.ch/pub/projects/SOLID/database/composite_published/"
    "SOLID_1978_published/"
)

SOLID_2017_FILES = [
    "solid_0_100.nc",
    "solid_100_100.nc",
    "solid_200_100.nc",
    "solid_300_100.nc",
    "solid_400_100.nc",
    "solid_500_100.nc",
    "solid_600_100.nc",
    "solid_700_100.nc",
    "solid_800_100.nc",
    "solid_900_100.nc",
    "solid_1000_100.nc",
    "solid_1100_100.nc",
    "solid_1200_100.nc",
    "solid_1300_100.nc",
    "solid_1400_100.nc",
    "solid_1500_100.nc",
    "solid_1600_100.nc",
    "solid_1700_100.nc",
    "solid_1800_100.nc",
    "solid_1900_100.nc",
]

SOLID_2017_URL = [SOLID_2017_FTP_FOLDER + file for file in SOLID_2017_FILES]


def transform_solid_2017(url: t.Union[str, t.List[str]]) -> xr.Dataset:
    """Transform function for SOLID (2017).

    Transform the HTTP response to :class:`xarray.Dataset` for the SOLID
    (2017) solar irradiance spectrum data set.

    Parameters
    ----------
    url: str or list of str
        URL.

    Returns
    -------
    :class:`xarray.Dataset`
        SOLID (2017) solar irradiance spectrum data set.
    """
    filenames = []
    for x in url:
        with closing(request.urlopen(x)) as r:  # noqa: S310
            filename = x.split("/")[-1]
            filenames.append(filename)
            with open(filename, "wb") as f:
                shutil.copyfileobj(r, f)

    ds = xr.open_mfdataset("solid_*.nc")  # type: ignore[no-untyped-call]

    end = datetime.date(2014, 12, 31)
    start = end - datetime.timedelta(ds.time.size - 1)

    formatted = to_data_set(
        w=ureg.Quantity(ds.wavelength.values, ds.wavelength.units),
        t=pd.date_range(start, end),
        ssi=ureg.Quantity(
            ds.data.values.transpose(), format_missing_carats_units(ds.data.units)
        ),
        url=SOLID_2017_FTP_FOLDER,
        attrs=dict(
            title="SOLID solar irradiance composite spectrum",
            source="Combined original SSI observations from 20 different"
            " instruments",
            observation_period=" to ".join(
                [x.strftime("%Y-%m-%d") for x in [start, end]]
            ),
            ref="https://doi.org/10.1002/2016JA023492",
        ),
    )

    for filename in filenames:
        os.remove(filename)

    return formatted


solid_2017 = Resource(
    name="solid_2017", url=SOLID_2017_URL, transform=transform_solid_2017
)


# ------------------------------------------------------------------------------
#                                Coddington (2021)
# ------------------------------------------------------------------------------


def transform_coddington_2021(url: t.Union[str, t.List[str]]) -> xr.Dataset:
    """Transform function for Coddington (2021).

    Transform the HTTP response to :class:`xarray.Dataset` for the Coddington
    (2021) solar irradiance spectrum data set.

    Parameters
    ----------
    url: str or list of str
        URL.

    Returns
    -------
    :class:`xarray.Dataset`
        Coddington (2021) solar irradiance spectrum data set.
    """
    response = requests.get(str(url))
    raw = xr.open_dataset(BytesIO(response.content), engine="h5netcdf")  # type: ignore
    w = ureg.Quantity(raw["Vacuum Wavelength"].values, raw["Vacuum Wavelength"].units)
    ssi = ureg.Quantity(
        raw["SSI"].values, format_missing_carats_units(raw["SSI"].units)
    )
    attrs = dict(
        title="TSIS-1 Hybrid Solar Reference Spectrum (HSRS)",
        institution="Laboratory for Atmospheric and Space Physics",
        source=(
            "TSIS-1 Spectral Irradiance Monitor (SIM), CubeSat Compact SIM "
            "(CSIM), Air Force Geophysical Laboratory ultraviolet solar "
            "irradiance balloon observations, ground-based Quality Assurance "
            "of Spectral Ultraviolet Measurements In Europe Fourier transform "
            "spectrometer solar irradiance observations, Kitt Peak National "
            "Observatory solar transmittance atlas and the semi-empirical "
            "Solar Pseudo-Transmittance Spectrum atlas."
        ),
        references="https://doi.org/10.1029/2020GL091709",
    )

    return to_data_set(w=w, ssi=ssi, attrs=attrs, url=str(url))


class Coddington2021Resolution(enum.Enum):
    """Coddington (2021) spectral resolution variant enumeration."""

    HIGH_RESOLUTION = ""
    ZP005 = "p005nm_resolution_"
    ZP025 = "p025nm_resolution_"
    ZP1 = "p1nm_resolution_"
    Z1 = "1nm_resolution_"


def coddington_2021_url(
    resolution: Coddington2021Resolution = Coddington2021Resolution.HIGH_RESOLUTION,
) -> str:
    """Get URL corresponding to Coddington (2021) spectral resolution variant.

    Parameters
    ----------
    resolution: Coddington2021Resolution
        Coddington (2021) spectral resolution variant.
    """
    root_url = "https://lasp.colorado.edu/lisird/resources/lasp/hsrs/"
    filename = f"hybrid_reference_spectrum_{resolution.value}c2021-03-04_with_unc.nc"
    return f"{root_url}/{filename}"


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
