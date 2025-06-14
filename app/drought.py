import asyncio
import io
import glob
import json

import numpy as np 
import pandas as pd
import shapely
import geopandas as gpd
import xarray as xr
import rioxarray

import matplotlib
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import matplotlib.dates as mdates
import matplotlib.font_manager as font_manager

import plotly.express as px
import plotly.graph_objects as go
from shiny import App, Inputs, Outputs, Session, ui, render, reactive
from shinywidgets import render_plotly, render_widget, output_widget

from pathlib import Path

from utils import *

# shiny run --reload drought.py

# open historical and forecast data for both integration windows
h3 = xr.open_dataset(Path(__file__).parent /'mnt/data/zarr/h3.zarr', engine='zarr', consolidated=True, decode_coords="all", chunks=None,).compute()
h12 = xr.open_dataset(Path(__file__).parent /'mnt/data/zarr/h12.zarr', engine='zarr', consolidated=True, decode_coords="all", chunks=None,).compute()
f3 = xr.open_dataset(Path(__file__).parent /'mnt/data/zarr/f3.zarr', engine='zarr', consolidated=True, decode_coords="all", chunks=None,).compute()
f12 = xr.open_dataset(Path(__file__).parent /'mnt/data/zarr/f12.zarr', engine='zarr', consolidated=True, decode_coords="all", chunks=None,).compute()

# the data variables can come back in a different order when you read in the Zarr instead of the NetCDF
f3 = f3[['mean', 'mode', 'agree', '5%', '20%', 'perc', '80%', '95%']]
f12 = f12[['mean', 'mode', 'agree', '5%', '20%', 'perc', '80%', '95%']]

# open country boundary layer
countries = gpd.read_parquet(Path(__file__).parent / 'mnt/data/vector/countries.parquet')

# open crop polygon layers
barley = gpd.read_parquet(Path(__file__).parent / 'mnt/data/vector/barley.parquet')
cocoa = gpd.read_parquet(Path(__file__).parent / 'mnt/data/vector/cocoa.parquet')
coffee = gpd.read_parquet(Path(__file__).parent / 'mnt/data/vector/coffee.parquet')
cotton = gpd.read_parquet(Path(__file__).parent / 'mnt/data/vector/cotton.parquet')
maize = gpd.read_parquet(Path(__file__).parent / 'mnt/data/vector/maize.parquet')
rice = gpd.read_parquet(Path(__file__).parent / 'mnt/data/vector/rice.parquet')
soy = gpd.read_parquet(Path(__file__).parent / 'mnt/data/vector/soybean.parquet')
sugarcane = gpd.read_parquet(Path(__file__).parent / 'mnt/data/vector/sugarcane.parquet')
wheat = gpd.read_parquet(Path(__file__).parent / 'mnt/data/vector/wheat.parquet')

# open crop raster layers
barley_production = open_production_data(Path(__file__).parent / 'mnt/data/spam/crop_production_era5-grid_barley.tif')
cocoa_production = open_production_data(Path(__file__).parent / 'mnt/data/spam/crop_production_era5-grid_cocoa.tif')
coffee_production = open_production_data(Path(__file__).parent / 'mnt/data/spam/crop_production_era5-grid_coffee-all.tif')
cotton_production = open_production_data(Path(__file__).parent / 'mnt/data/spam/crop_production_era5-grid_cotton.tif')
maize_production = open_production_data(Path(__file__).parent / 'mnt/data/spam/crop_production_era5-grid_maize.tif')
rice_production = open_production_data(Path(__file__).parent / 'mnt/data/spam/crop_production_era5-grid_rice.tif')
soy_production = open_production_data(Path(__file__).parent / 'mnt/data/spam/crop_production_era5-grid_soybean.tif')
sugarcane_production = open_production_data(Path(__file__).parent / 'mnt/data/spam/crop_production_era5-grid_sugarcane.tif')
wheat_production = open_production_data(Path(__file__).parent / 'mnt/data/spam/crop_production_era5-grid_wheat.tif')

# point the app to the static files directory
static_dir = Path(__file__).parent / "www"
# get the font based on the path
ginto = font_manager.FontProperties(fname='./www/GintoNormal-Regular.ttf')
ginto_medium = font_manager.FontProperties(fname='./www/GintoNormal-Medium.ttf')

