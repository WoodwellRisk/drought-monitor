
# ----------------------------------------------------------------------
# 1️⃣ Imports & global data loading
# ----------------------------------------------------------------------
import io
import json
import base64
from pathlib import Path

import pandas as pd
import numpy as np
import geopandas as gpd
import xarray as xr
import rioxarray

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.lines import Line2D

import plotly.express as px
import plotly.graph_objects as go

import dash
from dash import dcc, html, dash_table, Input, Output, State, ctx
from dash.exceptions import PreventUpdate

# Local helper – must exist in the repository
from utils.helpers import open_production_data   # adjust import if needed

# ----------------------------------------------------------------------
# 2️⃣ Global constants (same as Shiny file)
# ----------------------------------------------------------------------
updating = False                     # keep the flag from the original script

# ---- Date handling ----------------------------------------------------
year = 2025
month = 12
month_ic = f"{month:02d}"
year_ic  = str(year)

historical_dates = [
    d.strftime("%Y-%m-%d")
    for d in pd.date_range(start="1991-01-01",
                           end=f"{year_ic}-{month_ic}-01",
                           freq="MS")
]
forecast_dates = [
    d.strftime("%Y-%m-%d")
    for d in pd.date_range(start=f"{year_ic}-{month_ic}-01",
                           freq="MS",
                           periods=7)
][1:]

min_date          = None if updating else historical_dates[0]
min_slider_date   = min_date
max_slider_date   = None if updating else historical_dates[-5]
forecast_date     = None if updating else forecast_dates[0]
slider_dates      = historical_dates[:-4]

min_index   = None if updating else 0
max_year    = None if updating else year
skip_index  = None if updating else slider_dates.index(f"{max_year - 4}-01-01")
max_index   = None if updating else len(slider_dates) - 1

# ---- Load heavy datasets (once, at import time) -----------------------
# NOTE: paths are relative to this file, exactly as in the Shiny version
h3 = None if updating else xr.open_dataset(
    Path(__file__).parent /
    f"mnt/data/zarr/analysis/h3-{year_ic}-{month_ic}-01.zarr",
    engine="zarr",
    consolidated=True,
    decode_coords="all",
    chunks=None,
).compute()

h12 = None if updating else xr.open_dataset(
    Path(__file__).parent /
    f"mnt/data/zarr/analysis/h12-{year_ic}-{month_ic}-01.zarr",
    engine="zarr",
    consolidated=True,
    decode_coords="all",
    chunks=None,
).compute()

f3 = None if updating else xr.open_dataset(
    Path(__file__).parent /
    f"mnt/data/zarr/analysis/f3-{year_ic}-{month_ic}-01.zarr",
    engine="zarr",
    consolidated=True,
    decode_coords="all",
    chunks=None,
).compute()

f12 = None if updating else xr.open_dataset(
    Path(__file__).parent /
    f"mnt/data/zarr/analysis/f12-{year_ic}-{month_ic}-01.zarr",
    engine="zarr",
    consolidated=True,
    decode_coords="all",
    chunks=None,
).compute()

# ---- Vector layers -----------------------------------------------------
countries = (gpd.GeoDataFrame(columns=["name", "geometry"])
            if updating else
            gpd.read_parquet(
                Path(__file__).parent / "mnt/data/vector/countries.parquet"))

states = (gpd.GeoDataFrame(columns=["name", "country", "geometry"])
          if updating else
          gpd.read_parquet(
                Path(__file__).parent / "mnt/data/vector/states.parquet"))

# ---- Crop polygons ------------------------------------------------------
barley   = None if updating else gpd.read_parquet(
    Path(__file__).parent / "mnt/data/vector/barley.parquet")
cocoa    = None if updating else gpd.read_parquet(
    Path(__file__).parent / "mnt/data/vector/cocoa.parquet")
coffee   = None if updating else gpd.read_parquet(
    Path(__file__).parent / "mnt/data/vector/coffee.parquet")
cotton   = None if updating else gpd.read_parquet(
    Path(__file__).parent / "mnt/data/vector/cotton.parquet")
maize    = None if updating else gpd.read_parquet(
    Path(__file__).parent / "mnt/data/vector/maize.parquet")
rice     = None if updating else gpd.read_parquet(
    Path(__file__).parent / "mnt/data/vector/rice.parquet")
soy      = None if updating else gpd.read_parquet(
    Path(__file__).parent / "mnt/data/vector/soybean.parquet")
sugarcane= None if updating else gpd.read_parquet(
    Path(__file__).parent / "mnt/data/vector/sugarcane.parquet")
wheat    = None if updating else gpd.read_parquet(
    Path(__file__).parent / "mnt/data/vector/wheat.parquet")

# ---- Crop raster production maps ----------------------------------------
barley_production   = None if updating else open_production_data(
    Path(__file__).parent / "mnt/data/spam/crop_production_era5-grid_barley.tif")
cocoa_production    = None if updating else open_production_data(
    Path(__file__).parent / "mnt/data/spam/crop_production_era5-grid_cocoa.tif")
coffee_production   = None if updating else open_production_data(
    Path(__file__).parent / "mnt/data/spam/crop_production_era5-grid_coffee-all.tif")
cotton_production   = None if updating else open_production_data(
    Path(__file__).parent / "mnt/data/spam/crop_production_era5-grid_cotton.tif")
maize_production    = None if updating else open_production_data(
    Path(__file__).parent / "mnt/data/spam/crop_production_era5-grid_maize.tif")
rice_production     = None if updating else open_production_data(
    Path(__file__).parent / "mnt/data/spam/crop_production_era5-grid_rice.tif")
soy_production      = None if updating else open_production_data(
    Path(__file__).parent / "mnt/data/spam/crop_production_era5-grid_soybean.tif")
