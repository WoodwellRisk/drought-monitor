from shiny import App, Inputs, Outputs, Session, ui, render, reactive
from shinywidgets import output_widget, render_widget   

import altair as alt
from shinywidgets import render_altair
from vega_datasets import data
# alt.data_transformers.enable("vegafusion")

# print(plotly.io.renderers)
# plotly.io.renderers['svg'].config['displayModeBar'] = False

# @reactive.effect
# @reactive.event(historcial_wb, forecast_wb)
# def update_dataframe():
#     historical = historcial_wb()
#     forecast = forecast_wb()

#     # on app start or page reload, these variables will be empty
#     if(historical is None and forecast is None):
#         ...

#     try:
#         ...

#     except:
#         print("ERROR")
#         df_historical.set([])
#         df_forecast.set([])


# @reactive.effect
# @reactive.event(forecast_wb)
# def update_forecast_wb():
#     forecast = forecast_wb()
#     print(forecast)
#     print()

    # @render.plot
    # def plot():
        # name = country_name()
        # forecast = forecast_wb()
        # historical = historical_wb()

        # if(forecast is None and historical is None):
        #     return

        # df = forecast.mean(dim=['x', 'y']).drop_vars('spatial_ref').to_pandas().reset_index()
        
        # plt.plot(df['time'], df['perc'], color='black', linestyle='--')

# @render_widget
# https://shinylive.io/py/editor/#code=NobwRAdghgtgpmAXGKAHVA6VBPMAaMAYwHsIAXOcpMAMwCdiYACAZwAsBLCbJjmVYnTJMAVAB0IfAUKYwoZVABtiZRRwBGWbEpVMoLJkrISJaVAH0ArhyYBeJtaxQA5nHM1F1gCYAKCUwCHDgxiSwUw8x0yPzAvShZI5WMwAEo8f0DHLlQIljU4uh8OLzsmMUhyvCZFKHU4RVLyvOK4OkrZLlKARgAGKrkAD1KAVj6mADcoTzhunpSJeYgJOJpWVvHWoogcsirQ8N21lhYOUhTEDICAAX2dy6YrukoCjD4XOHuVpjiIBKifc73QK8fiCYQUfg0DiKD4QYHAmheKqoeRsUoQ1BQmEYGAAaxYGJ8LEsNChQ3sAHIMCxxs4KYt4YEBgZ7GoCT46FAIK4tjsMBAAQBqLopBmMpjYFlMYBdAC6IhhAuZYsZUOcVSg5MMijI1Ms6iiLABQMCmupEJ8zKqkqY-SgdFxrRoMGE9nKZVSJoCZpYcDI5gGNTqihiAA0mGQOKoPp64eKfX7zNgg-UYgBNCNRmHlFXwtXUqAbNU+FFkNi54FPMiWOhwkBNOiEcqIVhkQql8tVcoAd2KZebHoAbD0eqgBu1yjRBHJkhcwDTnOUAL4mOOM1dmUoAQXQPjMVg4VV9dA2dBSYCXsqAA
@render.image
def plot():
    import plotly.graph_objects as go
    import tempfile
    fd, path = tempfile.mkstemp(suffix = '.svg')
    print(fd, path)

    # fig = go.Figure(
    #     data=[go.Bar(y=[2, 1, 3])],
    #     # layout_title_text="A Figure Displayed with the 'svg' Renderer"

    # )

    # fig.update_layout(
    #     margin=dict(l=0, r=0, t=0, b=0),
    #     paper_bgcolor="#f7f7f7",
    #     # autosize=True
    #     # width='100%',
    #     # height=250,
    # )
    
    # fig.write_image(path, width=1980, height=1080)

    # name = country_name()

    # xs = list(range(input.n()+1))
    xs = list(range(30))
    ys = [1]*len(xs)
    fig, ax = plt.subplots()
    ax.stem(xs, ys , markerfmt = " ")
    ax.set_xlabel("X title")
    ax.set_ylabel("Y title")
    fig.savefig(path)

    return {"src": str(path), "format":"svg"}


