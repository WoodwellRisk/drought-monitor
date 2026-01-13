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
from dash import Dash, html, dcc, dash_table, callback, Output, Input
import dash_ag_grid as dag

from pathlib import Path

from utils.helpers import *

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
month = 12
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

window_list = [3, 12]
window_options = [{'label': f'{window} month', 'value': window} for window in window_list]


country_list = sorted(countries.name.unique())
country_options = [{'label': country.title(), 'value': country} for country in country_list]

crop_list = ['none', 'barley', 'cocoa', 'coffee', 'cotton', 'maize', 'rice', 'soy', 'sugar', 'wheat']
crop_options = [{'label': crop.title(), 'value': crop} for crop in crop_list]

##################
# DUMMY DATA
##################
df = pd.read_csv('https://raw.githubusercontent.com/plotly/datasets/master/gapminder2007.csv')

# initialize the app and incorporate css
external_stylesheets = ['./assets/css/stylesheet.css']
app = Dash(__name__, external_stylesheets=external_stylesheets)

def serve_layout():
    
    return html.Div(id='layout-container', children=[

        # header section
        html.Div(id='header', children=[
            html.Div(id='logo-container', children=[
                html.Div(id='logo-inner-container', children=[
                    html.Img(id='logo-image', src=app.get_asset_url('woodwell-risk.png'), alt='Woodwell Climate Research Center Risk group logo'),
                    html.Div(id='org-title-container', children=[
                        html.P('Woodwell Risk', id='org-title')
                    ])
                ]),
            ]),
            html.Div(id='menu-container', children=[
                html.Div(id='menu-inner-container', children=[
                    html.Button('About', id='about-button'),
                    html.Button('Settings', id='settings-button', disabled=True), # this could also be called options or controls
                ]),
            ]),
        ]),

        # wrapper container for sidebar and main panel
        html.Div(id='container', children=[

            html.Div(id='sidebar-container', children=[
                html.Div(id='sidebar-inner-container', children=[
                    html.Div(className='select-label-container', children=[
                        html.P('Select an integration window:', className='select-label'),
                        dcc.Dropdown(id='window-select', options=window_options, searchable=False),
                    ]),

                    html.Div(className='select-label-container', children=[
                            html.Div('Select a country:', className='select-label')
                        ]),
                        dcc.Dropdown(id='country-select', options=country_list),

                    html.Div(className='select-label-container', children=[
                        html.P('Select a state:', className='select-label')
                    ]),
                    dcc.Dropdown(id='state-select', options=[]),

                    html.Div(id='conditional-div-crop-select', children=[
                        html.Div(className='select-label-container', children=[
                            html.P('Select a crop', className='select-label')
                        ]),
                        dcc.Dropdown(id='crop-select', options=crop_options),
                    ]),

                    html.Div(id='process-data-container', children=[
                        html.Button('Run', id='process-data-button'),
                    ]),
                ])

                ]),

            # figures and tables
            html.Div(id='main-container', children=[
                html.Div(id='main-inner-container', children=[

                    # html.Div(className='box'),
                    # html.Div(className='box'),
                    # html.Div(className='box'),
                    # html.Div(className='box'),
                    # html.Div(className='box'),

                    dcc.Tabs(id='tabs-container', children=[
                        dcc.Tab(label='Historical data', value='historical', children=[
                            html.Div(id='iframe-container', children=[
                                html.Iframe(src='https://woodwellrisk.github.io/drought-monitor', height='100%', width='100%')
                            ])
                        ]),

                        dcc.Tab(label='Timeseries', value='timeseries', children=[
                            html.Div(id='download-timeseries-container', className='download-container', children=[
                                html.Button('Download timeseries', className='download-link'),
                                dcc.Download('download-timeseries-link', )
                            ]),
                            html.Div(id='timeseries-container', children=[
                                html.Div(id='timeseries-toggle-container', children=[
                                    dcc.Checklist(id='historical-checkbox', options=['Historical'], value=['Historical']),
                                    dcc.Checklist(id='forecast-checkbox', options=['Forecast'], value=['Forecast']),
                                ]),
                                html.Div(id='timeseries-inner-container', children=[
                                    dcc.Graph(id='timeseries'),
                                ]),
                            ]),

                            html.Div(id='conditional-div-time-slider', children=[]),
                            
                            html.Div(id='download-csv-container', className='download-container', children=[
                                html.Button('Download CSV', className='download-link'),
                                dcc.Download("download-csv-link")
                            ]),
                            html.Div(id='timeseries-table-container', children=[
                                dash_table.DataTable(
                                    id='timeseries-table',
                                    columns=[{'name': col, 'id': col} for col in df.columns],
                                    data=[],
                                    style_table={'overflowX': 'scroll'},
                                    style_header={'backgroundColor': '#f8f9fa', 'fontWeight': 'bold'},
                                    style_cell={'textAlign': 'left', 'padding': '5px'},
                                )
                            ]),
                        ]),
                        
                        dcc.Tab(label='Forecast map', value='forecast', children=[
                            html.Div(id='forecast-map-container', children=[
                                dcc.Graph('forecast-map'),
                            ]),
                        ]),
                    ])
                ]),
            ]),
        ])
    ])


app.layout = serve_layout


# callbacks
@app.callback(
    Output('sidebar-container', 'style'),
    Input('tabs-container', 'value')
)
def show_sidebar(selected_tab):
    return {'display': 'none'} if selected_tab == 'historical' else {'display': 'initial'}


@app.callback(
    Output('main-container', 'className'),
    Input('tabs-container', 'value')
)
def show_sidebar(selected_tab):
    if(selected_tab == 'timeseries'):
        return 'overflow'
    else:
        return ''


@app.callback(
    Output('conditional-div-crop-select', 'style'),
    Input('window-select', 'value')
)
def show_crop_select(window):
    return {'display': 'block'} if window == 3 else {'display': 'none'}


@app.callback(
    Output('state-select', 'options'),
    Output('state-select', 'value'),
    Input('country-select', 'value')
)
def show_state_options(country):
    if(country is None):
        return [], None
    else:
        df = states.query(" country == @country ")
        state_list = ['None'] + sorted(df.name.values.tolist())
        state_options = [{'label': state, 'value': state} for state in state_list] 

        return state_options, None


@app.callback(
    Output('conditional-div-time-slider', 'children'),
    Input('historical-checkbox', 'value')
)
def show_time_slider(value):
    if value:
        return html.Div(id='time-slider-container', children=[
            html.Button('Last 5 months', id='skip-months-button', className='skip-button'),
            html.Button('Last 5 years', id='skip-years-button', className='skip-button'),
            html.Button('All data', id='reset-skip-button', className='skip-button'),

            html.Div(id='time-slider-labels-container', children=[
                html.Div(min_slider_date, className='time-slider-label'),
                html.Div(id='time-slider-output'),
                html.Div(max_slider_date, className='time-slider-label'),
            ]),
            dcc.Slider(
                id='time-slider',
                min=0,
                max=len(slider_dates) - 1,
                value=skip_index,
            ),
        ])
    else:
        return None


# run the app
if __name__ == '__main__':
    app.run(debug=True)