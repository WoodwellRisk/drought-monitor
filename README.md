[mit license]: https://badgen.net/badge/license/MIT/blue
![MIT License][]

# Woodwell Risk Drought Monitor

## Data sources
...

## Processing steps
### Vector data
All `GeoPackage` files were converted to `GeoJSON` format in [`GeoPandas`](https://geopandas.org/en/stable/docs/reference/api/geopandas.GeoDataFrame.to_file.html). From there, we used [`Tippecanoe`](https://github.com/mapbox/tippecanoe) to convert the `GeoJSON` files to Mapbox `.mbtiles` format and used the Mapbox tool [`mbutil`](https://github.com/mapbox/mbutil) to convert those tiles to `.pbf` format. 

### Raster data
For back-end data analysis/transformation of `NetCDF` and `TIF` files, we used Python and R. Those rasters were then converted to `Zarr` pyramids using CarbonPlan's [`ndpyramid`](https://github.com/carbonplan/ndpyramid/tree/main) package.

## Acknowledgements
This site's interface and functionality rely heavily on code developed by <a href='https://carbonplan.org/' target='_blank'>CarbonPlan</a>. Specifically, we used the <a href='https://github.com/carbonplan/maps' target='_blank'>`maps`</a>, <a href='https://github.com/carbonplan/components' target='_blank'>`components`</a>, and <a href='https://github.com/carbonplan/layouts' target='_blank'>`layouts`</a> libraries. We took inspiration from CarbonPlan's <a href="https://github.com/carbonplan/forest-risks-web" target="_blank">`forest-risks-web`</a> code repository to create an updated and modified user interface for this data viewer. Additionally, we modified the <ExpandingSection /> component from the <a href="https://github.com/carbonplan/prototype-maps" target="_blank">`prototype-maps`</a> repository. You can read more about CarbonPlan's research and software development work <a href="https://carbonplan.org/research" target="_blank">here</a>.
