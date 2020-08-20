"""Taswira's CLI"""
import argparse
import os
import signal
import sys
import tempfile
import threading
import warnings
import webbrowser

import terracotta as tc
from terracotta.server.app import app as tc_app
from werkzeug.serving import run_simple

from ..app import get_app
from . import arg_types, update_config
from .helpers import get_free_port
from .ingestion import UnoptimizedRaster, ingest


def start_servers(dbpath, port):
    """Load given DB and start a Terracotta and Dash server.

    Args:
        dbpath: Path to a Terracota-generated DB.
        port: Port number for Terracotta server.
    """
    def handler(signum, frame):  # pylint: disable=unused-argument
        sys.exit(0)

    signal.signal(signal.SIGINT, handler)

    tc.update_settings(DRIVER_PATH=dbpath, DRIVER_PROVIDER='sqlite')
    app = get_app()
    app.init_app(tc_app)

    def open_browser():
        webbrowser.open(f'http://localhost:{port}')

    threading.Timer(2, open_browser).start()

    if 'DEBUG' in os.environ:
        app.run_server(port=port, threaded=False, debug=True)
    else:
        print('Starting Taswira...')
        run_simple('localhost', port, app.server)


def console():
    """The command-line interface for Taswira"""
    parser = argparse.ArgumentParser(
        description="Interactive visualization tool for GCBM")
    parser.add_argument(
        "config",
        type=arg_types.indicator_file,
        help="path to JSON config file",
    )
    parser.add_argument("spatial_results",
                        type=arg_types.spatial_results,
                        help="path to GCBM spatial output directory")
    parser.add_argument("db_results",
                        type=arg_types.db_results,
                        help="path to compiled GCBM results database")
    parser.add_argument("--allow-unoptimized",
                        action="store_true",
                        help="allow processing unoptimized raster files")
    args = parser.parse_args()

    update_config(args.config)

    with tempfile.TemporaryDirectory() as tmpdirname:
        try:
            if args.allow_unoptimized:
                warnings.simplefilter('ignore')  # Supress Terracotta warnings

            dbpath = ingest(args.spatial_results, args.db_results, tmpdirname,
                            args.allow_unoptimized)
            port = get_free_port()
            start_servers(dbpath, port)
        except UnoptimizedRaster:
            sys.exit("""\
Found a raster file that is not a valid cloud-optimized GeoTIFFs. This tool
wasn't designed to work with such files. You can try continuing anyway by
passing the `--allow-unoptimized` flag but it's not recommended.

For best experience, regenerate the raster files after configuring GCBM to use
the following GDAL parameters:

BIGTIFF=YES, TILED=YES, COMPRESS=ZSTD, ZSTD_LEVEL=1
""")
        except KeyboardInterrupt:
            sys.exit("Raster loading was interrupted")
