import functools
import os
from datetime import datetime

import gcsfs
import geopandas as gpd
import pandas as pd
import shapely
import xarray as xr

# calculate the initial conditions from today's day, month, and year
# in general, the month (and potentially year) roll back one month
# however, right before the update occurs, there are times when the month looks back two months
target_year = 2026
target_month = 10

if target_month == 1:
    target_month = 12
    target_year = target_year - 1
else:
    target_month -= 1

year_ic = str(target_year)
month_ic = str(target_month).zfill(2)

# generate the list of date we expect to find for historical data
historical_dates = [
    date.strftime('%Y-%m-%d')
    for date in pd.date_range(start='1991-01-01', end=f'{year_ic}-{month_ic}-01', freq='MS')
]
forecast_dates = [
    date.strftime('%Y-%m-%d')
    for date in pd.date_range(start=f'{year_ic}-{month_ic}-01', freq='MS', periods=7)
][1:]

BUCKET = os.getenv('DM_BUCKET')


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
    ds = xr.open_dataset(
        f'gs://{BUCKET}/zarr/analysis/wb-h{window}-{year_ic}-{month_ic}-01.zarr',
        engine='zarr',
        consolidated=True,
        decode_coords='all',
    )

    return ds


@functools.lru_cache(maxsize=2)
def load_forecast_wb(window: str) -> xr.Dataset:
    ds = xr.open_dataset(
        f'gs://{BUCKET}/zarr/analysis/wb-f{window}-{year_ic}-{month_ic}-01.zarr',
        engine='zarr',
        consolidated=True,
        decode_coords='all',
    )[['5%', '20%', 'perc', '80%', '95%']]

    return ds


# lazy load country layer
@functools.lru_cache(maxsize=1)
def load_countries() -> gpd.GeoDataFrame:
    return gpd.read_parquet(f'gs://{BUCKET}/vector/countries.parquet')


# lazy load states layer
@functools.lru_cache(maxsize=1)
def load_states() -> gpd.GeoDataFrame:
    return gpd.read_parquet(f'gs://{BUCKET}/vector/states.parquet')


# lazy load crop extent vector
@functools.lru_cache(maxsize=10)
def load_crop_extent_vector(crop_name: str) -> None | gpd.GeoDataFrame:
    if crop_name == '' or crop_name == 'none':
        return None
    return gpd.read_parquet(
        f'gs://{BUCKET}/vector/{crop_name}.parquet',
    )


# lazy load crop production raster
@functools.lru_cache(maxsize=10)
def load_crop_production_raster(crop_name: str) -> None | xr.Dataset:
    if crop_name == '' or crop_name == 'none':
        return None
    return (
        xr.open_dataset(
            f'gs://{BUCKET}/zarr/spam-crop-production.zarr',
            engine='zarr',
            consolidated=True,
        )
        .sel(crop=crop_name)
        .production
    )


@functools.lru_cache(maxsize=20)
def load_clipped_wb(window: str, cname: str, sname: str) -> tuple:
    """
    Compute and cache the historical and forecast water balance,
    clipped to a country or state's extext.
    """
    historical = load_historical_wb(window)
    forecast = load_forecast_wb(window)

    country = load_countries().query(" name == @cname ")
    state = load_states().query(" name == @sname and country == @cname ")
    boundary = country if sname == 'All' else state

    historical = historical.rio.clip(boundary.geometry, all_touched=True, drop=True).compute()
    forecast = forecast.rio.clip(boundary.geometry, all_touched=True, drop=True).compute()

    return historical, forecast


@functools.lru_cache(maxsize=50)
def load_clipped_production(cname: str, sname: str, crop: str) -> xr.DataArray:
    """
    Compute and cache the crop production raster, clipped to a
    country or state's extent.
    """
    country = load_countries().query(" name == @cname ")
    state = load_states().query(" name == @sname and country == @cname ")
    boundary = country if sname == 'All' else state

    production = load_crop_production_raster(crop).rio.write_crs(4326)
    return production.rio.clip(boundary.geometry, all_touched=True, drop=True).compute()