sugarcane_production= None if updating else open_production_data(
    Path(__file__).parent / "mnt/data/spam/crop_production_era5-grid_sugarcane.tif")
wheat_production    = None if updating else open_production_data(
    Path(__file__).parent / "mnt/data/spam/crop_production_era5-grid_wheat.tif")

# ----------------------------------------------------------------------
# 3️⃣ Helper utilities (fonts, bbox creator, etc.)
# ----------------------------------------------------------------------
from pathlib import Path
font_manager = plt.matplotlib.font_manager

# Custom fonts used in the original Shiny UI
ginto        = font_manager.FontProperties(fname="./www/GintoNormal-Regular.ttf")
ginto_medium = font_manager.FontProperties(fname="./www/GintoNormal-Medium.ttf")


def create_bbox_from_coords(xmin, xmax, ymin, ymax):
    """Return a simple GeoJSON‑like dict for Plotly map zooming."""
    return {
        "type": "FeatureCollection",
        "features": [{
            "type": "Feature",
            "geometry": {
                "type": "Polygon",
                "coordinates": [[
                    [xmin, ymin], [xmin, ymax],
                    [xmax, ymax], [xmax, ymin],
                    [xmin, ymin]
                ]]
            },
            "properties": {}
        }]
    }


# ----------------------------------------------------------------------
# 4️⃣ Initialise the Dash app & hidden stores
# ----------------------------------------------------------------------
external_stylesheets = ["./assets/css/stylesheet.css"]
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

