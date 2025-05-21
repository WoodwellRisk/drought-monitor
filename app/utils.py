import shapely
import geopandas as gpd
import xarray as xr


def process_dataset(ds):
    """
    Take in an Xarray dataset, rename the latitude and longitude columns, and shift the latitudes by 180 degrees.
    """
    dataset = ds.rename({ 'longitude':'x','latitude':'y'})
    dataset.rio.write_crs("epsg:4326", inplace=True)
    dataset.coords['x'] = (dataset.coords['x'] + 180) % 360 - 180
    dataset = dataset.sortby(dataset.x)

    return dataset


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