app_ui = ui.page_fluid(
    # css
     ui.tags.head(
        ui.include_css(static_dir / 'stylesheet.css'),        
        ui.include_js('./scripts/reset-sidebar-visibility.js', method='inline'),
        ui.include_js('./scripts/settings-button-click.js', method='inline'),
    ),

    ui.div({'id': 'layout'},

        ui.div({'id': 'navbar'},
            ui.div({'id': 'logo-container'}, 
                ui.div({'id': 'logo-inner-container'},
                    ui.img(src='woodwell-risk.png', width='45px', alt='Woodwell Climate Research Center Risk group logo'),
                    ui.p({'id': 'org-title'}, 'Woodwell Risk'),
                ),
            ),
            ui.div({'id': 'menu-container'},
                ui.div({'id': 'menu-inner-container'},
                ui.input_action_button("about_button", "About",),
                ui.input_action_button("settings_button", "Settings", onclick="onSettingsClick()"),
                ),
            ),
        ),

        # wrapper container for sidebar and main panel
        ui.div({'id': 'container'},
            # sidebar
            ui.div({'id': 'sidebar-container', 'class': 'show'},
                ui.div({'id': 'sidebar'}, 
                    ui.div({'id': 'sidebar-inner-container'},

                        ui.div({'class': 'select-label-container'},
                            ui.p({'class': 'select-label'}, 'Select an integration window:')
                        ),
                        ui.input_select('window_select', '', {3:'3 month', 12:'12 month'}, size=2),

                        ui.div({'class': 'select-label-container'},
                            ui.p({'class': 'select-label'}, 'Select a country:')
                        ),
                        ui.input_text("country_filter", label='', placeholder='Filter by name'),
                        # https://shiny.posit.co/py/api/core/ui.update_select.html
                        ui.input_select('country_select', '', [], size=5),

                        ui.div({'class': 'select-label-container'},
                            ui.p({'class': 'select-label'}, 'Select a crop:')
                        ),
                        ui.input_select('crop_select', '', [], size=5),

                        ui.div({'id': 'process-data-container'},
                            ui.input_task_button("process_data_button", label="Run"),
                        ),

                    )
                ),
            ),

            # figures and tables
            ui.div({"id": "main-container"},
                ui.panel_conditional(
                    "input.about_button > input.close_about_button",
                    ui.div({'id': 'about-inner-container'},
                        ui.div({'id': 'about-header'},
                            ui.input_action_button("close_about_button", "X"),
                        ),
                        ui.div({'id': 'about-body'},
                            ui.markdown(
                                """
                                ## Water balance
                                This site displays near real-time moisture anomalies along with an experimental 6-month forecast. 
                                Anomalies are measured as water balance percentiles relative to levels from 1991 to 2020. 
                                Values close to 0.5 represent normal conditions. Values below and above that mid-value indicate dryer- and wetter-than-normal conditions, respectively. 
                                Moisture anomalies are monitored on a monthly basis, from 2001 to present.


                                ## Applications
                                An integration window of 3 months is well suited for applications in agriculture, where shorter cycles of water balance are important. 
                                For sectors like the hydropower industry where longer-term patterns in water balance are more relevant, an integration window of 12 months is more appropriate.


                                ## Data sources
                                The water balance layers were created using <a href="https://cds.climate.copernicus.eu/stac-browser/collections/reanalysis-era5-single-levels-monthly-means?.language=en" target="_blank">ERA5 monthly averaged data</a>.

                                National and state outlines were downloaded from <a href="https://www.naturalearthdata.com/" target="_blank">Natural Earth</a>. 
                                Crop masks were created using a modified version of the <a href="https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi:10.7910/DVN/SWPENT" target="_blank">SPAM 2020</a> combined rainfed- and irrigated production data for specific crops.

                                ## Woodwell Risk
                                You can find out more about the Woodwell Risk group and the work that we do on our <a href="https://www.woodwellclimate.org/research-area/risk/" target="_blank">website</a>. 
                                Whenever possible, we publish our <a href="https://woodwellrisk.github.io/" target="_blank">methodologies</a> and <a href="https://github.com/WoodwellRisk" target="_blank">code</a> on GitHub.
                                """
                            ),
                        ),
                    ),
                    {'id': 'about-container'},
                ), 

                ui.div({'id': 'main'},
                ui.navset_tab(
                    ui.nav_panel('Timeseries', 
                        ui.div({'id': 'download-timeseries-container', 'class': 'download-container'},
                            ui.download_link("download_timeseries_link", 'Download timeseries')
                        ),
                        ui.div({'id': 'timeseries-container'},
                            ui.div({'id': 'timeseries-toggle-container'},
                                ui.input_checkbox("historical_checkbox", "Historical", True),
                                ui.input_checkbox("forecast_checkbox", "Forecast", True),
                            ),
                            ui.card({'id': 'timeseries-inner-container'},
                                ui.output_plot('timeseries', width='100%', height='100%'),
                            ),
                        ),
                        
                        ui.div({'id': 'download-csv-container', 'class': 'download-container'},
                            ui.download_link("download_csv_link", 'Download CSV')
                        ),
                        ui.div({'id': 'timeseries-table-container'},
                            ui.output_data_frame("timeseries_table"),
                        ),

                        ui.busy_indicators.options(),
                    ),

                    ui.nav_panel('Crop maps', 
                        ui.div({'id': 'crop-map-container'},
                            output_widget('crop_map'),
                            # ui.output_ui('crop_map'),
                        ),

                        # ui.div({'id': 'iframe-container'},
                        #     ui.tags.iframe(src='https://woodwellrisk.github.io/drought-monitor', height='100%', width='100%')
                        # )
                    ),

                    ui.nav_panel('Forecast map', 
                        ui.div({'id': 'forecast-map-container'},
                            ui.output_ui('forecast_map'),
                        ),
                    ),

                    id='tab_menu'
                ),
                
                ),
            ),
        ),
    ),
)

