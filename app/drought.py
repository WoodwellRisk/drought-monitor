from datetime import datetime
import io
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

updating = False

# calculate the initial conditions from today's year and month
# in general, the month (and potentially year) roll back one month
# for example: if we are producing the forecast in january, 
# then the initial conditions are from december of the previous year

# this is what we would like to do, 
# except that it would roll over in the new month before we have the new data
# today = datetime.today()
# year = today.year
# month = today.month

# if month == 1:
#     month = 12
#     year = year - 1
# else: 
#     month -= 1

year = 2025
month = 9
month_ic = str(month) if month >= 10 else '0' + str(month) 
year_ic = str(year)

# generate the list of date we expect to find for historical data
historical_dates = [date.strftime('%Y-%m-%d') for date in pd.date_range(start='1991-01-01', end=f'{year_ic}-{month_ic}-01', freq='MS')]
forecast_dates = [date.strftime('%Y-%m-%d') for date in pd.date_range(start=f'{year_ic}-{month_ic}-01', freq='MS', periods=7)][1:]
# print(forecast_dates)

# this is used in the the filename for downloading plots and tables, but is also used in slider values
min_date = None if updating else historical_dates[0]
min_slider_date = min_date
max_slider_date = None if updating else historical_dates[-5]
forecast_date = None if updating else forecast_dates[0]
slider_dates = historical_dates[:-4]

min_index = None if updating else 0
max_year = None if updating else year # we calculated this above
skip_index = None if updating else slider_dates.index(f'{max_year - 4}-01-01')
max_index = None if updating else len(slider_dates) - 1

# open historical and forecast data for both integration windows
h3 = None if updating else xr.open_dataset(Path(__file__).parent / f'mnt/data/zarr/analysis/h3-{year_ic}-{month_ic}-01.zarr', engine='zarr', consolidated=True, decode_coords="all", chunks=None,).compute()
h12 = None if updating else xr.open_dataset(Path(__file__).parent / f'mnt/data/zarr/analysis/h12-{year_ic}-{month_ic}-01.zarr', engine='zarr', consolidated=True, decode_coords="all", chunks=None,).compute()
f3 = None if updating else xr.open_dataset(Path(__file__).parent / f'mnt/data/zarr/analysis/f3-{year_ic}-{month_ic}-01.zarr', engine='zarr', consolidated=True, decode_coords="all", chunks=None,).compute()
f12 = None if updating else xr.open_dataset(Path(__file__).parent / f'mnt/data/zarr/analysis/f12-{year_ic}-{month_ic}-01.zarr', engine='zarr', consolidated=True, decode_coords="all", chunks=None,).compute()

# the data variables can come back in a different order when you read in the Zarr instead of the NetCDF
# f3 = f3[['mean', 'mode', 'agree', '5%', '20%', 'perc', '80%', '95%']]
# f12 = f12[['mean', 'mode', 'agree', '5%', '20%', 'perc', '80%', '95%']]
if not updating:
    f3 = f3[['5%', '20%', 'perc', '80%', '95%']]
    f12 = f12[['5%', '20%', 'perc', '80%', '95%']]

# open country boundary layer
countries = gpd.GeoDataFrame(columns=['name', 'geometry']) if updating else gpd.read_parquet(Path(__file__).parent / 'mnt/data/vector/countries.parquet')
states = gpd.GeoDataFrame(columns=['name', 'country', 'geometry']) if updating else gpd.read_parquet(Path(__file__).parent / 'mnt/data/vector/states.parquet')

# open crop polygon layers
barley = None if updating else gpd.read_parquet(Path(__file__).parent / 'mnt/data/vector/barley.parquet')
cocoa = None if updating else gpd.read_parquet(Path(__file__).parent / 'mnt/data/vector/cocoa.parquet')
coffee = None if updating else gpd.read_parquet(Path(__file__).parent / 'mnt/data/vector/coffee.parquet')
cotton = None if updating else gpd.read_parquet(Path(__file__).parent / 'mnt/data/vector/cotton.parquet')
maize = None if updating else gpd.read_parquet(Path(__file__).parent / 'mnt/data/vector/maize.parquet')
rice = None if updating else gpd.read_parquet(Path(__file__).parent / 'mnt/data/vector/rice.parquet')
soy = None if updating else gpd.read_parquet(Path(__file__).parent / 'mnt/data/vector/soybean.parquet')
sugarcane = None if updating else gpd.read_parquet(Path(__file__).parent / 'mnt/data/vector/sugarcane.parquet')
wheat = None if updating else gpd.read_parquet(Path(__file__).parent / 'mnt/data/vector/wheat.parquet')

