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

BASE_MAP_ATTRIBUTION = ('© <a href="https://www.openstreetmap.org/copyright">'
                        'OpenStreetMap</a> contributors')
N_COLORBAR_ROWS = 6


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


def get_element_after(current_element, iterator):
    """Returns the element that comes after the given element of the given
    iterator.
    """
    for element in iterator:
        if element == current_element:
            break
    return next(iterator, None)


def format_bounds(bounds):
    """Formats tuple of bounds for Leaflet.

    Args:
        bounds: A 4 element tuple of bounds.

    Returns:
        Nested list as required by Leaflet.
    """
    return [[bounds[1], bounds[0]], [bounds[3], bounds[2]]]


def get_colorbar(stretch_range, colormap):
    """Creates a colorbar component for a dash_leaflet.Map.

    Args:
        stretch_range: list of lower and upper limit for colorbar.
        colormap: string of color palette (like "virdis", "greens", etc.)

    Returns:
        dash_leaflet.Colobar component.
    """
    ctg = [
        f'{cmap["value"]:.3f}+'
        for cmap in get_colormap(stretch_range=stretch_range,
                                 colormap=colormap,
                                 num_values=N_COLORBAR_ROWS)
    ]

    return dlx.categorical_colorbar(categories=ctg,
                                    colorscale=colormap,
                                    width=20,
                                    height=100,
                                    position="bottomright")


def get_app():
    """Create a new Dash instance with a Terracotta instance embedded in it.

    Args:
        tc_app: Flask instance of Terracotta

    Returns:
        A Flask instance of a Dash app.
    """
    # pylint: disable=unused-variable
    data = _get_data()
    app = dash.Dash(__name__, server=False)
    app.title = 'Taswira'
    options = [{'label': k, 'value': k} for k in list(data)]
    app.layout = html.Div(
        [
            dcc.Store(id='raster-layers-store'),
            dcc.Dropdown(id='title-dropdown',
                         clearable=False,
                         options=options,
                         value=options[0]['value'],
                         style={
                             'position': 'relative',
                             'top': '5px',
                             'zIndex': '500',
                             'height': '0',
                             'maxWidth': '200px',
                             'marginLeft': 'auto',
                             'marginRight': '10px'
                         }),
            html.Div(dl.Map([
                dl.TileLayer(attribution=BASE_MAP_ATTRIBUTION),
                dl.LayerGroup(id='raster-layers'),
                dl.LayerGroup(id='colorbar-layer')
            ],
                            id='main-map'),
                     id='main-map-div',
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
                    'zIndex': '500',
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
                    'zIndex': '500',
                    'height': '0',
                    'marginRight': '9em'
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
            'fontFamily': 'sans-serif'
        })

    app.clientside_callback(
        """
        function(year, layers){
            return layers.map(l => {
                console.log(typeof l.props.id, typeof year);
                if (Number(l.props.id) === year)
                    return {...l,props: {...l.props, opacity: 1.0}};
                return l;
            });
        }
        """, Output('raster-layers', 'children'),
        [Input('year-slider', 'value'),
         Input('raster-layers-store', 'data')],
        [State('raster-layers', 'children')])

    @app.callback([
        Output('raster-layers-store', 'data'),
        Output('colorbar-layer', 'children'),
        Output('main-map', 'bounds')
    ], [Input('title-dropdown', 'value')])
    def update_raster_layers_colobar_map_bounds(title):
        ranges = [data[title][year]['range'] for year in data[title].keys()]
        lowers, uppers = list(zip(*ranges))
        stretch_range = [min(lowers), max(uppers)]

        xyz = '{z}/{x}/{y}'
        layers = []
        for year in data[title]:
            raster_data = data[title][year]
            colormap = raster_data['metadata']['colormap']
            bounds = format_bounds(raster_data['bounds'])
            layers.append(
                dl.TileLayer(
                    url=
                    f'/singleband/{title}/{year}/{xyz}.png?colormap={colormap}',
                    opacity=0,
                    id=year))

        colorbar = get_colorbar(stretch_range, colormap)

        return layers, [colorbar], bounds

    @app.callback([
        Output('year-slider', 'marks'),
        Output('year-slider', 'min'),
        Output('year-slider', 'max'),
    ], [Input('title-dropdown', 'value')])
    def update_slider(title):
        mark_style = {'color': '#fff', 'textShadow': '1px 1px 2px #000'}
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
                new_value = get_element_after(str(current_value),
                                              iter(marks.keys()))
                if new_value is not None:
                    return int(new_value)
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
            y_margs.append(meta['metadata']['indicator_value'])
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
