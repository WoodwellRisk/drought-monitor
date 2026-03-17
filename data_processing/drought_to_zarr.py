from concurrent.futures import ProcessPoolExecutor
from datetime import datetime
import os
from pathlib import Path
import timeit

import gcsfs
from ndpyramid import *
import numpy as np
import pandas as pd
import rioxarray
import xarray as xr
import zarr


def open_historical_dataset(path: str) -> xr.core.dataset.Dataset:
        """
        Opens a single file from GCS, extracts time dimension from filename, and returns a chunked dataset.

        Parameters:
            path(str): a filename pointing to a Xarray Dataset on a GCS bucket

        Returns:
            ds(xr.core.dataset.Dataset): an opened Xarray Dataset with dims ['time', 'x', 'y']
        """
        # workers inherit ACCESS_TOKEN from the environment, but need their own fs object
        ACCESS_TOKEN = os.getenv('GCLOUD_ACCESS_TOKEN')
        ds = xr.open_dataset(path, engine='h5netcdf', chunks={'x': 128, 'y': 128}, storage_options={'token': ACCESS_TOKEN})
        ds = ds.assign_coords({'time': pd.to_datetime(path[-13:-3])})

        return ds


def open_forecast_dataset(path: str) -> xr.core.dataset.Dataset:
        """
        Open a single Xarray Dataset based on a file path.

        Parameters:
            path(str): a filename pointing to a Xarray Dataset

        Returns:
            ds(xr.core.dataset.Dataset): an opened Xarray Dataset with dims ['time', 'x', 'y']
        """
        ACCESS_TOKEN = os.getenv('GCLOUD_ACCESS_TOKEN')
        ds = xr.open_dataset(path, engine='h5netcdf', chunks={'x': 128, 'y': 128}, storage_options={'token': ACCESS_TOKEN})

        return ds


def open_files_in_parallel(files: list) -> list:
    """
    Open a list of files pointing to NetCDF datasets in parallel.

    Parameters:
        files(list): a list of filenames

    Returns:
        ds_list(list): a list of opened Xarray Datasets
    """
    with ProcessPoolExecutor(max_workers=4) as executor:
        # map the function to all files
        ds_list = list(executor.map(open_historical_dataset, files))

    return ds_list


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
    # https://github.com/zarr-developers/zarr-python/issues/2964
    dt = pyramid_reproject(ds.drop_encoding(), levels=levels, other_chunks={'time': len(ds.time)})
    dt.to_zarr(path, consolidated=True, zarr_format=2, mode='w')


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
    year = 2026
    month = 3

    if month == 1:
        month = 12
        year = year - 1
    else: 
        month -= 1

    month_ic = str(month) if month >= 10 else '0' + str(month) 
    year_ic = str(year)

    # environment variables comes from .github/workflows/generate-wb-zarr.yml
    BUCKET = os.getenv('BUCKET_NAME')

    print('Generating input file list.')
    print()
    # create file list
    dates = pd.date_range(start='1991-01-01', end=f'{year_ic}-{month_ic}-01', freq='MS')
    h3_files = sorted([f'gs://{BUCKET}/historical/era5_water-balance-perc-w3_bl-1991-2020_mon_{date.strftime("%Y-%m-%d")}.nc' for date in dates])
    h12_files = sorted([file.replace('w3', 'w12') for file in h3_files])

    forecast_files = [f'gs://{BUCKET}/forecast/nmme_ensemble_water-balance-perc-w{window}_mon_ic-{year_ic}-{month_ic}-01_leads-6.nc' for window in [3, 12]]
    f3_file = [file for file in forecast_files if 'w3' in file][0]
    f12_file = [file for file in forecast_files if 'w12' in file][0]

    print('Opening data.')
    # open historical data for both integration windows
    # parallelize data reads
    # note: if we tried to use xr.open_mfdataset(...parallel=True), 
    # we would not be able to extract the time from the filename for each NetCDF
    print('    Opening H3 data...')
    ds_list = open_files_in_parallel(h3_files)
    h3 = xr.concat(ds_list, dim='time')
    h3 = process_dataset(h3)

    print('    Opening H12 data...')
    ds_list = open_files_in_parallel(h12_files)
    h12 = xr.concat(ds_list, dim='time')
    h12 = process_dataset(h12)

    # open forecast data for both integration windows
    print('    Opening F3 data...')
    f3 = open_forecast_dataset(f3_file)
    f3 = process_dataset(f3)
    f3 = f3.rename({ 'L': 'time', '50%': 'perc' })
    f3 = f3[['time', 'y', 'x', 'spatial_ref', '5%', '20%', 'perc', '80%', '95%']]
    
    print('    Opening F12 data...')
    print()
    f12 = open_forecast_dataset(f12_file)
    f12 = process_dataset(f12)
    f12 = f12.rename({ 'L': 'time', '50%': 'perc' })
    f12 = f12[['time', 'y', 'x', 'spatial_ref', '5%', '20%', 'perc', '80%', '95%']]

    dataset_dict = {
        'h3': h3,
        'h12': h12,
        'f3': f3,
        'f12': f12,
    }

    print('Saving Zarr stores used for analysis.')
    # save the data as zarr stores that we will use for analysis
    for dataset in ['h3', 'h12', 'f3', 'f12']:
        print(f'    Saving {dataset.upper()} data...')
        dataset_dict[dataset].to_zarr(f'gs://{BUCKET}/zarr/analysis/{dataset}-{year_ic}-{month_ic}-01.zarr', consolidated=True, zarr_format=2, mode='w')
    print()

    print('Saving Zarr stores used for visualization.')
    # next, save the data as zarr stores that we will use for visualization
    # first, we need to save their time coordinates as strings
    h3['time'] = [pd.to_datetime(value).strftime('%Y-%m-%d') for value in h3.time.values]
    h12['time'] = [pd.to_datetime(value).strftime('%Y-%m-%d') for value in h12.time.values]
    f3['time'] = [pd.to_datetime(value).strftime('%Y-%m-%d') for value in f3.time.values]
    f12['time'] = [pd.to_datetime(value).strftime('%Y-%m-%d') for value in f12.time.values]

    # datasets' 'time' dimension has changed
    dataset_dict['h3'] = h3
    dataset_dict['h12'] = h12
    dataset_dict['f3'] = f3
    dataset_dict['f12'] = f12

    # next, calculate the number of zoom levels to use for the output Zarr
    pixels_per_tile = 128
    longitute_length = h3.perc.x.shape[0]
    max_levels = round(np.sqrt(longitute_length / pixels_per_tile)) + 1
    levels = max_levels

    # create pyramids for each dataset, then save the pyramid to zarr
    for dataset in ['h3', 'h12', 'f3', 'f12']:
        print(f'    Saving {dataset.upper()} data...')
        pyramid_to_zarr(dataset_dict[dataset], levels, f'gs://{BUCKET}/zarr/viz/{dataset}-{year_ic}-{month_ic}-01.zarr')
    print()

    print('Done!')
    print()

    #---------------------------------------------------------------------------
    end = timeit.default_timer()
    print(f"Time to complete: {(end - start) / 3600 :.5f} hours")


if __name__ == '__main__':
    drought_pipeline()