# open crop raster layers
barley_production = None if updating else open_production_data(Path(__file__).parent / 'mnt/data/spam/crop_production_era5-grid_barley.tif')
cocoa_production = None if updating else open_production_data(Path(__file__).parent / 'mnt/data/spam/crop_production_era5-grid_cocoa.tif')
coffee_production = None if updating else open_production_data(Path(__file__).parent / 'mnt/data/spam/crop_production_era5-grid_coffee-all.tif')
cotton_production = None if updating else open_production_data(Path(__file__).parent / 'mnt/data/spam/crop_production_era5-grid_cotton.tif')
maize_production = None if updating else open_production_data(Path(__file__).parent / 'mnt/data/spam/crop_production_era5-grid_maize.tif')
rice_production = None if updating else open_production_data(Path(__file__).parent / 'mnt/data/spam/crop_production_era5-grid_rice.tif')
soy_production = None if updating else open_production_data(Path(__file__).parent / 'mnt/data/spam/crop_production_era5-grid_soybean.tif')
sugarcane_production = None if updating else open_production_data(Path(__file__).parent / 'mnt/data/spam/crop_production_era5-grid_sugarcane.tif')
wheat_production = None if updating else open_production_data(Path(__file__).parent / 'mnt/data/spam/crop_production_era5-grid_wheat.tif')

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
        ui.include_js('./scripts/sidebar-visibility.js', method='inline'),
    ),

    ui.div({'id': 'layout'},

        # navbar section
        ui.div({'id': 'navbar'},
            ui.div({'id': 'logo-container'}, 
                ui.div({'id': 'logo-inner-container'},
                    ui.img(src='woodwell-risk.png', width='45px', alt='Woodwell Climate Research Center Risk group logo'),
                    ui.p({'id': 'org-title'}, 'Woodwell Risk'),
                ),
            ),
            ui.div({'id': 'menu-container'},
                ui.div({'id': 'menu-inner-container'},
                ui.input_action_button('about_button', 'About',),
                ui.input_action_button('settings_button', 'Settings', disabled=True), # this could also be called options or controls
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
                            ui.p({'class': 'select-label'}, 'Select a state:')
                        ),
                        ui.input_select('state_select', '', [], size=5),

                        ui.panel_conditional('input.window_select == 3',
                            ui.div({'class': 'select-label-container'},
                                ui.p({'class': 'select-label'}, 'Select a crop:')
                            ),
                            ui.input_select('crop_select', '', [], size=5),
                            {'id': 'crop-select-conditional-panel'},
                        ),

                        ui.div({'id': 'process-data-container'},
                            ui.input_task_button("process_data_button", label="Run"),
                        ),
                    )
                ),
            ),

            # figures and tables
            ui.div({"id": "main-container"},
                ui.div({'id': 'main'},
                    ui.navset_tab(
                        # historical data tab
                        ui.nav_panel('Historical data', 
                            ui.div({'id': 'iframe-container'},
                                ui.tags.iframe(src='https://woodwellrisk.github.io/drought-monitor', height='100%', width='100%')
                            ),
                        ),

                        # timeseries and table tab
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

                            ui.output_ui('show_time_slider'),
                            
                            ui.div({'id': 'download-csv-container', 'class': 'download-container'},
                                ui.download_link("download_csv_link", 'Download CSV')
                            ),
                            ui.div({'id': 'timeseries-table-container'},
                                ui.output_data_frame("timeseries_table"),
                            ),

                            ui.busy_indicators.options(),
                        ),

                        # forecast map tab
                        ui.nav_panel('Forecast map', 
                            ui.div({'id': 'forecast-map-container'},
                                ui.output_ui('forecast_map'),
                            ),
                        ),
                        id='tab_menu'
                    ),
                ),
            ),

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
                            In order to examine the relationship between water balance anomalies and agriculture, we have provided the spatial extents of several crops.
                            These can be used to get water balance data within a given country where a specific crop is currently grown (as of 2020).
                            
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
            
            ui.output_ui('show_update_message'),
        ),
    ),
)

