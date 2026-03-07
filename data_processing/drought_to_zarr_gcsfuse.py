from datetime import datetime
import os
from pathlib import Path
import subprocess
import sys
import timeit

from ndpyramid import *
import numpy as np
import pandas as pd
import xarray as xr
import zarr


def process_dataset(ds: xr.core.dataset.Dataset) -> xr.core.dataset.Dataset:
    """
    Take in a Xarray Dataset, rename the latitude and longitude columns, and shift the latitudes by 180 degrees.

    Parameters:
        ds(xarray.core.dataset.Dataset): a Xarray Dataset with at least the dims (time, longitude, latitude)

    Returns:
        ds(xarray.core.dataset.Dataset): a modified version of the input Dataset
    """
    ds = ds.rename({ 'longitude':'x','latitude':'y'})
    ds.rio.write_crs(4326, inplace=True)
    ds.coords['x'] = (ds.coords['x'] + 180) % 360 - 180
    ds = ds.sortby(ds.x)

    return ds


def pyramid_to_zarr(ds: xr.core.dataset.Dataset, levels: int, path: str) -> None:
    """
    Convert a Xarray Dataset into a Zarr for visualization using CarbonPlan's `maps` package.

    Parameters:
        ds(xarray.core.dataset.Dataset): a Xarray Dataset with at least the dims (time, longitude, latitude)

        levels(int): the number of desired levels in the output Zarr pyramid

        path(str): the path on disk for where to save the Zarr store

    Returns:
        None
    """
    dt = pyramid_reproject(ds, levels=levels, other_chunks={'time': len(ds.time)})
    dt.to_zarr(path, consolidated=True)


def drought_pipeline():
    """
    Download processed historical and forecast water balance data and create Zarr stores
    for both visualization and analysis.
    """
    start = timeit.default_timer()
    #---------------------------------------------------------------------------

    # calculate the initial conditions from today's year and month
    # in general, the month (and potentially year) roll back one month
    # for example: if we are producing the forecast in january, 
    # then the initial conditions are from december of the previous year
    today = datetime.today()
    # year = today.year
    # month = today.month
    year = 2025
    month = 12

    if month == 1:
        month = 12
        year = year - 1
    else: 
        month -= 1

    month_ic = str(month) if month >= 10 else '0' + str(month) 
    year_ic = str(year)

    # outline file structure
    root = Path(os.getenv('BASE_PATH'))

    historical_raster_path = root / 'historical'
    forecast_raster_path = root / 'forecast'

    analysis_zarr_path = root / 'zarr' / 'analysis'
    viz_zarr_path = root / 'zarr' / 'viz'

    # create temporary directory structure if it does not exist
    historical_raster_path.mkdir(parents=True, exist_ok=True)
    forecast_raster_path.mkdir(parents=True, exist_ok=True)
    analysis_zarr_path.mkdir(parents=True, exist_ok=True)
    viz_zarr_path.mkdir(parents=True, exist_ok=True)

    print('--- Parent directory structure ---')
    print(os.listdir(root.resolve()))
    print()

    print('=== Listing number of NetCDF files ===')
    print()

    print('--- Historical NetCDFs ---')
    print(len(list(historical_raster_path.glob('*.nc'))))
    print()

    print('--- Forecast NetCDFs ---')
    print(len(list(forecast_raster_path.glob('*.nc'))))

    print()
    print('Done!')
    print()

    #---------------------------------------------------------------------------
    end = timeit.default_timer()
    print(f"Time to complete: {(end - start) / 3600 :.5f} hours")


if __name__ == '__main__':
    drought_pipeline()