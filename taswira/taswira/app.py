"""The Dash-based front-end"""
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_leaflet as dl
import dash_leaflet.express as dlx
import plotly.graph_objects as go
import terracotta as tc
from dash.dependencies import Input, Output, State
from terracotta.handlers.colormap import colormap as get_colormap


def _get_data():
    driver = tc.get_driver(tc.get_settings().DRIVER_PATH)
    data = {}
    with driver.connect():
        for k in driver.get_datasets():
            title, year = k
            if not title in data:
                data[title] = {}
            data[title][year] = driver.get_metadata(k)
    return data


def format_bounds(bounds):
    """Formats tuple of bounds for Leaflet.

    Args:
        bounds: A 4 element tuple of bounds.

    Returns:
        Nested list as required by Leaflet.
    """
    return [[bounds[1], bounds[0]], [bounds[3], bounds[2]]]


def get_app(tc_app):
    """Create a new Dash instance with a Terracotta instance embedded in it.

    Args:
        tc_app: Flask instance of Terracotta

    Returns:
        A Flask instance of a Dash app.
    """
    # pylint: disable=unused-variable
    data = _get_data()
    app = dash.Dash(__name__, server=tc_app)
    app.title = 'Taswira'
    options = [{'label': k, 'value': k} for k in list(data)]
    app.layout = html.Div(
        [
            dcc.Dropdown(id='title-dropdown',
                         clearable=False,
                         options=options,
                         value=options[0]['value'],
                         style={
                             'position': 'relative',
                             'top': '5px',
                             'z-index': '500',
                             'height': '0',
                             'max-width': '200px',
                             'margin-left': 'auto',
                             'margin-right': '10px'
                         }),
            html.Div(id='main-map',
                     style={
                         'position': 'relative',
                         'width': '100%',
                         'height': '70%',
                         'top': '0',
                         'left': '0'
                     }),
            html.Div(
                [
                    html.Button(id='animation-btn'),
                    dcc.Interval(id='animation-interval', disabled=True)
                ],
                style={
                    'position': 'relative',
                    'top': '-50px',
                    'left': '10px',
                    'z-index': '500',
                    'height': '0',
                },
                id="animation-control"),
            html.Div(
                [dcc.Slider(
                    id='year-slider',
                    step=None,
                    value=0,
                )],
                style={
                    'position': 'relative',
                    'top': '-50px',
                    'left': '60px',
                    'z-index': '500',
                    'height': '0',
                    'margin-right': '9em'
                },
                id='year-slider-div'),
            dcc.Graph(id='indicator-change-graph',
                      responsive=True,
                      style={
                          'width': '100%',
                          'height': '30%'
                      })
        ],
        style={
            'position': 'absolute',
            'width': '100%',
            'height': '100%',
            'top': '0',
            'left': '0',
            'font-family': 'sans-serif'
        })

    @app.callback(
        Output('main-map', 'children'),
        [Input('title-dropdown', 'value'),
         Input('year-slider', 'value')])
    def update_map(title, year):
        raster_data = data[title][str(year)]
        bounds = format_bounds(raster_data['bounds'])
        colormap = raster_data['metadata']['colormap']

        ctg = []
        for cmap in get_colormap(stretch_range=raster_data['range'],
                                 colormap=colormap,
                                 num_values=6):
            ctg.append(f'{cmap["value"]:.3f}+')

        colorbar = dlx.categorical_colorbar(categories=ctg,
                                            colorscale=colormap,
                                            width=20,
                                            height=100,
                                            position="bottomright")

        xyz = '{z}/{x}/{y}'
        leafmap = dl.Map([
            dl.TileLayer(
                attribution=
                '© <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
            ),
            dl.TileLayer(
                url=f'/singleband/{title}/{year}/{xyz}.png?colormap={colormap}'
            ), colorbar
        ],
                         bounds=bounds)
        return leafmap

    @app.callback([
        Output('year-slider', 'marks'),
        Output('year-slider', 'min'),
        Output('year-slider', 'max'),
    ], [Input('title-dropdown', 'value')])
    def update_slider(title):
        mark_style = {'color': '#fff', 'text-shadow': '1px 1px 2px #000'}
        marks = {
            int(k): dict(label=k, style=mark_style)
            for k in data[title].keys()
        }
        min_value = min(marks.keys())
        max_value = max(marks.keys())

        return marks, min_value, max_value

    @app.callback(Output('year-slider', 'value'), [
        Input('year-slider', 'marks'),
        Input('animation-interval', 'n_intervals')
    ], [State('year-slider', 'value')])
    def update_slider_value(marks, n_intervals, current_value):  # pylint: disable=unused-argument
        ctx = dash.callback_context
        min_value = min(marks.keys())

        if ctx.triggered:
            trigger = ctx.triggered[0]['prop_id'].split('.')[0]
            trigger_value = ctx.triggered[0]['value']
            if trigger == 'animation-interval' and trigger_value:
                keys = iter(marks.keys())
                for mark in keys:
                    if mark == str(current_value):
                        try:
                            return int(next(keys))
                        except StopIteration:
                            pass
            elif current_value:
                return current_value

        return int(min_value)

    @app.callback(Output('indicator-change-graph', 'figure'),
                  [Input('title-dropdown', 'value')])
    def update_graph(title):
        fig = go.Figure()
        x_marks = []
        y_margs = []
        for year, meta in data[title].items():
            x_marks.append(year)
            y_margs.append(meta['metadata']['value'])
        fig.add_trace(go.Scatter(x=x_marks, y=y_margs, mode='lines+markers'))

        unit = ''
        for _, meta in data[title].items():
            unit = meta['metadata']['unit']
            break

        fig.update_layout(autosize=False,
                          xaxis_title='Year',
                          yaxis_title=f'{title} ({unit})',
                          xaxis_type='category',
                          height=150,
                          margin=dict(t=10, b=0))
        return fig

    @app.callback(Output('animation-control', 'children'),
                  [Input('animation-btn', 'n_clicks')], [
                      State('animation-btn', 'value'),
                  ])
    def update_animation_control(n_clicks, current_value):  # pylint: disable=unused-argument
        new_value = 'pause' if current_value == 'play' else 'play'
        btn = html.Button(new_value.capitalize(),
                          value=new_value,
                          id='animation-btn',
                          style={
                              'height': '30px',
                              'backgroundColor': '#fff',
                              'textAlign': 'center',
                              'borderRadius': '4px',
                              'border': '2px solid rgba(0,0,0,0.2)',
                              'fontWeight': 'bold'
                          })
        is_paused = (new_value == 'play')
        interval = dcc.Interval(id='animation-interval', disabled=is_paused)
        return [btn, interval]

    return app