# @render_widget 
# def forecast_map(alt="a map showing the borders of a country of interest"):
    # return
        # config = {'responsive': False, 'displayModeBar': True, }#'staticPlot': True}

        # # https://stackoverflow.com/questions/73338999/how-to-center-plotly-scatter-geo-to-a-specific-country-in-python
        # fig = px.scatter_geo(df,
        #             locations="iso_alpha",
        #             size="pop",
        #             projection="natural earth"
        #             )

        # fig.update_geos(
        #     visible=True, resolution=50,
        #     showcountries=True, countrycolor="Black",
        #     # showsubunits=True, subunitcolor="Blue"
        # )

        # fig.update_layout(
        #     autosize=True,
        #     height=400,
        #     margin={"r":0,"t":0,"l":0,"b":0},
        #     geo=dict(
        #         center=dict(
        #             lat=51.0057,
        #             lon=13.7274
        #         ),
        #         # scope='europe',
        #         projection_scale=6
        #     )
        # )

        # fig = go.Figure(go.Scattergeo())
        # fig.update_geos(
        #     visible=False, resolution=50,
        #     showcountries=True, countrycolor="RebeccaPurple"
        # )
        # fig.update_layout(height=300, margin={"r":0,"t":0,"l":0,"b":0}, config=config)

        # fig = go.Figure(go.Scattergeo())
        # fig.update_geos(lataxis_showgrid=True, lonaxis_showgrid=True)
        # fig.update_layout(height=300, margin={"r":0,"t":0,"l":0,"b":0})

        # return fig

@render_altair
def scatterplot():
    # mean = [0, 0]
    # cov = [[1, 0.5], [0.5, 1]]
    # data = np.random.multivariate_normal(mean, cov, 4000)
    # df = pd.DataFrame(data, columns=['x', 'y'])
    # print("ALTER METHOD")
    # print(df)
    # print()

    # fig = alt.Chart(df).mark_circle(size=60, color='#b6377a').encode(
    #     x='x',
    #     y='y')
    
    # return fig

    # # https://altair-viz.github.io/gallery/groupby-map.html

    # airports = data.airports.url
    # states = alt.topo_feature(data.us_10m.url, feature='states')

    # # US states background
    # background = alt.Chart(states).mark_geoshape(
    #     fill='lightgray',
    #     stroke='white'
    # ).properties(
    #     width=500,
    #     height=300
    # ).project('albersUsa')

    # # Airports grouped by state
    # points = alt.Chart(airports, title='Number of airports in US').transform_aggregate(
    #     latitude='mean(latitude)',
    #     longitude='mean(longitude)',
    #     count='count()',
    #     groupby=['state']
    # ).mark_circle().encode(
    #     longitude='longitude:Q',
    #     latitude='latitude:Q',
    #     size=alt.Size('count:Q').title('Number of Airports'),
    #     color=alt.value('steelblue'),
    #     tooltip=['state:N','count:Q']
    # )

    # return (background + points)

    # https://idl.uw.edu/visualization-curriculum/altair_cartographic.html
    usa = data.us_10m.url
    unemp = data.unemployment.url

    fig = alt.Chart(alt.topo_feature(usa, 'counties')).mark_geoshape(
        stroke='#aaa', strokeWidth=0.25
    ).transform_lookup(
        lookup='id', from_=alt.LookupData(data=unemp, key='id', fields=['rate'])
    ).encode(
        alt.Color('rate:Q',
                scale=alt.Scale(domain=[0, 0.3], clamp=True), 
                legend=alt.Legend(format='%')),
        alt.Tooltip('rate:Q', format='.0%')
    ).project(
        type='albersUsa'
    ).configure_view(
        stroke=None
    )

    return fig


@render_altair
def random_data():
    # # https://altair-viz.github.io/user_guide/data.html
    # rand = np.random.RandomState(0)

    # data = pd.DataFrame({'value': rand.randn(100).cumsum()},
    #                     index=pd.date_range('2018', freq='D', periods=100)).reset_index()
    

    # fig = alt.Chart(data.reset_index()).mark_line().encode(
    #     x='index:T',
    #     y='value:Q'
    # ).interactive()

    # return fig

    # @alt.theme.register("sfmono", enable=True)
    # def sfmono():
    #     font = "SF Mono"
        
    #     return {
    #         "config" : {
    #             "title": {'font': font},
    #             "axis": {
    #                 "labelFont": font,
    #                 "titleFont": font
    #             },
    #             "header": {
    #                 "labelFont": font,
    #                 "titleFont": font
    #             },
    #             "legend": {
    #                 "labelFont": font,
    #                 "titleFont": font
    #             }
    #         }
    #     }

    # https://altair-viz.github.io/gallery/line_with_ci.html
    alt.renderers.set_embed_options(actions=False)
    source = data.cars()

    line = alt.Chart(source).mark_line().encode(
        x='Year',
        y='mean(Miles_per_Gallon)'
    )

    band = alt.Chart(source).mark_errorband(extent='ci').encode(
        x='Year',
        y=alt.Y('Miles_per_Gallon').title('Miles / Gallon'),
        # y='Miles_per_Gallon'
        tooltip=alt.value(None),
    )
    
    fig = (band + line).configure_axis(
        labelFont='Ginto Normal',
        labelFontSize=15,
        titleFont='Ginto Normal',
        titleFontSize=15
    )

    # fig.save('altair_timeseries.svg')
    # fig.save('altair_timeseries.png')

    return fig

