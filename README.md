[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://github.com/WoodwellRisk/drought-monitor/blob/main/LICENSE)

# Woodwell Risk Drought Monitor and Forecast
This site displays near real-time moisture anomalies along with an experimental 6-month forecast. Anomalies are measured as water balance percentiles relative to levels from 1991 to 2020. Values close to 0.5 represent normal conditions. Values below and above that mid-value indicate dryer- and wetter-than-normal conditions, respectively. Moisture anomalies are monitored on a monthly basis, from 2001 to present.

## Python environment
To recreate the conda environment we use in this repository, please run:
```
conda env create -f environment.yml
```
And to activate the environment:
```
conda activate shiny
```

## Run the app locally
To start a local server and see the app, please run the following command from within the `app/` directory:
```python
shiny run --reload drought.py
```

## Data sources and processing steps
### Vector data
National and state outlines were downloaded from [Natural Earth](https://www.naturalearthdata.com/). Crop masks were created using a modified version of the [SPAM 2020](https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi:10.7910/DVN/SWPENT) combined rainfed- and irrigated production data for specific crops.

### Raster data
The temperature, precipitation, and potential evapotranspiration data used to create the water balance index come from [ERA5 monthly averaged data](https://cds.climate.copernicus.eu/stac-browser/collections/reanalysis-era5-single-levels-monthly-means?.language=en) and were downloaded using the Copernicus Climate Data Store (CDS) Application Program Interface (API), or [CDS API](https://cds.climate.copernicus.eu/how-to-api).

For back-end data analysis/transformation of `NetCDF` and `TIF` files, we used Python and R.
