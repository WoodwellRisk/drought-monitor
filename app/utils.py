import functools

import gcsfs
import geopandas as gpd
import pandas as pd
import shapely
import xarray as xr

# calculate the initial conditions from today's year and month
# in general, the month (and potentially year) roll back one month
# for example: if we are producing the forecast in january,
# then the initial conditions are from december of the previous year

# this is what we would like to do,
# except that it would roll over in the new month before we have the new data
# today = datetime.today()
# year = today.year
# month = today.month
year = 2026
month = 7

if month == 1:
    month = 12
    year = year - 1
else:
    month -= 1

month_ic = str(month) if month >= 10 else '0' + str(month)
year_ic = str(year)

# generate the list of date we expect to find for historical data
historical_dates = [
    date.strftime('%Y-%m-%d')
    for date in pd.date_range(start='1991-01-01', end=f'{year_ic}-{month_ic}-01', freq='MS')
]
forecast_dates = [
    date.strftime('%Y-%m-%d')
    for date in pd.date_range(start=f'{year_ic}-{month_ic}-01', freq='MS', periods=7)
][1:]

bucket = 'drought-monitor'


def create_bbox_from_coords(
    x_min: float, y_min: float, x_max: float, y_max: float, crs: int = 4326
) -> gpd.GeoDataFrame:
    """
    Create a GeoPandas GeoDataFrame from a list of coordinates with the CRS specified on input.
    """
    top_left = (x_min, y_max)
    top_right = (x_max, y_max)
    bottom_left = (x_min, y_min)
    bottom_right = (x_max, y_min)

    bbox_geom = shapely.Polygon([top_left, top_right, bottom_right, bottom_left])
    bbox = gpd.GeoDataFrame(geometry=[bbox_geom], crs=crs)

    return bbox


# open historical and forecast data for both integration windows
@functools.lru_cache(maxsize=2)
def load_historical_wb(window: str) -> xr.Dataset:
    return xr.open_dataset(
        f'gs://{bucket}/zarr/analysis/wb-h{window}-{year_ic}-{month_ic}-01.zarr',
        engine='zarr',
        consolidated=True,
        decode_coords='all',
    ).compute()


@functools.lru_cache(maxsize=2)
def load_forecast_wb(window: str) -> xr.Dataset:
    return xr.open_dataset(
        f'gs://{bucket}/zarr/analysis/wb-f{window}-{year_ic}-{month_ic}-01.zarr',
        engine='zarr',
        consolidated=True,
        decode_coords='all',
    ).compute()[['5%', '20%', 'perc', '80%', '95%']]


# lazy load country boundary layer
@functools.lru_cache(maxsize=1)
def load_countries() -> gpd.GeoDataFrame:
    return gpd.read_parquet(f'gs://{bucket}/vector/countries.parquet')


# lazy load country boundary layer
@functools.lru_cache(maxsize=1)
def load_states() -> gpd.GeoDataFrame:
    return gpd.read_parquet(f'gs://{bucket}/vector/states.parquet')


# lazy load crop extent vector
@functools.lru_cache(maxsize=10)
def load_crop_extent_vector(crop_name: str) -> None | gpd.GeoDataFrame:
    if crop_name == '' or crop_name == 'none':
        return None
    return gpd.read_parquet(
        f'gs://{bucket}/vector/{crop_name}.parquet',
    )


# lazy load crop production raster
@functools.lru_cache(maxsize=10)
def load_crop_production_raster(crop_name: str) -> None | xr.Dataset:
    if crop_name == '' or crop_name == 'none':
        return None
    return (
        xr.open_dataset(
            f'gs://{bucket}/zarr/spam-crop-production.zarr',
            engine='zarr',
            consolidated=True,
        )
        .sel(crop=crop_name)
        .production.compute()
    )
