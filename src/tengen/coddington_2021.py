from io import BytesIO

import xarray as xr

from .resource import Resource


def transform(response):
    raw = xr.open_dataset(BytesIO(response.content), engine="h5netcdf")  # type: ignore
    # ...
    return raw


coddington_2021 = Resource(
    name="coddington_2021",
    url="https://lasp.colorado.edu/lisird/resources/lasp/hsrs/hybrid_reference_spectrum_c2021-03-04_with_unc.nc",
    transform=transform,
)
