import pathlib
import typing as t

import attr
import requests
import xarray as xr


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
            self.fetch_from_web()
        except requests.ConnectionError:
            if self.in_cache:
                self.fetch_from_cache()
            else:
                raise ValueError(
                    "could not fetch data set from the Web and could not fetch "
                    "from the cache because data set is in not in the cache"
                )
