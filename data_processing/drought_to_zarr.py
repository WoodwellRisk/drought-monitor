from datetime import datetime
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
    historical_raster_path = Path(__file__).parent / 'raster/historical'
    forecast_raster_path = Path(__file__).parent / 'raster/forecast'
    analysis_zarr_path = Path(__file__).parent / 'zarr/analysis'
    viz_zarr_path = Path(__file__).parent / 'zarr/viz'

    # create temporary directory structure if it does not exist
    historical_raster_path.mkdir(parents=True, exist_ok=True)
    forecast_raster_path.mkdir(parents=True, exist_ok=True)
    analysis_zarr_path.mkdir(parents=True, exist_ok=True)
    viz_zarr_path.mkdir(parents=True, exist_ok=True)

    print('Generating input file list.')
    print()
    
    # generate the list of files we expect to find for both historical and forecast data
    dates = pd.date_range(start='1991-01-01', end=f'{year_ic}-{month_ic}-01', freq='MS')
    h3_files = sorted([f'era5_water-balance-perc-w3_bl-1991-2020_mon_{date.strftime("%Y-%m-%d")}.nc' for date in dates])
    h12_files = sorted([file.replace('w3', 'w12') for file in h3_files])

    forecast_files = [f'nmme_ensemble_water-balance-perc-w{window}_mon_ic-{year_ic}-{month_ic}-01_leads-6.nc' for window in [3, 12]]
    f3_file = [file for file in forecast_files if 'w3' in file][0]
    f12_file = [file for file in forecast_files if 'w12' in file][0]

    print()
    print('Downloading historical and forecast data (if not already present).')
    # if past historical files that we need don't exist locally, we need to download them once
    for window in [3, 12]:
        if window == 3:
            files = h3_files
        else:
            files = h12_files

        for file in files:
            if not Path(historical_raster_path / file).is_file():
                result = subprocess.run([
                    'gcloud',
                    'storage',
                    '--no-user-output-enabled', 
                    'cp',
                    f'gs://drought-monitor/historical/{file}',
                    historical_raster_path,
                ])

                if(result.returncode != 0):
                    print('Error downloading updated historical data, exiting.')
                    print(return_code)
                    sys.exit()

    # forecast files are only downloaded once a month as new data is generated
    for window in [3, 12]:
        file = [file for file in forecast_files if str(window) in file][0]

        if not Path(forecast_raster_path / file).is_file():
            result = subprocess.run([
                'gcloud',
                'storage',
                '--no-user-output-enabled', 
                'cp',
                f'gs://drought-monitor/forecast/{file}',
                forecast_raster_path,
            ])

            if(result.returncode != 0):
                print('Error downloading updated forecast data, exiting.')
                sys.exit()

    print()
    print('Opening data.')
    print()
    # open historical data for both integration windows
    h3 = xr.concat([xr.open_dataset(historical_raster_path / file).assign_coords({'time': pd.to_datetime(file[-13:-3])}) for file in h3_files], dim='time')
    h3 = process_dataset(h3)

    h12 = xr.concat([xr.open_dataset(historical_raster_path / file).assign_coords({'time': pd.to_datetime(file[-13:-3])}) for file in h12_files], dim='time')
    h12 = process_dataset(h12)

    # open forecast data for both integration windows
    f3 = xr.open_dataset(forecast_raster_path / f3_file, engine='netcdf4')
    f3 = process_dataset(f3)
    f3 = f3.rename({ 'L': 'time', '50%': 'perc' })
    f3 = f3[['time', 'y', 'x', 'spatial_ref', '5%', '20%', 'perc', '80%', '95%']]

    f12 = xr.open_dataset(forecast_raster_path / f12_file, engine='netcdf4')
    f12 = process_dataset(f12)
    f12 = f12.rename({ 'L': 'time', '50%': 'perc' })
    f12 = f12[['time', 'y', 'x', 'spatial_ref', '5%', '20%', 'perc', '80%', '95%']]

    dataset_dict = {
        'h3': h3,
        'h12': h12,
        'f3': h3,
        'f12': f12,
    }

    print('Saving Zarr stores used for analysis.')
    # save the data as zarr stores that we will use for analysis
    for dataset in ['h3', 'h12', 'f3', 'f12']:
        dataset_dict[dataset].to_zarr(f'{analysis_zarr_path}/{dataset}-{year_ic}-{month_ic}-01.zarr', consolidated=True, zarr_format=2, mode='w')

    for dataset in ['h3', 'h12', 'f3', 'f12']:
        print(f'   Uploading {dataset} to analysis bucket.')
        result = subprocess.run([
            'gcloud',
            'storage',
            '--no-user-output-enabled', 
            'cp',
            '-r',
            f'./zarr/analysis/{dataset}-{year_ic}-{month_ic}-01.zarr',
            'gs://drought-monitor/zarr/analysis/',
        ])

        if(result.returncode != 0):
            print('   Error uploading data to analysis bucket, exiting.')
            sys.exit()

    print()
    print('Saving Zarr stores used for visualization.')
    # next, save the data as zarr stores that we will use for visualization
    # first, we need to save their time coordinates as strings
    h3['time'] = [pd.to_datetime(value).strftime('%Y-%m-%d') for value in h3.time.values]
    h12['time'] = [pd.to_datetime(value).strftime('%Y-%m-%d') for value in h12.time.values]
    f3['time'] = [pd.to_datetime(value).strftime('%Y-%m-%d') for value in f3.time.values]
    f12['time'] = [pd.to_datetime(value).strftime('%Y-%m-%d') for value in f12.time.values]

    # next, calculate the number of zoom levels to use for the output Zarr
    pixels_per_tile = 128
    longitute_length = h3.perc.x.shape[0]
    max_levels = round(np.sqrt(longitute_length / pixels_per_tile)) + 1
    levels = max_levels

    # create pyramids for each dataset, then save the pyramid to zarr
    for dataset in ['h3', 'h12', 'f3', 'f12']:
        pyramid_to_zarr(dataset_dict[dataset], levels, viz_zarr_path / f'{dataset}-{year_ic}-{month_ic}-01.zarr')

    for dataset in ['h3', 'h12', 'f3', 'f12']:
        print(f'   Uploading {dataset} to visualization bucket.')
        result = subprocess.run([
            'gcloud',
            'storage',
            '--no-user-output-enabled', 
            'cp',
            '-r',
            f'./zarr/viz/{dataset}-{year_ic}-{month_ic}-01.zarr',
            'gs://drought-monitor/zarr/viz/',
        ])

        if(result.returncode != 0):
            print('   Error uploading data to visualization bucket, exiting.')
            sys.exit()

    print()
    print('Done!')
    print()

    #---------------------------------------------------------------------------
    end = timeit.default_timer()
    print(f"Time to complete: {(end - start) / 3600 :.5f} hours")


if __name__ == '__main__':
    drought_pipeline()