def server(input: Inputs, output: Outputs, session: Session):
    
    countries_list = sorted(countries.name.values)
    country_options = reactive.value(countries_list)

    crop_list = [
        'None', 'Barley', 'Cocoa', 'Coffee', 'Cotton',
        'Maize', 'Rice', 'Soy', 'Sugarcane', 'Wheat',
    ]
    crop_options = reactive.value(crop_list)
    crop_layer = reactive.value(None)
    crop_production = reactive.value(None)

    country_name = reactive.value('')
    crop_name = reactive.value('')
    filter_text = reactive.value('')
    bounds = reactive.value([])
    bbox = reactive.value([])
    
    # this is used in the the filename for downloading plots and tables, but
    # may also be used later in slider values
    forecast_date = '04-2025'

    # these values change the data between the 3-month and 12-month integration windows
    integration_window = reactive.value(input.window_select)

    h = reactive.value(None)
    f = reactive.value(None)

    # these values represent the data clipped to a specific area, used for the timeseries figures
    historical_wb = reactive.value(None)
    forecast_wb = reactive.value(None)

    # these values represent the data clipped to a specific area for the unweighted forecast map
    unweighted_historical_wb = reactive.value(None)
    unweighted_forecast_wb = reactive.value(None)

    # values for quickly storing and downloading figures and tables
    timeseries_to_save = reactive.value(None)
    table_to_save = reactive.value(None)
    add_download_links = reactive.value(True)
    crop_figure = reactive.value(None)

    display_bounds_error = reactive.value(False)


    @reactive.effect
    @reactive.event(input.window_select)
    def update_integration_window():
        window_size = input.window_select()
        integration_window.set(window_size)


    @reactive.effect
    @reactive.event(integration_window)
    def update_rasters():
        window_size = integration_window()

        if(window_size == '3'):
            h.set(h3)
            f.set(f3)
        elif(window_size == '12'):
            h.set(h12)
            f.set(f12)
        else:
            raise ValueError("The integration window should be either 3 or 12 months.")


    @reactive.effect
    @reactive.event(input.about_button)
    def action_button_click():
        ui.update_action_button("about_button", disabled=True)


    @reactive.effect
    @reactive.event(input.close_about_button)
    def action_button_close_click():
        ui.update_action_button("about_button", disabled=False)
    

    @reactive.effect
    @reactive.event(input.country_filter)
    def update_filter_text():
        filter_text.set(input.country_filter())


    @render.text
    def country_filter_text():
        return filter_text()


    @reactive.effect
    @reactive.event(filter_text)
    def update_country_list():
        query = filter_text()
        country_options.set(countries_list if query == '' else [value for value in countries_list if query.lower() in value.lower()])
    

    @reactive.effect
    @reactive.event(country_options)
    def update_country_select():
        new_options = country_options()
        ui.update_select('country_select', label=None, choices=new_options, selected=None)


    @reactive.effect
    @reactive.event(input.country_select)
    def update_country_name():
        new_country = input.country_select()
        country_name.set(new_country)


    @render.text
    def country_name_text():
        return country_name()
    

    @reactive.effect
    @reactive.event(country_name)
    def update_bounds():
        name = country_name()

        # on app start or page reload, these variables will be empty
        if(name == ''):
            return

        # https://stackoverflow.com/questions/1894269/how-to-convert-string-representation-of-list-to-a-list#1894296
        new_bounds = json.loads(countries.query(" name == @name ").bbox.values[0])
        bounds.set(new_bounds)

        xmin, ymin, xmax, ymax = new_bounds
        new_bbox = create_bbox_from_coords(xmin, xmax, ymin, ymax)
        bbox.set(new_bbox)


    @render.text
    def country_bbox_text():
        return bounds()


    @reactive.effect
    @reactive.event(crop_options)
    def update_crop_select():
        new_options = crop_options()
        ui.update_select('crop_select', label=None, choices=new_options, selected=None)


    @reactive.effect
    @reactive.event(input.crop_select)
    def update_crop():
        new_crop = input.crop_select().lower()
        crop_name.set(new_crop)

        match new_crop:
            case '':
                crop_layer.set(None)
                crop_production.set(None)
            case 'none':
                crop_layer.set(None)
                crop_production.set(None)
            case 'barley':
                crop_layer.set(barley)
                crop_production.set(barley_production)
            case 'cocoa':
                crop_layer.set(cocoa)
                crop_production.set(cocoa_production)
            case 'coffee':
                crop_layer.set(coffee)
                crop_production.set(coffee_production)
            case 'cotton':
                crop_layer.set(cotton)
                crop_production.set(cotton_production)
            case 'maize':
                crop_layer.set(maize)
                crop_production.set(maize_production)
            case 'rice':
                crop_layer.set(rice)
                crop_production.set(rice_production)
            case 'soy':
                crop_layer.set(soy)
                crop_production.set(soy_production)
            case 'sugarcane':
                crop_layer.set(sugarcane)
                crop_production.set(sugarcane_production)
            case 'wheat':
                crop_layer.set(wheat)
                crop_production.set(wheat_production)


    @render.text
    def crop_name_text():
        return crop_name()


    @reactive.effect
    @reactive.event(input.process_data_button)
    def update_wb_data():
        crop = crop_name()
        crop_extent = crop_layer()
        # production = crop_production().rio.write_crs(4326, inplace=True)
        # production.rio.write_crs(4326, inplace=True)

        name = country_name()

        window_size = integration_window()

        historical = h()
        forecast = f()

        # on app start or page reload, these variables will be empty
        if(name == '' or crop == '' or historical is None or forecast is None):
        # if(name == '' or crop == ''):
            return

        xmin, ymin, xmax, ymax = bounds.get()
        bounding_box = bbox()
        country = countries.query(" name == @name ")

        # we have already filtered countries where we don't have data, so clipping by country extent 
        # should never produce a rioxarray.exceptions.NoDataInBounds error at this step
        historical = historical.rio.clip(country.geometry, all_touched=True, drop=True)
        historical = historical.assign_attrs({'crop': crop})

        forecast = forecast.rio.clip(country.geometry, all_touched=True, drop=True)
        forecast = forecast.assign_attrs({'crop': crop})

        if(crop == 'none'):
            display_bounds_error.set(False)
            historical_wb.set(historical)
            forecast_wb.set(forecast)
            unweighted_historical_wb.set(historical)
            unweighted_forecast_wb.set(forecast)

            return
        else: # we need to production weight the timeseries
            try:
                historical = historical.rio.clip(crop_extent.geometry, all_touched=True, drop=True)
                forecast = forecast.rio.clip(crop_extent.geometry, all_touched=True, drop=True)

                # sometimes, this is silently failing when there is no data to show, but instead returns an empty dataset
                if(historical.perc.isnull().all() or forecast.perc.isnull().all()):
                    print('No data in bounds, but silently failing!')
                    display_bounds_error.set(True)
                    historical_wb.set(None)
                    forecast_wb.set(None)
                    unweighted_historical_wb.set(None)
                    unweighted_forecast_wb.set(None)
                    return

                # but we don't need to production weight the forecast map data
                unweighted_historical_wb.set(historical)
                unweighted_forecast_wb.set(forecast)

                # clip production data to country extent, then standardize
                production = crop_production()
                production = production.rio.write_crs(4236)
                country_level_production = production.rio.clip(country.geometry, all_touched=True, drop=True)
                standardized_production = country_level_production / country_level_production.sum(skipna=True)
                standardized_production = standardized_production[['x', 'y', 'production']]

                # multiply water balance data by standardized production values
                historical = xr.merge([historical, standardized_production])
                historical = historical * historical.production

                forecast = xr.merge([forecast, standardized_production])
                forecast['mean'] = forecast['mean'] * forecast.production
                forecast['mode'] = forecast['mode'] * forecast.production
                forecast['5%'] = forecast['5%'] * forecast.production
                forecast['20%'] = forecast['20%'] * forecast.production
                forecast['perc'] = forecast['perc'] * forecast.production
                forecast['80%'] = forecast['80%'] * forecast.production
                forecast['95%'] = forecast['95%'] * forecast.production

                # next, multiply the water balance data by the number of rows in the dataset
                # in this case, it is the number of rows in the first (and every individual) month
                nrows_historical = historical.drop_vars('spatial_ref').to_dataframe().dropna().query(" time == @pd.to_datetime(@historical.time.values[0]) ").shape[0]
                nrows_forecast = forecast.drop_vars('spatial_ref').to_dataframe().dropna().query(" time == @pd.to_datetime(@forecast.time.values[0]) ").shape[0]
                print(f"NUMBER OF ROWS: {nrows_historical} {nrows_forecast}\n")
                
                historical *= nrows_historical
                
                forecast['mean'] = forecast['mean'] * nrows_forecast
                forecast['mode'] = forecast['mode'] * nrows_forecast
                forecast['5%'] = forecast['5%'] * nrows_forecast
                forecast['20%'] = forecast['20%'] * nrows_forecast
                forecast['perc'] = forecast['perc'] * nrows_forecast
                forecast['80%'] = forecast['80%'] * nrows_forecast
                forecast['95%'] = forecast['95%'] * nrows_forecast
                
                # lastly, drop the production row from the dataframes
                historical = historical.drop_vars('production')
                historical = historical[['time', 'x', 'y', 'perc']]

                forecast = forecast.drop_vars('production')
                forecast = forecast[['time', 'x', 'y', 'mean', 'mode', 'agree', '5%', '20%', 'perc', '80%', '95%']]

            except rioxarray.exceptions.NoDataInBounds:
                print('No data in bounds!')
                display_bounds_error.set(True)
                historical_wb.set(None)
                forecast_wb.set(None)
                unweighted_historical_wb.set(None)
                unweighted_forecast_wb.set(None)
                return

            except Exception as error:
                print(error)

            display_bounds_error.set(False)
            historical_wb.set(historical)
            forecast_wb.set(forecast)


    @reactive.effect
    @reactive.event(display_bounds_error)
    def update_bounds_error():
        crop = crop_name()
        name = country_name()
        
        if(crop == '' or name == ''):
            return

        show_error = display_bounds_error()
        
        if(show_error):
            ui.insert_ui(
                ui.div({'class': 'bounds-error-container'},
                    ui.div({'class': 'bounds-error'},
                        # f'No water balance data to show. This is likely because {crop} is not grown in {name} or the data resoultion is too low.'
                        'No water balance data to show. This is likely because the crop you chose is not grown in the country in question or the data resoultion is too low.'

                    ),
                ),
                selector='#forecast-map-container',
                where='beforeEnd',
            )

            ui.insert_ui(
                ui.div({'class': 'bounds-error-container'},
                    ui.div({'class': 'bounds-error'},
                        # f'No water balance data to show. This is likely because {crop} is not grown in {name} or the data resoultion is too low.'
                        'No water balance data to show. This is likely because the crop you chose is not grown in the country in question or the data resoultion is too low.'

                    ),
                ),
                selector='#timeseries-inner-container',
                where='beforeEnd',
            )
        else:
            ui.remove_ui('.bounds-error-container', multiple=True)


    @reactive.effect
    @reactive.event(historical_wb, forecast_wb, input.historical_checkbox, input.forecast_checkbox)
    def update_dataframe():
        crop = crop_name()
        production = crop_production()
        name = country_name()
        window_size = integration_window()

        show_historical = input.historical_checkbox()
        show_forecast = input.forecast_checkbox()

        historical = historical_wb()
        forecast = forecast_wb()

        # if the xarray data is empty (on initial load) or if the toggles controlling which datasets to show are both false, then return empty dataframe
        if((forecast is None and historical is None) or (show_forecast == False and show_historical == False)):
            df = pd.DataFrame({
                'country': [], 'type': [], 'crop': [], 'time': [], 'percentile': [], 'agreement': [],
                '5%': [], '20%': [], '80%': [], '95%': [],
                })
        else:
            # # else, we need to check if we need to production-weight the timeseries
            # if(crop == '' or crop == 'none'):
            #     pass
            # else:
            #     # clip production data to country extent, then standardize
            #     country = countries.query(" name == @name ")
            #     production = production.rio.write_crs(4236)
            #     country_level_production = production.rio.clip(country.geometry, all_touched=True, drop=True)
            #     standardized_production = country_level_production / country_level_production.sum(skipna=True)
            #     standardized_production = standardized_production[['x', 'y', 'production']]

            #     # multiply water balance data by standardized production values
            #     historical = xr.merge([historical, standardized_production])
            #     historical = historical * historical.production

            #     forecast = xr.merge([forecast, standardized_production])
            #     forecast['mean'] = forecast['mean'] * forecast.production
            #     forecast['mode'] = forecast['mode'] * forecast.production
            #     forecast['5%'] = forecast['5%'] * forecast.production
            #     forecast['20%'] = forecast['20%'] * forecast.production
            #     forecast['perc'] = forecast['perc'] * forecast.production
            #     forecast['80%'] = forecast['80%'] * forecast.production
            #     forecast['95%'] = forecast['95%'] * forecast.production

            #     # next, multiply the water balance data by the number of rows in the dataset
            #     # in this case, it is the number of rows in the first (and every individual) month
            #     nrows_historical = historical.drop_vars('spatial_ref').to_dataframe().dropna().query(" time == @pd.to_datetime(@historical.time.values[0]) ").shape[0]
            #     nrows_forecast = forecast.drop_vars('spatial_ref').to_dataframe().dropna().query(" time == @pd.to_datetime(@forecast.time.values[0]) ").shape[0]
            #     print("NUMBER OF ROWS")
            #     print(nrows_historical, nrows_forecast)
            #     print()

            #     # assert(nrows_historical == nrows_forecast)
                
            #     historical *= nrows_historical
                
            #     forecast['mean'] = forecast['mean'] * nrows_forecast
            #     forecast['mode'] = forecast['mode'] * nrows_forecast
            #     forecast['5%'] = forecast['5%'] * nrows_forecast
            #     forecast['20%'] = forecast['20%'] * nrows_forecast
            #     forecast['perc'] = forecast['perc'] * nrows_forecast
            #     forecast['80%'] = forecast['80%'] * nrows_forecast
            #     forecast['95%'] = forecast['95%'] * nrows_forecast
                
            #     # lastly, drop the production row from the dataframes
            #     historical = historical.drop_vars('production')
            #     historical = historical[['time', 'x', 'y', 'perc']]

            #     forecast = forecast.drop_vars('production')
            #     forecast = forecast[['time', 'x', 'y', 'mean', 'mode', 'agree', '5%', '20%', 'perc', '80%', '95%']]

            #     print("HISTORICAL:")
            #     print(historical)
            #     print()

            # include just historical
            if(show_historical == True and show_forecast == False):
                df = historical.mean(dim=['x', 'y']).drop_vars('spatial_ref').to_pandas().reset_index()
                df['perc'] = df['perc'].astype(float).round(4)
                df['agree'] = np.nan
                df['time'] = df['time'].dt.date
                df.columns = ['time', 'percentile', 'agreement']
                df['country'] = name
                df['crop'] = crop
                df['type'] = 'historical'
                df['window'] = int(window_size)
                df['5%'] = np.nan
                df['20%'] = np.nan
                df['80%'] = np.nan
                df['95%'] = np.nan
                
                df = df[['country', 'crop', 'type', 'window', 'time', 'percentile', 'agreement', '5%', '20%', '80%', '95%']].sort_values('time', ascending=False).reset_index(drop=True)
            
            # include just forecast
            elif(show_historical == False and show_forecast == True):
                df = forecast.mean(dim=['x', 'y']).drop_vars('spatial_ref').to_pandas().reset_index()
                # this is the 50% line in the forecast data
                df['perc'] = df['perc'].astype(float).round(4)
                df['mean'] = df['mean'].astype(float).round(4)
                df['mode'] = df['mode'].astype(float).round(4)
                df['agree'] = df['agree'].astype(float).round(4)
                df['5%'] = df['5%'].astype(float).round(4)
                df['20%'] = df['20%'].astype(float).round(4)
                df['80%'] = df['80%'].astype(float).round(4)
                df['95%'] = df['95%'].astype(float).round(4)
                df['time'] = df['time'].dt.date
                df.columns = ['time', 'mean', 'mode', 'agreement', '5%', '20%', 'percentile', '80%', '95%']
                df['country'] = name
                df['crop'] = crop
                df['type'] = 'forecast'
                df['window'] = int(window_size)
                
                df = df[['country', 'crop', 'type', 'window', 'time', 'percentile', 'agreement', '5%', '20%', '80%', '95%']].sort_values('time', ascending=False).reset_index(drop=True)

            # else both are active, include both
            else:
                df_historical = historical.mean(dim=['x', 'y']).drop_vars('spatial_ref').to_pandas().reset_index()
                df_historical['perc'] = df_historical['perc'].astype(float).round(4)
                df_historical['agree'] = np.nan
                df_historical['time'] = df_historical['time'].dt.date
                df_historical.columns = ['time', 'percentile', 'agreement']
                df_historical['country'] = name
                df_historical['crop'] = crop
                df_historical['type'] = 'historical'
                df_historical['window'] = int(window_size)
                df_historical['5%'] = np.nan
                df_historical['20%'] = np.nan
                df_historical['80%'] = np.nan
                df_historical['95%'] = np.nan
                df_historical = df_historical[['country', 'crop', 'type', 'window', 'time', 'percentile', 'agreement', '5%', '20%', '80%', '95%']]

                df_forecast = forecast.mean(dim=['x', 'y']).drop_vars('spatial_ref').to_pandas().reset_index()
                df_forecast['perc'] = df_forecast['perc'].astype(float).round(4)
                df_forecast['mean'] = df_forecast['mean'].astype(float).round(4)
                df_forecast['mode'] = df_forecast['mode'].astype(float).round(4)
                df_forecast['agree'] = df_forecast['agree'].astype(float).round(4)
                df_forecast['5%'] = df_forecast['5%'].astype(float).round(4)
                df_forecast['20%'] = df_forecast['20%'].astype(float).round(4)
                df_forecast['80%'] = df_forecast['80%'].astype(float).round(4)
                df_forecast['95%'] = df_forecast['95%'].astype(float).round(4)
                df_forecast['time'] = df_forecast['time'].dt.date
                df_forecast.columns = ['time', 'mean', 'mode', 'agreement', '5%', '20%', 'percentile', '80%', '95%']
                df_forecast['country'] = name
                df_forecast['crop'] = crop
                df_forecast['type'] = 'forecast'
                df_forecast['window'] = int(window_size)
                df_forecast = df_forecast[['country', 'crop', 'type', 'window', 'time', 'percentile', 'agreement', '5%', '20%', '80%', '95%']]

                df = pd.concat([df_historical, df_forecast]).sort_values('time', ascending=False).reset_index(drop=True)

        table_to_save.set(df)
        return df


    @reactive.effect
    @reactive.event(table_to_save)
    def set_download_button_states():
        """
        If there is nothing to download, then we want to disable the user's ability to download empty figures and tables.
        """
        df = table_to_save()

        if df.empty:
            ui.remove_ui(selector="#download_timeseries_link")
            ui.remove_ui(selector="#download_csv_link")
            add_download_links.set(True)
        else:
            if(add_download_links()):
                ui.insert_ui(
                    ui.download_link("download_timeseries_link", 'Download timeseries'),
                    selector="#download-timeseries-container",
                    where="beforeEnd",
                ),
                ui.insert_ui(
                    ui.download_link("download_csv_link", 'Download CSV'),
                    selector="#download-csv-container",
                    where="beforeEnd",
                ),
                add_download_links.set(False)


    @render.plot
    @reactive.event(table_to_save)
    def timeseries(alt="A graph showing a timeseries of historical and forecasted water balance"):
        # later if we want to make it so that we can dynamically change the timeframe:
        # https://plotly.com/python/range-slider/
        historical = historical_wb()
        forecast = forecast_wb()

        if(historical is None or forecast is None):
            return

        show_historical = input.historical_checkbox()
        show_forecast = input.forecast_checkbox()

        # df = update_dataframe()
        df = table_to_save()

        timeseries_color = '#1b1e23'
        high_certainty_color = '#f4c1c1'
        medium_certainty_color = '#f69a9a'

        legend_options = {
            'xdata': [0],
            'ydata': [0],
        }

        historical_label = Line2D(color=timeseries_color, markerfacecolor=timeseries_color, label='Historical', linewidth=1, **legend_options, )
        forecast_label = Line2D(color=timeseries_color, markerfacecolor=timeseries_color, label='Forecast', linestyle='--', linewidth=1, **legend_options)
        medium_certainty_label = Line2D(color=medium_certainty_color, markerfacecolor=medium_certainty_color, label='20-80%', linewidth=3, **legend_options)
        high_certainty_label = Line2D(color=high_certainty_color, markerfacecolor=high_certainty_color, label='5-95%', linewidth=3, **legend_options)
        legend_elements = []

        fig, ax = plt.subplots()

        # if both are true, we need to stitch together the historical and forecast timeseries
        if(show_historical == True and show_forecast == True):
            df_historical = df.query(" type == 'historical' ")
            # this is the 6-month forecast plus the last data entry for historical data
            df_forecast = df.iloc[0:7, :]
            
            # forecast data needs to be plotted first because of the uncertainty bounds
            ax.fill_between(df_forecast['time'], df_forecast['5%'], df_forecast['95%'], color=high_certainty_color)
            ax.fill_between(df_forecast['time'], df_forecast['20%'], df_forecast['80%'], color=medium_certainty_color)
            ax.plot(df_forecast['time'], df_forecast['percentile'], color=timeseries_color, linestyle='--')
            ax.plot(df_historical['time'], df_historical['percentile'], color=timeseries_color)
            
            legend_elements = [historical_label, forecast_label, medium_certainty_label, high_certainty_label]

        if(show_historical == True and show_forecast == False):
            ax.plot(df['time'], df['percentile'], color=timeseries_color)
            
            legend_elements = [historical_label]

        if(show_historical == False and show_forecast == True):
            ax.fill_between(df['time'], df['5%'], df['95%'], color=high_certainty_color)
            ax.fill_between(df['time'], df['20%'], df['80%'], color=medium_certainty_color)
            ax.plot(df['time'], df['percentile'], color=timeseries_color, linestyle='--')

            forecast_date_format = mdates.DateFormatter('%m-%y')
            ax.xaxis.set_major_formatter(forecast_date_format)

            legend_elements = [forecast_label, medium_certainty_label, high_certainty_label]

        ax.set_xlabel('Time', fontproperties=ginto_medium)
        ax.set_ylabel('Mean water balance', fontproperties=ginto_medium)

        # use custom fonts for x and y axes labels
        for label in ax.get_xticklabels():
            label.set_fontproperties(ginto)
    
        for label in ax.get_yticklabels():
            label.set_fontproperties(ginto)

        ax.margins(0, 0)
        ax.set_ylim(-0.05, 1.05)

        if(not show_forecast and not show_historical):
            ax.set_xticks([0, 1, 2, 3, 4, 5])
            ax.set_xticklabels(['', '', '', '', '', ''])

        # you need both of these to change the colors
        fig.patch.set_facecolor('#f7f7f7')
        ax.set_facecolor('#f7f7f7')

        plt.tight_layout()
        fig.subplots_adjust(bottom=0.25)

        if(len(legend_elements) > 0):
            fig.legend(handles=legend_elements, ncols=len(legend_elements), loc='lower center', bbox_to_anchor=(0 if len(legend_elements) == 3 else 0.025, 0, 1, 0.5), fontsize='small', facecolor='white', frameon=False)

        timeseries_to_save.set(fig)
        return fig


    @render.download(filename=lambda: f'drought-timeseries-{country_name().lower()}-{"historical" if input.historical_checkbox() else ""}-{"forecast" if input.forecast_checkbox() else ""}-{"" if crop_name() == "none" else crop_name()}-{str(integration_window())+"month"}-{forecast_date}.png'.replace(' ', '-').replace('--', '-').replace('--', '-'))
    def download_timeseries_link():

        name = country_name()

        forecast = forecast_wb()
        historical = historical_wb()

        if(forecast is None and historical is None):
            return

        show_historical = input.historical_checkbox()
        show_forecast = input.forecast_checkbox()

        fig = timeseries_to_save()
        plt.figure(fig)
        ax = plt.gca()

        fig.patch.set_facecolor('white')
        ax.set_facecolor('white')

        if(show_historical == True and show_forecast == False):
            historical_and_forecast_label = 'Historical'
        elif(show_historical == False and show_forecast == True):
            historical_and_forecast_label = 'Forecasted'
        elif(show_historical == True and show_forecast == True):
            historical_and_forecast_label = 'Historical and forecasted'

        title = f'{historical_and_forecast_label} water balance for {name}'
        ax.set_title(title, fontproperties=ginto_medium)

        fig.subplots_adjust(top=0.9)

        with io.BytesIO() as buffer:
            plt.savefig(buffer, format="png", dpi=300)
            yield buffer.getvalue()


    # # @render.plot
    # # # @reactive.event(country)
    # # def forecast_map(alt="a map showing the borders of a country of interest"):
    # #     name = country_name()

    # #     # on app start or page reload, these variables will be empty
    # #     if(name == ''):
    # #         return

    # #     # plot_raster = None
    # #     xmin, ymin, xmax, ymax = bounds.get()
    # #     bounding_box = bbox()
    # #     plot_country = countries.query(" name == @name ")

    # #     # try:
    # #     #     # first clip by the bounding box to get the figure extent (drop=True)
    # #     #     # then clip by country geometry for just the data in that country (drop=False)
    # #     #     plot_raster = ds.rio.clip(bounding_box.geometry, all_touched=True, drop=True)
    # #     #     plot_raster = plot_raster.rio.clip(plot_country.geometry, all_touched=True, drop=False)
    # #     #     print(plot_raster)
    # #     #     plot_raster.perc.drop_vars('spatial_ref').plot(cmap='RdBu_r', add_colorbar=False, ax=ax)
    # #     # except:
    # #     #     print("No data in bounds")

    # #     # plotting
    # #     fig, ax = plt.subplots()

    # #     countries.plot(facecolor='white', edgecolor='none', ax=ax)
    # #     # if(plot_raster):
    # #     #     plot_raster.perc.drop_vars('spatial_ref').plot(cmap='RdBu_r', add_colorbar=False, ax=ax)
    # #     try:
    # #         # first clip by the bounding box to get the figure extent (drop=True)
    # #         # then clip by country geometry for just the data in that country (drop=False)
    # #         plot_raster = f().rio.clip(bounding_box.geometry, all_touched=True, drop=True)
    # #         plot_raster = plot_raster.rio.clip(plot_country.geometry, all_touched=True, drop=False)
    # #         plot_raster.perc.drop_vars('spatial_ref').plot(cmap='RdBu', add_colorbar=False, ax=ax)
    # #     except:
    # #         print("No data in bounds")
        
    # #     countries.plot(facecolor='none', edgecolor='black', ax=ax)
    # #     # plot_country.plot(facecolor='none', edgecolor='black', ax=ax)

    # #     ax.set_xlim(xmin, xmax)
    # #     ax.set_ylim(ymin, ymax)

    # #     # and this removes white background in figure
    # #     fig.patch.set_alpha(0)

    # #     return fig 

    # @render_plotly
    @render.ui
    @reactive.event(unweighted_forecast_wb)
    def forecast_map(alt="a map showing the borders of a country of interest"):

        name = country_name()
        country = countries.query(" name == @name ")
        forecast = unweighted_forecast_wb()

        if(name == '' or forecast is None):
            return

        config = {
            # 'staticPlot': False, 
            'displaylogo': False, 
            # 'displayModeBar': False, 
            'scrollZoom': True,
            # 'modeBarButtonsToRemove': ['zoom', 'pan', 'select', 'lasso2d', 'toImage']
            'modeBarButtonsToRemove': ['pan', 'select', 'lasso2d', 'toImage']

        }

        country = countries.query(" name == @name ")
        centroid = country.centroid.values[0]
        bbox = json.loads(country.bbox.values[0])
        bounding_box = create_bbox_from_coords(*bbox).to_geo_dict()

        max_bounds = max(abs(bbox[0] - bbox[2]), abs(bbox[1] - bbox[3])) * 111
        zoom = 11 - np.log(max_bounds)

        country_forecast = forecast.rio.clip(country.geometry, all_touched=True, drop=True)
        df = country_forecast['mean'].drop_vars('spatial_ref').to_dataframe().dropna().reset_index()
        df.columns = ['time', 'y', 'x', 'Percentile']

        forecast_dates = df.time.unique().tolist()
        formatted_dates = [date.strftime("%b-%Y") for date in forecast_dates]

        fig = px.scatter_map(
            data_frame = df, 
            lat = df.y, 
            lon = df.x, 
            color = df['Percentile'],
            color_continuous_scale = px.colors.diverging.RdYlBu, 
            # color_continuous_scale = px.colors.sequential.Plasma,
            range_color = [0, 1],
            hover_data = {'time': False, 'x': False, 'y': False, 'Percentile': ':.3f'},
            map_style = 'carto-positron-nolabels',
            zoom=zoom,
            height=445,
            animation_frame = 'time'
        )

        fig["layout"].pop("updatemenus")

        steps = []
        for idx in range(len(formatted_dates)):
            step = dict(
                method='animate',
                label=formatted_dates[idx]
            )
            steps.append(step)

        fig.update_layout(
            sliders=[{
                'currentvalue': {'prefix': 'Time: '},
                'len': 0.8,
                'pad': {'b': 10, 't': 0},
                'steps': steps,
                # 'transition': {'easing': 'circle-in'},
                'bgcolor': '#f7f7f7',
                'bordercolor': '#1b1e23',
                'activebgcolor': '#1b1e23',
                'tickcolor': '#1b1e23',
                'font': {'color': '#1b1e23'},
            }],
            margin=dict(l=0, r=0, t=0, b=0),
            paper_bgcolor='#f7f7f7',
        )

        fig.update_coloraxes(
            colorbar_title_side='right',
            colorbar_len=0.8,
            colorbar_thickness=20,
        )

        fig.update_layout(coloraxis_colorbar_x=0.01)

        fig.add_traces(
            px.scatter_geo(geojson=bounding_box).data
        )

        # figurewidget = go.FigureWidget(fig)
        # return figurewidget
        # return fig

        # https://stackoverflow.com/questions/78834353/animated-plotly-graph-in-pyshiny-express
        """
        The below is not working in CSS: the background color and border radius change, but not the padding.
        So I could try to directly change the HTML string to add the padding in myself.

        .maplibregl-ctrl-attrib-inner {
            background-color: lightgray;
            border-radius: 10px;
            padding: 2px 5px;
        }
        """

        # to save individual images later: https://github.com/plotly/plotly.py/issues/664
        return ui.HTML(fig.to_html(config=config, auto_play=False))


    # # @reactive.effect
    # # def _():
    # #     # map.widget.center = city_centers[input.center()]
    # #     print(forecast_map)


    @render_plotly
    def crop_map():
        crop = crop_name()
        crop_extent = crop_layer()

        config = {
            # 'staticPlot': False, 
            'displaylogo': False, 
            # 'displayModeBar': False, 
            'scrollZoom': True,
            # https://stackoverflow.com/questions/59817118/how-to-trigger-zoom-in-and-zoom-out-in-plotly-chart-using-user-created-on-click
            # https://plotly.com/javascript/zoom-events/
            'modeBarButtonsToRemove': ['zoom', 'pan', 'select', 'lasso2d', 'toImage'],
            'modeBarButtonsToAdd': ["zoomInGeo", "zoomInMap", "zoomInMapbox"],
            # 'modeBarButtonsToRemove': ['pan', 'select', 'lasso2d', 'toImage'] if crop == 'none' or crop == '' else ['zoom', 'pan', 'select', 'lasso2d'],
            # 'toImageButtonOptions': {
            #     'filename': f'{crop}_extent',
            #     'format': 'svg', # one of png, svg, jpeg, webp
            #     # 'height': 500,
            #     # 'width': 700,
            #     'height': None,
            #     'width': None,
            #     'scale': 1 # multiply title/legend/axis/canvas sizes by this factor
            # }
            # https://community.plotly.com/t/image-export-how-to-set-dpi-alternatively-how-to-scale-down-using-width-and-height/49536/2
        }

        fig = go.Figure(go.Scattermap())

        fig.update_layout(
            map = {'style': "carto-positron-nolabels",},
            margin = {'l':0, 'r':0, 'b':0, 't':0},
        )

        # save the figure (not the widget!) so that we can update the layers later
        # crop_figure.set(fig)

        # crop_map.save(fig) # ??
        # and then something later like:
        # fig = crop_map()
        # most likely: fig.update_layout(map = {...'layers': [{'source': crop_layer, 'type': 'fill', 'below': 'traces', 'color': 'royalblue', 'opacity': 0.7,}]},)
        # or: fig.add_traces(...)
        # return fig

        if(crop_extent is None):
        # if(crop == '' or crop == 'none'):
            figurewidget = go.FigureWidget(fig)
            figurewidget._config = config
            return figurewidget
        
        fig.update_layout(
            map = {
                'style': "carto-positron-nolabels",
                'layers': [
                    {
                        'source': crop_extent.to_geo_dict(),
                        'type': 'fill', 
                        'below': 'traces', 
                        # 'fill': {'outlinecolor': 'black'},
                        'color': 'black', 
                        'opacity': 0.4,
                    },
                    {
                        'source': crop_extent.to_geo_dict(),
                        'type': 'line', 
                        'below': 'traces', 
                        'color': 'black', 
                        'line': {'width': 1.5},
                    },
                ]
            },
        )

        # https://github.com/plotly/plotly.py/issues/1074#issuecomment-1471486307
        figurewidget = go.FigureWidget(fig)
        figurewidget._config = config

        # fig.write_image('figure.png', engine='kaleido')
        # figurewidget.write_image('widget.png')

        return figurewidget


    # @reactive.effect
    # def update_crop_map():
    #     """
    #     """

    #     crop = crop_name()
    #     if(crop == ''):
    #         return

    #     print(crop_map.widget.center)

    #     fig = crop_figure()
    #     print(type(fig))
    #     print(fig)
    #     print(fig.layout)
    #     print()

    #     if(crop == 'none'):
    #         fig.update_layout(map = {'layers': []})
    #         return

    #     match crop:
    #         case 'barley':
    #             crop_layer = barley.to_geo_dict()
    #         case 'cocoa':
    #             crop_layer = cocoa.to_geo_dict()
    #         case 'coffee':
    #             crop_layer = coffee.to_geo_dict()
    #         case 'cotton':
    #             crop_layer = cotton.to_geo_dict()
    #         case 'maize':
    #             crop_layer = maize.to_geo_dict()
    #         case 'rice':
    #             crop_layer = rice.to_geo_dict()
    #         case 'soy':
    #             crop_layer = soy.to_geo_dict()
    #         case 'sugar':
    #             crop_layer = sugar.to_geo_dict()
    #         case 'wheat':
    #             crop_layer = wheat.to_geo_dict()
    #         case _:
    #             return

    #     fig.update_layout(
    #         map = {
    #             'style': "carto-positron-nolabels",
    #             'layers': [
    #                 {
    #                     'source': crop_layer,
    #                     'type': 'fill', 
    #                     'below': 'traces', 
    #                     'fill': {'outlinecolor': 'black'},
    #                     'color': 'black', 
    #                     'opacity': 0.7,
    #                 },
    #                 # {
    #                 #     'source': crop_layer,
    #                 #     'type': 'line', 
    #                 #     # 'below': 'traces', 
    #                 #     'color': 'black', 
    #                 #     'line': {'width': 1.5},
    #                 # },
    #             ]
    #         },
    #     )

    #     return fig


    # @render_widget
    # def crop_map():
    #     from ipyleaflet import basemaps, LayersControl, TileLayer, Map, GeoData, GeoJSON

    #     # basemap = TileLayer(
    #     #     url='https://{s}.basemaps.cartocdn.com/light_nolabels/{z}/{x}/{y}{r}.png',
    #     #     # attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>',
    #     #     subdomains='abcd',
    #     #     maxZoom=20,
    #     # )

    #     zoom = 2

    #     m = Map(basemap=basemaps.CartoDB.Positron, zoom=zoom, scroll_wheel_zoom=True,  attribution_control=False)

    #     geo_data = GeoData(geo_dataframe=wheat, style={'color': 'black','weight': 1, 'opacity': 1}, name='Wheat')
    #     # geo_data = GeoJSON(
    #     #     data=wheat.to_geo_dict(),
    #     #     style={'color': 'black', 'fillColor': '#3366cc', 'weight': 1, 'opacity': 1},
    #     #     name = 'Wheat'
    #     # )
    #     m.add(geo_data)
    #     m.add(LayersControl())

    #     return m


    # @reactive.effect
    # # @reactive.event(crop_name)
    # def _():
    #     from ipyleaflet import LayersControl, TileLayer, Map, GeoData, GeoJSON

    #     crop = crop_name()
    #     basemap = crop_map.widget.layers[0]
    #     # basemap.redraw()
    #     zoom = crop_map.widget.zoom
    #     center = crop_map.widget.center
    #     print(zoom, center)

    #     # if(len(crop_map.widget.layers) > 1):
    #     #     print(crop_map.widget.layers)
    #     #     print()
    #     #     crop_map.widget.remove(crop_map.widget.layers[1])
        
    #     if(crop == '' or crop == 'none'):
    #         # geo_data = GeoData(geo_dataframe=wheat, style={'color':'black','weight':1},)
    #         # geo_data = GeoJSON(
    #         #     data=wheat.to_geo_dict(),
    #         #     style={'color': 'black','weight':1},
    #         # )

    #         # crop_map.widget.add_layer(geo_data)
    #         # crop_map.widget.add_control(LayersControl())
    #         # crop_map.widget = Map(layers=(basemap,), zoom=zoom, center=center, scroll_wheel_zoom=True,  attribution_control=False)
    #         crop_map.widget.layers = (basemap,)
        
    #     else:
    #         print(crop)
    #         print("TRUE! SHOULD BE UPDATING MAP LAYERS")
    #         match crop:
    #             case 'barley':
    #                 crop_layer = barley
    #                 # m.layers = [GeoData(geo_dataframe=barley, style={'color': 'black','weight':1},)]
    #                 # m.add(GeoData(geo_dataframe=barley, style={'color': 'black','weight':1},))
    #             case 'cocoa':
    #                 crop_layer = cocoa
    #                 # m.add(GeoData(geo_dataframe=cocoa, style={'color': 'black','weight':1},))
    #             case 'coffee':
    #                 crop_layer = coffee
    #                 # m.add(GeoData(geo_dataframe=coffee, style={'color': 'black','weight':1},))
    #             case 'cotton':
    #                 crop_layer = cotton
    #                 # m.add(GeoData(geo_dataframe=cotton, style={'color': 'black','weight':1},))
    #             case 'maize':
    #                 crop_layer = maize
    #                 # m.add(GeoData(geo_dataframe=sugarcane, style={'color': 'black','weight':1},))
    #             case 'rice':
    #                 crop_layer = rice
    #                 # m.add(GeoData(geo_dataframe=rice, style={'color': 'black','weight':1},))
    #             case 'soy':
    #                 crop_layer = soy
    #                 # m.add(GeoData(geo_dataframe=soy, style={'color': 'black','weight':1},))
    #             case 'sugarcane':
    #                 crop_layer = sugarcane
    #                 # m.add(GeoData(geo_dataframe=sugarcane, style={'color': 'black','weight':1},))
    #             case 'wheat':
    #                 crop_layer = wheat
    #                 # m.add(GeoData(geo_dataframe=wheat, style={'color': 'black','weight':1},))
    #                 # m.add(LayersControl())

    #         geo_data = GeoData(geo_dataframe=crop_layer, style={'color': 'black','weight':1},)
    #         crop_map.widget.layers = (basemap, geo_data)
    #         # crop_map.widget
         

    @render.data_frame
    @reactive.event(table_to_save)
    def timeseries_table():
        df = table_to_save()

        return render.DataTable( df.drop(['5%', '20%', '80%', '95%'], axis=1), width='100%', height='375px', editable=False, )
    

    @render.download(filename=lambda: f'drought-table-{country_name().lower()}-{"historical" if input.historical_checkbox() else ""}-{"forecast" if input.forecast_checkbox() else ""}-{"" if crop_name() == "none" else crop_name()}-{str(integration_window())+"month"}-{forecast_date}.csv'.replace(' ', '-').replace('--', '-').replace('--', '-'))
    def download_csv_link():
        df = table_to_save()

        with io.BytesIO() as buffer:
            df.to_csv(buffer)
            yield buffer.getvalue()


app = App(app_ui, server, static_assets=static_dir)