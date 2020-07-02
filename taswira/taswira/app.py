"""The Dash-based front-end"""
import dash
import dash_html_components as html
import dash_leaflet as dl
import terracotta as tc


def _get_data():
    driver = tc.get_driver(tc.get_settings().DRIVER_PATH)
    with driver.connect():
        return [
            dict(title=k[0], year=k[1], **driver.get_metadata(k))
            for k, v in driver.get_datasets().items()
        ]


def format_bounds(bounds):
    """Formats tuple of bounds for Leaflet.

    Args:
        bounds: A 4 element tuple of bounds.

    Returns:
        Nested list as required by Leaflet.
    """
    return [[bounds[1], bounds[0]], [bounds[3], bounds[2]]]


def _make_map(tile_url, bounds):
    style = {'width': '500px', 'height': '500px'}

    return dl.Map([dl.TileLayer(), dl.TileLayer(url=tile_url)],
                  id='main-map',
                  bounds=bounds,
                  style=style)


def get_app(tc_app):
    """Create a new Dash instance with a Terracotta instance embedded in it.

    Args:
        tc_app: Flask instance of Terracotta

    Returns:
        A Flask instance of a Dash app.
    """
    data = _get_data()
    app = dash.Dash(__name__, server=tc_app, routes_pathname_prefix='/dash/')
    xyz = '{z}/{x}/{y}'
    main_map = _make_map(
        f'/singleband/{data[0]["title"]}/{data[0]["year"]}/{xyz}.png',
        format_bounds(data[0]['bounds']))
    app.layout = html.Div(main_map)

    return app
