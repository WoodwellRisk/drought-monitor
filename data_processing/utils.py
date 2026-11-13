from concurrent.futures import ThreadPoolExecutor

import numpy as np
import pandas as pd
import rioxarray
import xarray as xr
from ndpyramid import pyramid_reproject


def shift_longitudes(ds: xr.Dataset) -> xr.Dataset:
    """
    Take in an Xarray dataset and shift the longitudes by 180 degrees.
    """
    ds.coords['x'] = (ds.coords['x'] + 180) % 360 - 180
    ds = ds.sortby(ds.x)

    return ds


def open_dataset(path: str) -> xr.Dataset:
    """
    Opens a single file from GCS and returns a chunked dataset.

    Parameters:
        path(str): a filename pointing to a Xarray Dataset on a GCS bucket

    Returns:
        ds(xr.Dataset): an opened Xarray Dataset with dims ['time', 'x', 'y']
    """
    ds = xr.open_dataset(path, engine='h5netcdf', chunks={})

    return ds


def open_files_in_parallel(files: list) -> list:
    """
    Open a list of files pointing to NetCDF datasets in parallel.

    Parameters:
        files(list): a list of filenames

    Returns:
        ds_list(list): a list of opened Xarray Datasets
    """
    with ThreadPoolExecutor(max_workers=4) as executor:
        # map the function to all files
        ds_list = list(executor.map(open_dataset, files))

    return ds_list


def process_dataset(ds: xr.Dataset) -> xr.Dataset:
    """
    Take in a Xarray Dataset, rename the latitude and longitude columns, and shift the longitudes by 180 degrees.

    Parameters:
        ds(xarray.core.dataset.Dataset): a Xarray Dataset with at least the dims (time, longitude, latitude)

    Returns:
        ds(xarray.core.dataset.Dataset): a modified version of the input Dataset
    """
    ds = ds.rename({'longitude': 'x', 'latitude': 'y'})
    ds = ds.rio.write_crs(4326)
    ds = shift_longitudes(ds)

    return ds


def scale_percentiles(ds: xr.Dataset) -> xr.Dataset:
    """
    Scale each data variable in `ds` by 100.
    This shifts the data from [0, 1] to [0, 100].
    """
    with xr.set_options(keep_attrs=True):
        return ds * 100


def format_time_as_dates(ds: xr.Dataset) -> xr.Dataset:
    """
    Convert NumPy datetime strings to U10 strings for the 'time' dim in the input `ds`.
    """
    ds['time'] = np.array(
        [pd.to_datetime(value).strftime('%Y-%m-%d') for value in ds.time.values],
        dtype='U10',
    )

    return ds


def pyramid_to_zarr(ds: xr.Dataset, levels: int, path: str) -> None:
    """
    Convert a Xarray Dataset into a Zarr for visualization using CarbonPlan's `maps` package.

    Parameters:
        ds(xarray.core.dataset.Dataset): a Xarray Dataset with at least the dims (time, longitude, latitude)

        levels(int): the number of desired levels in the output Zarr pyramid

        path(str): the path on disk for where to save the Zarr store

    Returns:
        None
    """
    # https://github.com/zarr-developers/zarr-python/issues/2964
    dt = pyramid_reproject(
        ds.drop_encoding(),
        levels=levels,
        # extra_dim='window',
        # other_chunks={'window': len(ds.window), 'time': len(ds.time)},
        other_chunks={'time': len(ds.time)},
    )

    dt.to_zarr(path, zarr_format=2, consolidated=True, mode='w')
