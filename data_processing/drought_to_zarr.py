import os
import timeit

import gcsfs
import numpy as np
import pandas as pd
import xarray as xr
import zarr
from utils import (
    format_time_as_dates,
    open_dataset,
    open_files_in_parallel,
    process_dataset,
    pyramid_to_zarr,
    scale_percentiles,
)


def drought_pipeline():
    """
    Download processed historical and forecast water balance data and create Zarr stores
    for both visualization and analysis.
    """
    start = timeit.default_timer()
    # ---------------------------------------------------------------------------

    # calculate the initial conditions from today's year and month
    # in general, the month (and potentially year) roll back one month
    # for example: if we are producing the forecast in january,
    # then the initial conditions are from december of the previous year
    # today = datetime.today()
    # year = today.year
    # month = today.month
    year = 2026
    month = 11

    if month == 1:
        month = 12
        year = year - 1
    else:
        month -= 1

    year_ic = str(year)
    month_ic = str(month).zfill(2)

    # environment variables
    BUCKET = os.getenv('DM_BUCKET')

    print('Generating input file list.')
    print()
    # create file list
    dates = pd.date_range(start='1991-01-01', end=f'{year_ic}-{month_ic}-01', freq='MS')
    h3_files = sorted(
        [
            f'gs://{BUCKET}/era5/monthly/water_balance_hamon_percentiles/era5_water-balance-perc-w3_bl-1991-2020_mon_{date.strftime("%Y-%m-%d")}.nc'
            for date in dates
        ]
    )
    h12_files = sorted([file.replace('w3', 'w12') for file in h3_files])

    forecast_files = [
        f'gs://{BUCKET}/nmme/ensemble/water_balance_hamon_percentiles/nmme_ensemble_water-balance-perc-w{window}_mon_ic-{year_ic}-{month_ic}-01_leads-6.nc'
        for window in [3, 12]
    ]
    f3_file = [file for file in forecast_files if 'w3' in file][0]
    f12_file = [file for file in forecast_files if 'w12' in file][0]

    print('Opening data.')
    # open historical data for both integration windows
    # parallelize data reads
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
    f3 = open_dataset(f3_file)
    f3 = process_dataset(f3)
    f3 = f3.rename({'50%': 'perc'})
    f3 = f3[['time', 'y', 'x', 'spatial_ref', '5%', '20%', 'perc', '80%', '95%']]

    print('    Opening F12 data...')
    print()
    f12 = open_dataset(f12_file)
    f12 = process_dataset(f12)
    f12 = f12.rename({'50%': 'perc'})
    f12 = f12[['time', 'y', 'x', 'spatial_ref', '5%', '20%', 'perc', '80%', '95%']]

    dataset_dict = {
        'h3': h3,
        'h12': h12,
        'f3': f3,
        'f12': f12,
    }

    print('Scaling data from [0, 1] to [0, 100].')
    dataset_dict = {name: scale_percentiles(ds) for name, ds in dataset_dict.items()}
    print()

    print('Saving Zarr stores used for analysis.')
    # save the data as zarr stores that we will use for analysis
    for dataset in dataset_dict:
        print(f'    Saving {dataset.upper()} data...')
        save_to = f'gs://{BUCKET}/zarr/analysis/wb-{dataset}-{year_ic}-{month_ic}-01.zarr'
        dataset_dict[dataset].to_zarr(
            save_to,
            consolidated=True,
            zarr_format=2,
            mode='w',
        )
    print()

    print('Saving Zarr stores used for visualization.')
    # next, save the data as zarr stores that we will use for visualization
    # first, we need to save their time coordinates as object arrays
    dataset_dict = {name: format_time_as_dates(ds) for name, ds in dataset_dict.items()}

    # next, calculate the number of zoom levels to use for the output Zarr
    pixels_per_tile = 128
    longitude_length = h3.perc.x.shape[0]
    max_levels = round(np.sqrt(longitude_length / pixels_per_tile)) + 1
    levels = max_levels

    # create pyramids for each dataset, then save the pyramid to zarr
    for dataset in dataset_dict:
        print(f'    Saving {dataset.upper()} data...')
        save_to = f'gs://{BUCKET}/zarr/viz/wb-{dataset}-{year_ic}-{month_ic}-01.zarr'
        pyramid_to_zarr(dataset_dict[dataset], levels, save_to)
    print()

    print('Done!')
    print()

    # ---------------------------------------------------------------------------
    end = timeit.default_timer()
    print(f"Time to complete: {(end - start) / 3600 :.5f} hours")


if __name__ == '__main__':
    drought_pipeline()