# Hidden stores – they replace Shiny's reactive values
app.layout = html.Div([

    # ------------------------------------------------------------------
    # 4.1 Stores
    # ------------------------------------------------------------------
    dcc.Store(id="store-historical-wb"),
    dcc.Store(id="store-forecast-wb"),
    dcc.Store(id="store-unweighted-hist"),
    dcc.Store(id="store-unweighted-fcst"),
    dcc.Store(id="store-table"),
    dcc.Store(id="store-timeseries-fig"),
    dcc.Store(id="store-bounds"),
    dcc.Store(id="store-bbox"),
    dcc.Store(id="store-crop-layer"),
    dcc.Store(id="store-crop-prod"),
    dcc.Store(id="store-display-bounds-error", data=False),

    # ------------------------------------------------------------------
    # 4.2 UI – copied from your dash_app.txt (tidied a little)
    # ------------------------------------------------------------------
    html.Div(id='layout-container', children=[

        # Header ---------------------------------------------------------
        html.Div(id='header', children=[
            html.Div(id='logo-container', children=[
                html.Div(id='logo-inner-container', children=[
                    html.Img(id='logo-image',
                             src=app.get_asset_url('woodwell-risk.png'),
                             alt='Woodwell Climate Research Center Risk group logo'),
                    html.Div(id='org-title-container',
                             children=[html.P('Woodwell Risk', id='org-title')])
                ])
            ]),
            html.Div(id='menu-container', children=[
                html.Div(id='menu-inner-container', children=[
                    html.Button('About', id='about-button'),
                    html.Button('Settings', id='settings-button', disabled=True)
                ])
            ])
        ]),

        # Main container ------------------------------------------------
        html.Div(id='container', children=[

            # Sidebar ----------------------------------------------------
            html.Div(id='sidebar-container', children=[
                html.Div(id='sidebar-inner-container', children=[

                    # Integration window selector
                    html.Div(className='select-label-container', children=[
                        html.P('Select an integration window:',
                               className='select-label'),
                        dcc.Dropdown(
                            id='window-select',
                            options=[
                                {'label': '3 month', 'value': 3},
                                {'label': '12 month', 'value': 12}
                            ],
                            clearable=False,
                            searchable=False
                        )
                    ]),

                    # Country selector
                    html.Div(className='select-label-container', children=[
                        html.P('Select a country:', className='select-label')
                    ]),
                    dcc.Dropdown(
                        id='country-select',
                        options=[{'label': c.title(),
                                  'value': c}
                                 for c in sorted(countries.name.unique())],
                        placeholder='Choose a country'
                    ),

                    # State selector
                    html.Div(className='select-label-container', children=[
                        html.P('Select a state:', className='select-label')
                    ]),
                    dcc.Dropdown(
                        id='state-select',
                        options=[],
                        placeholder='Choose a state'
                    ),

                    # Conditional crop selector (visible only for 3‑month window)
                    html.Div(id='conditional-div-crop-select', children=[
                        html.Div(className='select-label-container', children=[
                            html.P('Select a crop', className='select-label')
                        ]),
                        dcc.Dropdown(
                            id='crop-select',
                            options=[
                                {'label': 'None', 'value': 'none'},
                                {'label': 'Barley', 'value': 'barley'},
                                {'label': 'Cocoa', 'value': 'cocoa'},
                                {'label': 'Coffee', 'value': 'coffee'},
                                {'label': 'Cotton', 'value': 'cotton'},
                                {'label': 'Maize', 'value': 'maize'},
                                {'label': 'Rice', 'value': 'rice'},
                                {'label': 'Soy', 'value': 'soy'},
                                {'label': 'Sugarcane', 'value': 'sugarcane'},
                                {'label': 'Wheat', 'value': 'wheat'}
                            ],
                            placeholder='Choose a crop')
                    ]),

                    # Run button
                    html.Div(id='process-data-container',
                             children=[html.Button('Run', id='process-data-button')])
                ])
            ]),

            # Main panel -------------------------------------------------
            html.Div(id='main-container', children=[
                html.Div(id='main-inner-container', children=[

                    dcc.Tabs(id='tabs-container', children=[

                        # Historical data tab
                        dcc.Tab(label='Historical data', value='historical', children=[
                            html.Div(id='iframe-container', children=[
                                html.Iframe(src='https://woodwellrisk.github.io/drought-monitor',
                                            height='100%', width='100%')
                            ])
                        ]),

                        # Timeseries tab
                        dcc.Tab(label='Timeseries', value='timeseries', children=[

                            # Download PNG button
                            html.Div(id='download-timeseries-container',
                                     className='download-container',
                                     children=[
                                         html.Button('Download timeseries',
                                                     className='download-link',
                                                     id='download-timeseries-btn'),
                                         dcc.Download(id='download-timeseries-link')
                                     ]),

                            # Plot area
                            html.Div(id='timeseries-container', children=[
                                html.Div(id='timeseries-toggle-container', children=[
                                    dcc.Checklist(
                                        id='historical-checkbox',
                                        options=[{'label': 'Historical',
                                                  'value': 'Historical'}],
                                        value=['Historical']
                                    ),
                                    dcc.Checklist(
                                        id='forecast-checkbox',
                                        options=[{'label': 'Forecast',
                                                  'value': 'Forecast'}],
                                        value=['Forecast']
                                    )
                                ]),
                                html.Div(id='timeseries-inner-container',
                                         children=[dcc.Graph(id='timeseries')])
                            ]),

                            # Time‑slider (shown only when Historical is checked)
                            html.Div(id='conditional-div-time-slider'),

                            # CSV download button
                            html.Div(id='download-csv-container',
                                     className='download-container',
                                     children=[
                                         html.Button('Download CSV',
                                                     className='download-link',
                                                     id='download-csv-btn'),
                                         dcc.Download(id='download-csv-link')
                                     ]),

                            # Data table
                            html.Div(id='timeseries-table-container',
                                     children=[
                                         dash_table.DataTable(
                                             id='timeseries-table',
                                             columns=[],   # will be filled by callback
                                             data=[],
                                             style_table={'overflowX': 'auto'},
                                             style_header={'backgroundColor': '#f8f9fa',
                                                           'fontWeight': 'bold'},
                                             style_cell={'textAlign': 'left',
                                                         'padding': '5px'}
                                         )
                                     ])
                        ]),

                        # Forecast map tab
                        dcc.Tab(label='Forecast map', value='forecast', children=[
                            html.Div(id='forecast-map-container',
                                     children=[dcc.Graph(id='forecast-map')])
                        ])
                    ])
                ]),

                html.Div(
                    id='about-container',
                    style={'display': 'none',},
                    children=[
                        html.Div(
                            id='about-inner-container',
                            children=[
                                html.Div(
                                    id='about-header',
                                    children=[
                                        html.Button('✕',
                                                    id='close-about-button',
                                                    n_clicks=0,
                                        )
                                    ]
                                ),
                                html.Div(
                                    id='about-body',
                                    children=[
                                        dcc.Markdown(
                                            """
                                            ## Water balance
                                            <p>
                                                This site displays near real-time moisture anomalies along with an experimental 6-month forecast. 
                                                Anomalies are measured as water balance percentiles relative to levels from 1991 to 2020. 
                                                Values close to 0.5 represent normal conditions. Values below and above that mid-value indicate dryer- and wetter-than-normal conditions, respectively. 
                                                Moisture anomalies are monitored on a monthly basis, from 2001 to present.
                                            </p>

                                            ## Applications
                                            <p>
                                                An integration window of 3 months is well suited for applications in agriculture, where shorter cycles of water balance are important.
                                                In order to examine the relationship between water balance anomalies and agriculture, we have provided the spatial extents of several crops.
                                                These can be used to get water balance data within a given country where a specific crop is currently grown (as of 2020).
                                            </p>

                                            <p>
                                                For sectors like the hydropower industry where longer-term patterns in water balance are more relevant, an integration window of 12 months is more appropriate.
                                            </p>

                                            ## Data sources
                                            <p>
                                                The water balance layers were created using <a href="https://cds.climate.copernicus.eu/stac-browser/collections/reanalysis-era5-single-levels-monthly-means?.language=en" target="_blank" rel="noopener noreferrer">ERA5 monthly averaged data</a>.
                                            </p>

                                            <p>
                                                National and state outlines were downloaded from <a href="https://www.naturalearthdata.com/" target="_blank" rel="noopener noreferrer">Natural Earth</a>. 
                                                Crop masks were created using a modified version of the <a href="https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi:10.7910/DVN/SWPENT" target="_blank" rel="noopener noreferrer">SPAM 2020</a> combined rainfed- and irrigated production data for specific crops.
                                            </p>

                                            ## Woodwell Risk
                                            <p>
                                                You can find out more about the Woodwell Risk group and the work that we do on our <a href="https://www.woodwellclimate.org/research-area/risk/" target="_blank" rel="noopener noreferrer">website</a>. 
                                                Whenever possible, we publish our <a href="https://woodwellrisk.github.io/" target="_blank" rel="noopener noreferrer">methodologies</a> and <a href="https://github.com/WoodwellRisk" target="_blank" rel="noopener noreferrer">code</a> on GitHub.
                                            </p>
                                            """,
                                            dangerously_allow_html=True, # we are the only ones writing and publishing the html links
                                        )
                                ])
                        ])
                    ])
            ])
        ])
    ])
])


@app.callback(
    Output('settings-button', 'disabled'),
    Input('about-modal', 'style')
)
def disable_settings(style):
    return style.get('display') != 'none'


@app.callback(
    Output('sidebar-container', 'style'),
    Input('tabs-container', 'value')
)
def toggle_sidebar_visibility(selected_tab):
    """
    Mirrors Shiny's `show_sidebar` effect:
    hide the sidebar when the user is on the “Historical data” tab.
    """
    return {'display': 'none'} if selected_tab == 'historical' else {'display': 'initial'}


