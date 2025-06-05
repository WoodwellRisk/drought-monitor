import numpy as np
import shapely
import geopandas as gpd
import xarray as xr


def shift_data(ds):
    """
    Take in an Xarray dataset and shift the latitudes by 180 degrees.
    """
    ds.coords['x'] = (ds.coords['x'] + 180) % 360 - 180
    ds = ds.sortby(ds.x)

    return ds


def open_production_data(path):
    """
    Read in a crop production raster, rename the band data, and shift the latitude and longitude columns 
    """
    production = xr.open_dataset(path).sel(band=1)
    production = production.rename_vars({'band_data': 'production'})
    production.rio.write_crs(4326, inplace=True)
    production = shift_data(production)
    production = xr.where(production <= 0, np.nan, production)
    
    return production


def create_bbox_from_coords(x_min, x_max, y_min, y_max, crs=4326):
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