def server(input: Inputs, output: Outputs, session: Session):
    
    countries_list = sorted(countries.name.values)
    country_options = reactive.value(countries_list)
    state_options = reactive.value([])

    crop_list = [
        'None', 'Barley', 'Cocoa', 'Coffee', 'Cotton',
        'Maize', 'Rice', 'Soy', 'Sugarcane', 'Wheat',
    ]
    crop_options = reactive.value(crop_list)
    crop_layer = reactive.value(None)
    crop_production = reactive.value(None)

    country_name = reactive.value('')
    state_name = reactive.value('')
    crop_name = reactive.value('')
    filter_text = reactive.value('')
    bounds = reactive.value([])
    bbox = reactive.value([])
    
    slider_date = reactive.value(min_slider_date)

    # these values change the data between the 3-month and 12-month integration windows
    integration_window = reactive.value(None)

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


    @render.ui
    def show_update_message():
        if updating:
            return ui.TagList(
                ui.div({'id': 'update-message-container'},
                    ui.div({'id': 'update-message'}, 
                        'The website is currently being updated. Please check back later.'
                    ),
                ),
            )


    @reactive.effect
    @reactive.event(input.window_select)
    def update_integration_window():
        window_size = input.window_select()
        integration_window.set(window_size)
        
        if(window_size == '12'):
            # if the integration window is not set to 3 months, then we don't want to look at agriculture applications
            # setting the name to 'none' takes care of the rest of the logic around 
            # not weighting the forecast by crop production, which is handled in another method
            crop_name.set('none')
            new_options = crop_options()
            ui.update_select('crop_select', label=None, choices=new_options, selected='None')


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
        state_name.set('')


    @render.text
    def country_name_text():
        return country_name()


    @reactive.effect
    @reactive.event(country_name)
    def update_state_list():
        cname = country_name()
        sname = state_name()

        if(cname == ''): return

        df = states.query(" country == @cname ")
        states_list = sorted(df.name.values.tolist())
        # some countries have no administrative states / regions
        if(len(states_list) == 0 ):
            new_options = ['All']
        else: 
            if(cname == 'USA'):
                states_list = [state for state in states_list if state != 'CONUS']
                new_options = ['All', 'CONUS'] + states_list
            else:
                new_options = ['All'] + states_list
        
        state_options.set(new_options)


    @reactive.effect
    @reactive.event(state_options)
    def update_state_select():
        new_options = state_options()
        ui.update_select('state_select', label=None, choices=new_options, selected=None)


    @reactive.effect
    @reactive.event(input.state_select)
    def update_state_name():
        new_state = input.state_select()
        state_name.set(new_state)
    

    @reactive.effect
    @reactive.event(country_name, state_name)
    def update_bounds():
        cname = country_name()
        sname = state_name()

        # on app start or page reload, these variables will be empty
        if(cname == '' or sname == ''):
            return

        # https://stackoverflow.com/questions/1894269/how-to-convert-string-representation-of-list-to-a-list#1894296
        if(sname == 'All'):
            new_bounds = json.loads(countries.query(" name == @cname ").bbox.values[0])
        else:
            new_bounds = json.loads(states.query(" name == @sname and country == @cname ").bbox.values[0])
        bounds.set(new_bounds)

        xmin, ymin, xmax, ymax = new_bounds
        new_bbox = create_bbox_from_coords(xmin, xmax, ymin, ymax)
        bbox.set(new_bbox)


    @reactive.effect
    @reactive.event(crop_options)
    def update_crop_select():
        new_options = crop_options()
        ui.update_select('crop_select', label=None, choices=new_options, selected='None')


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


    @render.ui
    def show_time_slider():
        if not updating:
            return ui.TagList(
            ui.panel_conditional('input.historical_checkbox == true',
                ui.div({'id': 'time-slider-container'}, 
                    ui.input_action_link('skip_months_button', 'Last 5 months', class_='skip-button'),
                    ui.input_action_link('skip_years_button', 'Last 5 years', class_='skip-button'),
                    ui.input_action_link('reset_skip_button', 'All data', class_='skip-button'),

                    ui.div({'id': 'time-slider-labels-container'},
                        ui.div({'class': 'time-slider-label'}, min_slider_date),
                        ui.output_text('time_slider_output'),
                        ui.div({'class': 'time-slider-label'}, max_slider_date),
                    ),
                    ui.input_slider('time_slider', '',
                        min=0,
                        max=len(slider_dates) - 1,
                        value=skip_index,
                    ),
                ),
            {'id': 'show-slider-container'},
            ),
        )

    
    @reactive.effect
    @reactive.event(input.reset_skip_button)
    def reset_skip_button():
        ui.update_slider('time_slider', value=min_index)

    
    @reactive.effect
    @reactive.event(input.skip_years_button)
    def update_skip_years_button():
        ui.update_slider('time_slider', value=skip_index)

    
    @reactive.effect
    @reactive.event(input.skip_months_button)
    def update_skip_years_button():
        ui.update_slider('time_slider', value=max_index)


    @reactive.effect
    @reactive.event(input.time_slider)
    def update_slider_date():
        if slider_dates is None:
            return
        else:
            slider_date.set(slider_dates[input.time_slider()])


    @render.text
    def time_slider_output():
        return slider_date()


    @reactive.effect
    @reactive.event(input.process_data_button)
    def update_wb_data():
        crop = crop_name()
        crop_extent = crop_layer()

        cname = country_name()
        sname = state_name()

        window_size = integration_window()

        if(window_size == '3'):
            historical = h3
            forecast = f3
        elif(window_size == '12'):
            historical = h12
            forecast = f12
        else:
            raise ValueError("The integration window should be either 3 or 12 months.")

        # on app start or page reload, these variables will be empty
        if(cname == '' or sname == '' or crop == '' or historical is None or forecast is None):
            return

        xmin, ymin, xmax, ymax = bounds.get()
        bounding_box = bbox()
        country = countries.query(" name == @cname ")
        state = states.query(" name == @sname and country == @cname ")

        # we have already filtered countries where we don't have data, so clipping by country extent 
        # should never produce a rioxarray.exceptions.NoDataInBounds error at this step
        if(sname == 'All'):
            historical = historical.rio.clip(country.geometry, all_touched=True, drop=True)
            forecast = forecast.rio.clip(country.geometry, all_touched=True, drop=True)
        else:
            historical = historical.rio.clip(state.geometry, all_touched=True, drop=True)
            forecast = forecast.rio.clip(state.geometry, all_touched=True, drop=True)

        historical = historical.assign_attrs({'crop': crop})
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
                if(sname == 'All'):
                    clipped_production = production.rio.clip(country.geometry, all_touched=True, drop=True)
                else:
                    clipped_production = production.rio.clip(state.geometry, all_touched=True, drop=True)
                standardized_production = clipped_production / clipped_production.sum(skipna=True)
                standardized_production = standardized_production[['x', 'y', 'production']]

                # multiply water balance data by standardized production values
                historical = xr.merge([historical, standardized_production])
                historical = historical * historical.production

                forecast = xr.merge([forecast, standardized_production])
                forecast['5%'] = forecast['5%'] * forecast.production
                forecast['20%'] = forecast['20%'] * forecast.production
                forecast['perc'] = forecast['perc'] * forecast.production
                forecast['80%'] = forecast['80%'] * forecast.production
                forecast['95%'] = forecast['95%'] * forecast.production

                # next, multiply the water balance data by the number of rows in the dataset
                # in this case, it is the number of rows in the first (and every individual) month
                nrows_historical = historical.drop_vars('spatial_ref').sel(time=min_date).to_dataframe().dropna().shape[0]
                nrows_forecast = forecast.drop_vars('spatial_ref').sel(time=forecast_date).to_dataframe().dropna().shape[0]
                
                historical *= nrows_historical
                
                forecast['5%'] = forecast['5%'] * nrows_forecast
                forecast['20%'] = forecast['20%'] * nrows_forecast
                forecast['perc'] = forecast['perc'] * nrows_forecast
                forecast['80%'] = forecast['80%'] * nrows_forecast
                forecast['95%'] = forecast['95%'] * nrows_forecast
                
                # lastly, drop the production row from the dataframes
                historical = historical[['time', 'x', 'y', 'perc']]

                # forecast = forecast[['time', 'x', 'y', 'agree', '5%', '20%', 'perc', '80%', '95%']]
                forecast = forecast[['time', 'x', 'y', '5%', '20%', 'perc', '80%', '95%']]


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
        cname = country_name()
        
        if(crop == '' or cname == ''):
            return

        show_error = display_bounds_error()
        
        if(show_error):
            ui.insert_ui(
                ui.div({'class': 'bounds-error-container'},
                    ui.div({'class': 'bounds-error'},
                        # f'No water balance data to show. This is likely because {crop} is not grown in {name} or the data resoultion is too low.'
                        'No water balance data to show. This is likely because the crop you chose is not grown in the country / state in question or the data resoultion is too low.'

                    ),
                ),
                selector='#forecast-map-container',
                where='beforeEnd',
            )

            ui.insert_ui(
                ui.div({'class': 'bounds-error-container'},
                    ui.div({'class': 'bounds-error'},
                        # f'No water balance data to show. This is likely because {crop} is not grown in {name} or the data resoultion is too low.'
                        'No water balance data to show. This is likely because the crop you chose is not grown in the country / state in question or the data resoultion is too low.'

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
        cname = country_name()
        sname = state_name()
        window_size = integration_window()

        show_historical = input.historical_checkbox()
        show_forecast = input.forecast_checkbox()

        historical = historical_wb()
        forecast = forecast_wb()

        # if the xarray data is empty (on initial load) or if the toggles controlling which datasets to show are both false, then return empty dataframe
        if((forecast is None and historical is None) or (show_forecast == False and show_historical == False)):
            # df = pd.DataFrame({
            #     'country': [], 'state': [], 'type': [], 'crop': [], 'time': [], 'percentile': [], 'agreement': [],
            #     '5%': [], '20%': [], '80%': [], '95%': [],
            # })
            df = pd.DataFrame({
                'country': [], 'state': [], 'type': [], 'crop': [], 'window': [], 'time': [], 
                'percentile': [], '5%': [], '20%': [], '80%': [], '95%': [],
            })
        else:
            # include just historical
            if(show_historical == True and show_forecast == False):
                df = historical.mean(dim=['x', 'y']).drop_vars('spatial_ref').to_pandas().reset_index()
                df['perc'] = df['perc'].astype(float).round(4)
                # df['agree'] = np.nan
                df['time'] = df['time'].dt.date
                # df.columns = ['time', 'percentile', 'agreement']
                df.columns = ['time', 'percentile']
                df['country'] = cname
                df['state'] = sname
                df['crop'] = crop
                df['type'] = 'historical'
                df['window'] = int(window_size)
                df['5%'] = np.nan
                df['20%'] = np.nan
                df['80%'] = np.nan
                df['95%'] = np.nan
                
                # df = df[['country', 'state', 'crop', 'type', 'window', 'time', 'percentile', 'agreement', '5%', '20%', '80%', '95%']].sort_values('time', ascending=False).reset_index(drop=True)
                df = df[['country', 'state', 'crop', 'type', 'window', 'time', 'percentile', '5%', '20%', '80%', '95%']].sort_values('time', ascending=False).reset_index(drop=True)

            
            # include just forecast
            elif(show_historical == False and show_forecast == True):
                df = forecast.mean(dim=['x', 'y']).drop_vars('spatial_ref').to_pandas().reset_index()
                # this is the 50% line in the forecast data
                df['perc'] = df['perc'].astype(float).round(4)
                # df['agree'] = df['agree'].astype(float).round(4)
                df['5%'] = df['5%'].astype(float).round(4)
                df['20%'] = df['20%'].astype(float).round(4)
                df['80%'] = df['80%'].astype(float).round(4)
                df['95%'] = df['95%'].astype(float).round(4)
                df['time'] = df['time'].dt.date
                # df.columns = ['time', 'agreement', '5%', '20%', 'percentile', '80%', '95%']
                df.columns = ['time', '5%', '20%', 'percentile', '80%', '95%']
                df['country'] = cname
                df['state'] = sname
                df['crop'] = crop
                df['type'] = 'forecast'
                df['window'] = int(window_size)
                
                # df = df[['country', 'state', 'crop', 'type', 'window', 'time', 'percentile', 'agreement', '5%', '20%', '80%', '95%']].sort_values('time', ascending=False).reset_index(drop=True)
                df = df[['country', 'state', 'crop', 'type', 'window', 'time', 'percentile', '5%', '20%', '80%', '95%']].sort_values('time', ascending=False).reset_index(drop=True)


            # else both are active, include both
            else:
                df_historical = historical.mean(dim=['x', 'y']).drop_vars('spatial_ref').to_pandas().reset_index()
                df_historical['perc'] = df_historical['perc'].astype(float).round(4)
                # df_historical['agree'] = np.nan
                df_historical['time'] = df_historical['time'].dt.date
                # df_historical.columns = ['time', 'percentile', 'agreement']
                df_historical.columns = ['time', 'percentile']
                df_historical['country'] = cname
                df_historical['state'] = sname
                df_historical['crop'] = crop
                df_historical['type'] = 'historical'
                df_historical['window'] = int(window_size)
                df_historical['5%'] = np.nan
                df_historical['20%'] = np.nan
                df_historical['80%'] = np.nan
                df_historical['95%'] = np.nan
                # df_historical = df_historical[['country', 'state', 'crop', 'type', 'window', 'time', 'percentile', 'agreement', '5%', '20%', '80%', '95%']]
                df_historical = df_historical[['country', 'state', 'crop', 'type', 'window', 'time', 'percentile', '5%', '20%', '80%', '95%']]

                df_forecast = forecast.mean(dim=['x', 'y']).drop_vars('spatial_ref').to_pandas().reset_index()
                df_forecast['perc'] = df_forecast['perc'].astype(float).round(4)
                # df_forecast['agree'] = df_forecast['agree'].astype(float).round(4)
                df_forecast['5%'] = df_forecast['5%'].astype(float).round(4)
                df_forecast['20%'] = df_forecast['20%'].astype(float).round(4)
                df_forecast['80%'] = df_forecast['80%'].astype(float).round(4)
                df_forecast['95%'] = df_forecast['95%'].astype(float).round(4)
                df_forecast['time'] = df_forecast['time'].dt.date
                # df_forecast.columns = ['time', 'agreement', '5%', '20%', 'percentile', '80%', '95%']
                df_forecast.columns = ['time', '5%', '20%', 'percentile', '80%', '95%']
                df_forecast['country'] = cname
                df_forecast['state'] = sname
                df_forecast['crop'] = crop
                df_forecast['type'] = 'forecast'
                df_forecast['window'] = int(window_size)
                # df_forecast = df_forecast[['country', 'state', 'crop', 'type', 'window', 'time', 'percentile', 'agreement', '5%', '20%', '80%', '95%']]
                df_forecast = df_forecast[['country', 'state', 'crop', 'type', 'window', 'time', 'percentile', '5%', '20%', '80%', '95%']]

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
    @reactive.event(table_to_save, slider_date)
    def timeseries(alt="A graph showing a timeseries of historical and forecasted water balance"):
        # later if we want to make it so that we can dynamically change the timeframe:
        # https://plotly.com/python/range-slider/
        historical = historical_wb()
        forecast = forecast_wb()

        if(historical is None or forecast is None):
            return

        show_historical = input.historical_checkbox()
        show_forecast = input.forecast_checkbox()
        filter_date = slider_date()

        df = table_to_save()
        df = df.query(" @pd.to_datetime(@df['time'], format='%Y-%m-%d') >= @pd.Timestamp(@filter_date) ")
        # print(df.head(20)[['country', 'state', 'crop', 'time', 'window', 'percentile']])
        # print()


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
            df_historical = df.iloc[6:, :]
            # print(df_historical[['country', 'state', 'crop', 'time', 'window', 'percentile']])
            # print()

            # this is the 6-month forecast plus the last data entry for historical data
            df_forecast = df.iloc[0:7, :]
            # print(df_forecast[['country', 'state', 'crop', 'time', 'window', 'percentile']])
            # print()
            
            # forecast data needs to be plotted first because of the uncertainty bounds
            ax.fill_between(df_forecast['time'], df_forecast['5%'], df_forecast['95%'], color=high_certainty_color)
            ax.fill_between(df_forecast['time'], df_forecast['20%'], df_forecast['80%'], color=medium_certainty_color)
            ax.plot(df_forecast['time'], df_forecast['percentile'], color=timeseries_color, linestyle='--')
            ax.plot(df_historical['time'], df_historical['percentile'], color=timeseries_color)
            
            legend_elements = [historical_label, forecast_label, medium_certainty_label, high_certainty_label]

        if(show_historical == True and show_forecast == False):
            ax.plot(df['time'], df['percentile'], color=timeseries_color)

            if(len(df) == 5):
                ax.set_xticks([date for date in df.time.values])
            
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

        # when there are 60 or more entries in the dataframe, 
        # the date labels along the x-axis get crowded and difficult to read
        if(len(df) <= 60):
            date_format = mdates.DateFormatter('%m-%y')
            ax.xaxis.set_major_formatter(date_format)

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


    @render.download(filename=lambda: f'drought-timeseries-{country_name().lower()}-{"" if state_name() == "" else state_name().lower()}-{"historical" if input.historical_checkbox() else ""}-{"forecast" if input.forecast_checkbox() else ""}-{"" if crop_name() == "none" else crop_name()}-{str(integration_window())+"month"}-{forecast_date}.png'.replace(' ', '-').replace('--', '-').replace('--', '-'))
    def download_timeseries_link():

        cname = country_name()
        sname = state_name()

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

        title = f"{historical_and_forecast_label} water balance for {sname + ', ' if sname != '' and sname != 'All' else ''}{cname}"
        ax.set_title(title, fontproperties=ginto_medium)

        fig.subplots_adjust(top=0.9)

        with io.BytesIO() as buffer:
            plt.savefig(buffer, format="png", dpi=300)
            yield buffer.getvalue()
    

    @render.ui
    @reactive.event(unweighted_forecast_wb)
    def forecast_map(alt="a map showing the borders of a country of interest"):

        cname = country_name()
        sname = state_name()
        country = countries.query(" name == @cname ")
        state = states.query(" name == @sname and country == @cname ")
        forecast = unweighted_forecast_wb()

        if(cname == '' or sname == '' or forecast is None):
            return

        config = {
            # 'staticPlot': False, 
            'displaylogo': False, 
            # 'displayModeBar': False, 
            'scrollZoom': True,
            # 'modeBarButtonsToRemove': ['zoom', 'pan', 'select', 'lasso2d', 'toImage']
            'modeBarButtonsToRemove': ['pan', 'select', 'lasso2d', 'toImage']

        }

        centroid = country.centroid.values[0]
        bbox = json.loads(country.bbox.values[0])
        bounding_box = create_bbox_from_coords(*bbox).to_geo_dict()

        max_bounds = max(abs(bbox[0] - bbox[2]), abs(bbox[1] - bbox[3])) * 111
        zoom = 11 - np.log(max_bounds)

        country_forecast = forecast.rio.clip(country.geometry, all_touched=True, drop=True)
        df = country_forecast['perc'].drop_vars('spatial_ref').to_dataframe().dropna().reset_index()
        df.columns = ['time', 'y', 'x', 'Percentile']

        formatted_dates = [pd.to_datetime(date).strftime("%b-%Y") for date in forecast_dates]

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
            # map_style = 'carto-darkmatter-nolabels',
            zoom = zoom,
            height = 445,
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
                'font': {'color': '#1b1e23', 'family': 'Ginto normal'},
            }],
            margin=dict(l=0, r=0, t=0, b=0),
            paper_bgcolor='#f7f7f7',
        )

        fig.update_coloraxes(
            colorbar_title_side='right',
            colorbar_title_font=dict(color='#1b1e23', family='Ginto normal'),
            # colorbar_title_font=dict(color='#f7f7f7', family='Ginto normal'),
            colorbar_len=0.8,
            colorbar_thickness=20,
            colorbar_tickfont=dict(color='#1b1e23', family='Ginto normal'),
            # colorbar_tickfont=dict(color='#f7f7f7', family='Ginto normal'),
        )

        fig.update_layout(
            coloraxis_colorbar_x=0.01,
            hoverlabel=dict(font_family='Ginto normal')
        )

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
         

    @render.data_frame
    @reactive.event(table_to_save)
    def timeseries_table():
        df = table_to_save()

        return render.DataTable( df.drop(['5%', '20%', '80%', '95%'], axis=1), width='100%', height='375px', editable=False, )
    

    @render.download(filename=lambda: f'drought-table-{country_name().lower()}-{"" if state_name() == "" else state_name().lower()}-{"historical" if input.historical_checkbox() else ""}-{"forecast" if input.forecast_checkbox() else ""}-{"" if crop_name() == "none" else crop_name()}-{str(integration_window())+"month"}-{forecast_date}.csv'.replace(' ', '-').replace('--', '-').replace('--', '-'))
    def download_csv_link():
        df = table_to_save()

        with io.BytesIO() as buffer:
            df.to_csv(buffer)
            yield buffer.getvalue()


app = App(app_ui, server, static_assets=static_dir)