# @app.callback(
#     Output('settings-button', 'disabled'),
#     Input('about-button', 'n_clicks'),
#     Input('close-about-button', 'n_clicks')
# )
# def toggle_settings_button(about_clicks, close_clicks):
#     """
#     Matches Shiny's `action_button_click` / `action_button_close_click`.
#     When the About panel is opened, the Settings button becomes disabled.
#     When the About panel is closed, it is re‑enabled.
#     """
#     ctx = dash.callback_context
#     if not ctx.triggered:
#         raise PreventUpdate

#     triggered_id = ctx.triggered_id
#     if triggered_id == 'about-button':
#         return True   # disable Settings
#     elif triggered_id == 'close-about-button':
#         return False  # enable Settings
#     else:
#         raise PreventUpdate


@app.callback(
    Output('main-container', 'className'),
    Input('tabs-container', 'value')
)
def toggle_main_class(selected_tab):
    """
    Replicates Shiny's second `show_sidebar` effect:
    add the `overflow` class when the Timeseries tab is active.
    """
    return 'overflow' if selected_tab == 'timeseries' else ''

# ----------------------------------------------------------------------
# 1️⃣ Update geographic bounds when country / state changes
# ----------------------------------------------------------------------
@app.callback(
    Output('store-bounds', 'data'),   # list [xmin, ymin, xmax, ymax]
    Output('store-bbox',   'data'),   # GeoJSON‑like dict for the map
    Input('country-select', 'value'),
    Input('state-select',   'value')
)
def update_bounds(country, state):
    """Mirrors Shiny's `update_bounds` reactive effect."""
    if not country or not state:
        raise PreventUpdate

    if state == 'All':
        bounds = json.loads(
            countries.query("name == @country").bbox.values[0])
    else:
        bounds = json.loads(
            states.query("name == @state and country == @country")
                  .bbox.values[0])

    xmin, ymin, xmax, ymax = bounds
    bbox_geo = create_bbox_from_coords(xmin, xmax, ymin, ymax)
    return bounds, bbox_geo


# ----------------------------------------------------------------------
# 2️⃣ Populate the state dropdown when a country is chosen
# ----------------------------------------------------------------------
@app.callback(
    Output('state-select', 'options'),
    Output('state-select', 'value'),
    Input('country-select', 'value')
)
def populate_states(selected_country):
    if not selected_country:
        return [], None

    df = states.query("country == @selected_country")
    state_list = ['All'] + sorted(df.name.tolist())
    options = [{'label': s, 'value': s} for s in state_list]
    return options, None


# ----------------------------------------------------------------------
# 3️⃣ Show / hide the crop selector (only for a 3‑month window)
# ----------------------------------------------------------------------
@app.callback(
    Output('conditional-div-crop-select', 'style'),
    Input('window-select', 'value')
)
def toggle_crop_selector(window):
    return {'display': 'block'} if window == 3 else {'display': 'none'}


# ----------------------------------------------------------------------
# 4️⃣ Show / hide the time‑slider (only when Historical is checked)
# ----------------------------------------------------------------------
@app.callback(
    Output('conditional-div-time-slider', 'children'),
    Input('historical-checkbox', 'value')
)
def maybe_show_slider(hist_checked):
    """Replicates Shiny's `show_time_slider` UI block."""
    if not hist_checked:
        return None

    return html.Div(id='time-slider-container', children=[
        html.Button('Last 5 months', id='skip-months-button',
                    className='skip-button'),
        html.Button('Last 5 years',  id='skip-years-button',
                    className='skip-button'),
        html.Button('All data',      id='reset-skip-button',
                    className='skip-button'),
        html.Div(id='time-slider-labels-container', children=[
            html.Div(min_slider_date, className='time-slider-label'),
            html.Div(id='time-slider-output'),
            html.Div(max_slider_date, className='time-slider-label')
        ]),
        dcc.Slider(
            id='time-slider',
            min=0,
            max=len(slider_dates) - 1,
            value=skip_index
        )
    ])


# ----------------------------------------------------------------------
# 5️⃣ Update the stored crop layer & production raster when a crop is chosen
# ----------------------------------------------------------------------
@app.callback(
    Output('store-crop-layer', 'data'),   # vector GeoDataFrame (or None)
    Output('store-crop-prod',  'data'),   # raster xarray (or None)
    Input('crop-select', 'value')
)
def update_crop_layer(crop):
    """Matches the Shiny `match new_crop:` block."""
    if not crop:
        raise PreventUpdate

    crop = crop.lower()
    if crop in ('', 'none'):
        return None, None

    # Vector layer mapping
    layer = {
        'barley':   barley,
        'cocoa':    cocoa,
        'coffee':   coffee,
        'cotton':   cotton,
        'maize':    maize,
        'rice':     rice,
        'soy':      soy,
        'sugarcane':sugarcane,
        'wheat':    wheat,
    }.get(crop)

    # Production raster mapping
    prod = {
        'barley':   barley_production,
        'cocoa':    cocoa_production,
        'coffee':   coffee_production,
        'cotton':   cotton_production,
        'maize':    maize_production,
        'rice':     rice_production,
        'soy':      soy_production,
        'sugarcane':sugarcane_production,
        'wheat':    wheat_production,
    }.get(crop)

    return layer, prod


