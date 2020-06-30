"""The Dash-based front-end"""
import dash
import dash_html_components as html


def get_app(server):
    """Combine existing flash app with Dash app.

    Args:
        server: Flash instance to embed.
    """
    app = dash.Dash(__name__, server=server, routes_pathname_prefix='/dash/')
    app.layout = html.Div("My Dash app")
    return app