# ----------------------------------------------------------------------
# 6️⃣ Heavy data processing – triggered by the “Run” button
# ----------------------------------------------------------------------
@app.callback(
    Output('store-historical-wb',      'data'),
    Output('store-forecast-wb',        'data'),
    Output('store-unweighted-hist',   'data'),
    Output('store-unweighted-fcst',   'data'),
    Output('store-display-bounds-error', 'data'),
    Input('process-data-button', 'n_clicks'),
    State('country-select', 'value'),
    State('state-select',   'value'),
    State('crop-select',    'value'),
    State('window-select',  'value'),          # 3 or 12
    State('store-crop-layer','data'),
    State('store-crop-prod', 'data')
)
def process_wb_data(n_clicks, country, state, crop, window,
                    crop_layer, crop_prod):
    """Implements Shiny's `update_wb_data` reactive effect."""
    if not n_clicks:
        raise PreventUpdate

    # Guard against missing selections
    if not country or not state or not window:
        raise PreventUpdate

    # Choose the correct Zarr datasets
    if window == 3:
        hist_ds = h3
        fcst_ds = f3
    elif window == 12:
        hist_ds = h12
        fcst_ds = f12
    else:
        raise ValueError("Window must be 3 or 12")

    # Clip to country / state geometry
    if state == 'All':
        geom = countries.query("name == @country").geometry
    else:
        geom = states.query("name == @state and country == @country").geometry

    hist_clip = hist_ds.rio.clip(geom, all_touched=True, drop=True)
    fcst_clip = fcst_ds.rio.clip(geom, all_touched=True, drop=True)

    # Attach crop attribute (used later for naming)
    hist_clip = hist_clip.assign_attrs({'crop': crop})
    fcst_clip = fcst_clip.assign_attrs({'crop': crop})

    # ------------------------------------------------------------------
    # No crop (or crop == 'none') → just return the clipped datasets
    # ------------------------------------------------------------------
    if crop == 'none' or not crop_layer:
        return (hist_clip.to_dict(),
                fcst_clip.to_dict(),
                hist_clip.to_dict(),
                fcst_clip.to_dict(),
                False)   # no bounds error

    # ------------------------------------------------------------------
    # With a crop → production‑weight the data
    # ------------------------------------------------------------------
    try:
        # Clip to the crop polygon
        hist_crop = hist_clip.rio.clip(crop_layer.geometry,
                                      all_touched=True, drop=True)
        fcst_crop = fcst_clip.rio.clip(crop_layer.geometry,
                                      all_touched=True, drop=True)

        # Bail out if everything is NaN (same logic as Shiny)
        if hist_crop.perc.isnull().all() or fcst_crop.perc.isnull().all():
            return (None, None, None, None, True)

        # Keep un‑weighted copies for the map
        unweighted_hist = hist_crop.copy()
        unweighted_fcst = fcst_crop.copy()

        # --------------------------------------------------------------
        # Production weighting
        # --------------------------------------------------------------
        prod = crop_prod.rio.write_crs(4326)   # ensure WGS‑84
        prod_clip = prod.rio.clip(geom, all_touched=True, drop=True)

        std_prod = prod_clip / prod_clip.sum(skipna=True)
        std_prod = std_prod[['x', 'y', 'production']]

        # Multiply water‑balance by standardized production
        hist_weighted = xr.merge([hist_crop, std_prod])
        hist_weighted = hist_weighted * hist_weighted.production

        fcst_weighted = xr.merge([fcst_crop, std_prod])
        for v in ['5%', '20%', 'perc', '80%', '95%']:
            fcst_weighted[v] = fcst_weighted[v] * fcst_weighted.production

        # Scale by number of rows (as Shiny does)
        nrows_hist = (hist_weighted
                      .drop_vars('spatial_ref')
                      .sel(time=min_date)
                      .to_dataframe()
                      .dropna()
                      .shape[0])
        nrows_fcst = (fcst_weighted
                      .drop_vars('spatial_ref')
                      .sel(time=forecast_date)
                      .to_dataframe()
                      .dropna()
                      .shape[0])

        hist_weighted = hist_weighted * nrows_hist
        for v in ['5%', '20%', 'perc', '80%', '95%']:
            fcst_weighted[v] = fcst_weighted[v] * nrows_fcst

        # Keep only the columns needed for the timeseries view
        hist_final = hist_weighted[['time', 'x', 'y', 'perc']]
        fcst_final = fcst_weighted[['time', 'x', 'y',
                                   '5%', '20%', 'perc', '80%', '95%']]

        return (hist_final.to_dict(),
                fcst_final.to_dict(),
                unweighted_hist.to_dict(),
                unweighted_fcst.to_dict(),
                False)

    except rioxarray.exceptions.NoDataInBounds:
        return (None, None, None, None, True)
    except Exception as exc:
        print(exc)
        return (None, None, None, None, True)


# ----------------------------------------------------------------------
# 7️⃣ Build the timeseries DataFrame that feeds the table & plot
# ----------------------------------------------------------------------
@app.callback(
    Output('store-table', 'data'),          # JSON string of the DataFrame
    Input('store-historical-wb', 'data'),
    Input('store-forecast-wb',   'data'),
    Input('historical-checkbox', 'value'),   # list, e.g. ['Historical']
    Input('forecast-checkbox',   'value'),   # list, e.g. ['Forecast']
    State('country-select', 'value'),
    State('state-select',   'value'),
    State('crop-select',    'value'),
    State('window-select',  'value')
)
def build_timeseries_df(hist_dict, fcst_dict,
                        hist_checked, fcst_checked,
                        country, state, crop, window):
    """Recreates Shiny's `update_dataframe` reactive block."""
    # Re‑create xarray objects from the stored dicts (or None)
    hist = xr.Dataset.from_dict(hist_dict) if hist_dict else None
    fcst = xr.Dataset.from_dict(fcst_dict) if fcst_dict else None

    show_hist = bool(hist_checked)   # non‑empty list → True
    show_fcst = bool(fcst_checked)

    # Early exit – nothing to show
    if ((hist is None and fcst is None) or
        (not show_hist and not show_fcst)):
        empty = pd.DataFrame()
        return empty.to_json(date_format='iso')

    # Helper to attach constant columns
    def _add_common(df, typ):
        df['country'] = country
        df['state']   = state
        df['crop']    = crop
        df['type']    = typ
        df['window']  = int(window)
        return df

    frames = []

    if show_hist and hist is not None:
        df_h = (hist.mean(dim=['x', 'y'])
                .drop_vars('spatial_ref')
                .to_pandas()
                .reset_index())
        df_h['perc'] = df_h['perc'].astype(float).round(4)
        df_h['time'] = df_h['time'].dt.date
        df_h = _add_common(df_h, 'historical')
        df_h = df_h.reindex(columns=['country','state','crop','type','window',
                                    'time','percentile','5%','20%','80%','95%'])
        frames.append(df_h)

    if show_fcst and fcst is not None:
        df_f = (fcst.mean(dim=['x', 'y'])
                .drop_vars('spatial_ref')
                .to_pandas()
                .reset_index())
        for col in ['5%','20%','perc','80%','95%']:
            df_f[col] = df_f[col].astype(float).round(4)
        df_f['time'] = df_f['time'].dt.date
        df_f = _add_common(df_f, 'forecast')
        df_f = df_f.reindex(columns=['country','state','crop','type','window',
                                    'time','percentile','5%','20%','80%','95%'])
        frames.append(df_f)

    result = pd.concat(frames).sort_values('time', ascending=False)\
                              .reset_index(drop=True)

    return result.to_json(date_format='iso')


# ----------------------------------------------------------------------
# 8️⃣ Draw the Matplotlib timeseries, embed it as a Plotly image,
#     and store the raw PNG for the download button.
# ----------------------------------------------------------------------
@app.callback(
    Output('timeseries',           'figure'),   # Plotly figure shown in the UI
    Output('store-timeseries-fig', 'data'),   # Base‑64 PNG for the download callback
    Input('store-table',   'data'),          # JSON string of the DataFrame
    Input('time-slider',   'value'),         # Index into `slider_dates`
    State('historical-checkbox', 'value'),   # List, e.g. ['Historical']
    State('forecast-checkbox',   'value')    # List, e.g. ['Forecast']
)
def draw_timeseries(table_json, slider_idx,
                    hist_checked, fcst_checked):
    """
    Mirrors the Shiny `timeseries` render function.
    Returns:
        * a Plotly figure that simply displays the Matplotlib PNG,
        * a base‑64‑encoded PNG (stored in a hidden Store) for the download button.
    """

    # ------------------------------------------------------------------
    # 1️⃣ Load the DataFrame that was built in `build_timeseries_df`
    # ------------------------------------------------------------------
    if not table_json:
        raise PreventUpdate

    df = pd.read_json(io.StringIO(table_json), orient='records')
    if df.empty:
        raise PreventUpdate

    # ------------------------------------------------------------------
    # 2️⃣ Apply the time‑slider filter (same logic as Shiny)
    # ------------------------------------------------------------------
    filter_date_str = slider_dates[slider_idx]          # e.g. "1995-03-01"
    filter_ts = pd.Timestamp(filter_date_str)

    df = df[pd.to_datetime(df['time']) >= filter_ts]

    # ------------------------------------------------------------------
    # 3️⃣ Determine which layers are active
    # ------------------------------------------------------------------
    show_hist = bool(hist_checked)      # non‑empty list → True
    show_fcst = bool(fcst_checked)

    # ------------------------------------------------------------------
    # 4️⃣ Plot styling constants (colors, legend handles)
    # ------------------------------------------------------------------
    timeseries_color       = '#1b1e23'
    high_certainty_color   = '#f4c1c1'
    medium_certainty_color = '#f69a9a'

    # Legend handles – identical to the ones used in Shiny
    historical_handle = Line2D([0], [0],
        color=timeseries_color,
        markerfacecolor=timeseries_color,
        label='Historical',
        linewidth=1.25)

    forecast_handle = Line2D([0], [0],
        color=timeseries_color,
        markerfacecolor=timeseries_color,
        label='Mean forecast',
        linestyle='--',
        linewidth=1.25)

    medium_handle = Line2D([0], [0],
        color=medium_certainty_color,
        markerfacecolor=medium_certainty_color,
        label='60%',
        linewidth=3)

    high_handle = Line2D([0], [0],
        color=high_certainty_color,
        markerfacecolor=high_certainty_color,
        label='90%',
        linewidth=3)

    # ------------------------------------------------------------------
    # 5️⃣ Build the Matplotlib figure (exactly the same visual as Shiny)
    # ------------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(8, 4))

    # ---- Both historical and forecast are displayed --------------------
    if show_hist and show_fcst:
        # Shiny splits the dataframe to hide the gap between historic &
        # forecast series. We replicate that logic here.
        df_historical = df.iloc[6:, :]          # historic portion (after gap)
        df_forecast   = df.iloc[0:7, :]          # forecast portion (incl. overlap)
        df_bridge     = df.iloc[5:7, :]          # tiny bridge to cover the gap

        # Plot forecast uncertainty first (so it sits underneath the line)
        ax.fill_between(df_forecast['time'],
                        df_forecast['5%'],
                        df_forecast['95%'],
                        color=high_certainty_color)

        ax.fill_between(df_forecast['time'],
                        df_forecast['20%'],
                        df_forecast['80%'],
                        color=medium_certainty_color)

        # Forecast mean (dashed)
        ax.plot(df_forecast['time'],
                df_forecast['percentile'],
                color=timeseries_color,
                linestyle='--')

        # Historical mean (solid)
        ax.plot(df_historical['time'],
                df_historical['percentile'],
                color=timeseries_color)

        # Bridge line – closes the visual gap
        ax.plot(df_bridge['time'],
                df_bridge['percentile'],
                color=timeseries_color)

        legend_items = [historical_handle,
                        forecast_handle,
                        medium_handle,
                        high_handle]

    # ---- Historical only ------------------------------------------------
    elif show_hist and not show_fcst:
        ax.plot(df['time'],
                df['percentile'],
                color=timeseries_color)

        legend_items = [historical_handle]

    # ---- Forecast only --------------------------------------------------
    elif show_fcst and not show_hist:
        ax.fill_between(df['time'],
                        df['5%'],
                        df['95%'],
                        color=high_certainty_color)

        ax.fill_between(df['time'],
                        df['20%'],
                        df['80%'],
                        color=medium_certainty_color)

        ax.plot(df['time'],
                df['percentile'],
                color=timeseries_color,
                linestyle='--')

        # Use month‑year formatter for the x‑axis (matches Shiny)
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%m-%y'))

        legend_items = [forecast_handle,
                        medium_handle,
                        high_handle]

    else:
        # No layer selected – nothing to draw
        raise PreventUpdate

    # ------------------------------------------------------------------
    # 6️⃣ Axis labels, limits, fonts (exactly as in Shiny)
    # ------------------------------------------------------------------
    ax.set_xlabel('Time', fontproperties=ginto_medium)
    ax.set_ylabel('Water balance percentile', fontproperties=ginto_medium)

    # Show month‑year ticks only when we have ≤60 points (same rule as Shiny)
    if len(df) <= 60:
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%m-%y'))

    # Apply the custom font to tick labels
    for label in ax.get_xticklabels():
        label.set_fontproperties(ginto)
    for label in ax.get_yticklabels():
        label.set_fontproperties(ginto)

    ax.margins(0, 0)
    ax.set_ylim(-0.05, 1.05)

    # Background colours
    fig.patch.set_facecolor('#f7f7f7')
    ax.set_facecolor('#f7f7f7')

    plt.tight_layout()
    fig.subplots_adjust(bottom=0.25)

    # ------------------------------------------------------------------
    # 7️⃣ Legend (position mirrors Shiny)
    # ------------------------------------------------------------------
    if legend_items:
        fig.legend(handles=legend_items,
                   ncol=len(legend_items),
                   loc='lower center',
                   bbox_to_anchor=(0 if len(legend_items) == 3 else 0.025,
                                   0, 1, 0.5),
                   fontsize='small',
                   facecolor='white',
                   frameon=False)

    # ------------------------------------------------------------------
    # 8️⃣ Convert Matplotlib → Plotly image (so Dash can display it)
    # ------------------------------------------------------------------
    buf = io.BytesIO()
    fig.savefig(buf, format='png', dpi=150)
    buf.seek(0)
    png_base64 = base64.b64encode(buf.read()).decode()

    plotly_fig = {
        "data": [{
            "type": "image",
            "source": f"data:image/png;base64,{png_base64}",
            "xref": "paper",
            "yref": "paper",
            "x": 0,
            "y": 1,
            "sizex": 1,
            "sizey": 1,
            "sizing": "stretch",
            "layer": "above"
        }],
        "layout": {
            "margin": {"l": 0, "r": 0, "t": 0, "b": 0},
            "paper_bgcolor": "#f7f7f7",
            "plot_bgcolor": "#f7f7f7",
            "xaxis": {"visible": False},
            "yaxis": {"visible": False},
            "height": 400   # adjust to match your UI layout if needed
        }
    }

    # ------------------------------------------------------------------
    # 9️⃣ Store the raw PNG (base‑64) for the download‑timeseries callback
    # ------------------------------------------------------------------
    # We reuse the same PNG we just generated; encode it again for storage.
    # The download callback will simply decode this string.
    buf_for_store = io.BytesIO()
    fig.savefig(buf_for_store, format='png', dpi=300)
    buf_for_store.seek(0)
    png_for_store = base64.b64encode(buf_for_store.read()).decode()

    # Return the Plotly figure for on‑screen display and the stored PNG.
    return plotly_fig, png_for_store


@app.callback(
    Output('timeseries-table', 'columns'),
    Output('timeseries-table', 'data'),
    Input('store-table', 'data')
)
def populate_timeseries_table(table_json):
    """
    Takes the JSON DataFrame produced by `build_timeseries_df`,
    extracts the column definitions and rows for the Dash DataTable.
    """
    if not table_json:
        raise PreventUpdate

    df = pd.read_json(io.StringIO(table_json), orient='records')
    if df.empty:
        # Empty table – no columns
        return [], []

    # Build column spec for dash_table.DataTable
    columns = [{"name": col, "id": col} for col in df.columns]
    data = df.to_dict('records')
    return columns, data


@app.callback(
    Output("download-timeseries-link", "data"),
    Input("download-timeseries-btn", "n_clicks"),
    State("store-timeseries-fig", "data"),
    prevent_initial_call=True,
)
def download_timeseries(n_clicks, png_base64):
    """
    Sends the PNG that was stored by `draw_timeseries`.
    The filename mirrors the Shiny version.
    """
    if not png_base64:
        raise PreventUpdate

    img_bytes = base64.b64decode(png_base64)

    # Build a filename similar to the Shiny logic
    # (you can adapt the naming scheme if you wish)
    filename = f"drought-timeseries.png"

    return dcc.send_bytes(lambda buff: buff.write(img_bytes), filename=filename)


@app.callback(
    Output("download-csv-link", "data"),
    Input("download-csv-btn", "n_clicks"),
    State("store-table", "data"),
    prevent_initial_call=True,
)
def download_csv(n_clicks, table_json):
    """
    Streams the CSV representation of the DataFrame that lives in
    `store-table`.  The CSV format matches the Shiny `download_csv_link`.
    """
    if not table_json:
        raise PreventUpdate

    df = pd.read_json(io.StringIO(table_json), orient='records')
    if df.empty:
        raise PreventUpdate

    csv_buffer = io.BytesIO()
    df.to_csv(csv_buffer, index=False)
    csv_buffer.seek(0)

    filename = "drought-table.csv"
    return dcc.send_bytes(lambda buff: buff.write(csv_buffer.read()),
                          filename=filename)


@app.callback(
    Output('forecast-map', 'figure'),
    Input('store-unweighted-fcst', 'data'),
    Input('store-bbox',           'data'),
    Input('country-select',       'value'),
    Input('state-select',         'value')
)
def render_forecast_map(fcst_json, bbox_geojson, country, state):
    """
    Replicates the Shiny `forecast_map` UI block.
    Uses Plotly Express `scatter_mapbox` (or `scatter_map`) to animate
    the forecast percentiles.
    """
    if not fcst_json or not bbox_geojson:
        raise PreventUpdate

    # Re‑create the xarray dataset from the stored dict
    fcst = xr.Dataset.from_dict(fcst_json)

    # Clip to the country geometry (same as Shiny)
    country_geom = countries.query("name == @country").geometry
    fcst_country = fcst.rio.clip(country_geom, all_touched=True, drop=True)

    # Convert to a tidy DataFrame for Plotly
    df = (fcst_country['perc']
          .drop_vars('spatial_ref')
          .to_dataframe()
          .dropna()
          .reset_index())
    df.columns = ['time', 'y', 'x', 'Percentile']

    # Human‑readable month‑year labels for the slider
    formatted_dates = [pd.to_datetime(d).strftime("%b-%Y")
                       for d in forecast_dates]

    # Compute a sensible zoom level based on the bbox
    xmin, ymin, xmax, ymax = json.loads(json.dumps(bbox_geojson['features'][0]['geometry']['coordinates'][0]))
    max_bounds = max(abs(xmin - xmax), abs(ymin - ymax)) * 111
    zoom = max(3, 11 - np.log(max_bounds))   # keep a minimum zoom

    fig = px.scatter_mapbox(
        data_frame=df,
        lat='y',
        lon='x',
        color='Percentile',
        color_continuous_scale=px.colors.diverging.RdYlBu,
        range_color=[0, 1],
        hover_data={'time': False, 'x': False, 'y': False,
                    'Percentile': ':.3f'},
        zoom=zoom,
        height=445,
        animation_frame='time',
        mapbox_style='carto-positron'   # matches the Shiny map style
    )

    # Remove the default Play/Pause buttons – we’ll use the custom slider
    fig.layout.updatemenus = []   # same as Shiny's `fig["layout"].pop("updatemenus")`

    # Build a custom slider that mimics the Shiny UI
    steps = []
    for idx, label in enumerate(formatted_dates):
        step = dict(method='animate',
                    label=label,
                    args=[[label],  # the frame name
                          {"duration": 500, "ease": "linear"}])
        steps.append(step)

    fig.update_layout(
        sliders=[{
            "currentvalue": {"prefix": "Time: "},
            "len": 0.8,
            "pad": {"b": 10, "t": 0},
            "steps": steps,
            "bgcolor": "#f7f7f7",
            "bordercolor": "#1b1e23",
            "activebgcolor": "#1b1e23",
            "tickcolor": "#1b1e23",
            "font": {"color": "#1b1e23", "family": "Ginto normal"}
        }],
        margin=dict(l=0, r=0, t=0, b=0),
        paper_bgcolor="#f7f7f7",
        mapbox=dict(center=dict(lat=df['y'].mean(),
                               lon=df['x'].mean()))
    )

    # Add the country/state outline (GeoJSON) as a separate trace
    fig.add_trace(go.Scattermapbox(
        lon=[coord[0] for coord in bbox_geojson['features'][0]['geometry']['coordinates'][0]],
        lat=[coord[1] for coord in bbox_geojson['features'][0]['geometry']['coordinates'][0]],
        mode='lines',
        line=dict(color="#1b1e23", width=2),
        hoverinfo='skip',
        showlegend=False
    ))

    return fig


@app.callback(
    Output('time-slider', 'value'),
    Input('skip-months-button', 'n_clicks'),
    Input('skip-years-button',  'n_clicks'),
    Input('reset-skip-button',  'n_clicks'),
    prevent_initial_call=True
)
def handle_skip_buttons(skip_months, skip_years, reset):
    """
    Mirrors the Shiny effects that update the slider when the user clicks
    “Last 5 months”, “Last 5 years”, or “All data”.
    """
    triggered = ctx.triggered_id

    if triggered == 'skip-months-button':
        return max_index                     # show the last 5 months
    elif triggered == 'skip-years-button':
        return skip_index                    # show the last 5 years
    elif triggered == 'reset-skip-button':
        return min_index                     # show all data
    else:
        raise PreventUpdate


@app.callback(
    Output('time-slider-output', 'children'),
    Input('time-slider', 'value')
)
def update_slider_output(idx):
    """
    Equivalent to Shiny's `time_slider_output` render.text.
    """
    if idx is None or idx < 0 or idx >= len(slider_dates):
        raise PreventUpdate
    return slider_dates[idx]


@app.callback(
    Output('forecast-map-container', 'children'),
    Output('timeseries-inner-container', 'children'),
    Input('store-display-bounds-error', 'data'),
    State('crop-select', 'value'),
    State('country-select', 'value')
)
def show_bounds_error(display_error, crop, country):
    """
    Inserts or removes the error banner that Shiny added with
    `ui.insert_ui`.  In Dash we simply replace the children of the
    containers with the error message when needed.
    """
    if not display_error:
        # No error – keep the original children (the map / timeseries plot)
        raise PreventUpdate

    # Build the error HTML (same text as Shiny)
    error_html = html.Div(
        className='bounds-error-container',
        children=html.Div(
            className='bounds-error',
            children=('No water balance data to show. This is likely because '
                      'the crop you chose is not grown in the country / state '
                      'in question or the data resolution is too low.')
        )
    )

    # Replace both containers with the error banner
    return error_html, error_html


# run the app
if __name__ == '__main__':
    app.run(debug=True)