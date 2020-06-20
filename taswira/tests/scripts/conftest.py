import time
from multiprocessing import Process

import numpy as np
import pytest
import rasterio

from taswira.scripts.helpers import get_free_port

GCBM_TEST_FILES = [
    {
        'dtype': 'float32',
        'name': 'AG_Biomass_C_2010.tiff',
        'title': 'AG_Biomass_C',
        'year': '2010'
    },
    {
        'dtype': 'int16',
        'name': 'NPP_2013.tiff',
        'title': 'NPP',
        'year': '2013'
    }
]


TEST_CONFIG = [
    {
        "title": "AG Biomass",
        "database_indicator": "Aboveground Biomass",
        "file_pattern": "AG_Biomass_C_*.tiff",
        "palette": "YlGnBu",
        "graph_units": "Mtc",
    },
    {
        "title": "NPP",
        "database_indicator": "NPP",
        "file_pattern": "NPP*.tiff",
        "palette": "Greens",
        "graph_units": "Ktc",
    }
]


@pytest.fixture(scope='session')
def GCBM_raster_files(tmpdir_factory):
    outpath = tmpdir_factory.mktemp('raster')

    def _make_GCBM_raster(dtype, name):
        """Generate a GCBM-like GeoTIFF raster."""
        raster_data = np.arange(-200 * 400, 200 * 400,
                                dtype=dtype).reshape(400, 400)

        raster_data.flat[::5] = 10000  # Add some nodata points

        # These properties were taken from FLINT and GCBM.
        profile = {
            'driver': 'GTiff',
            'dtype': dtype,
            'nodata': 10000,
            'width': raster_data.shape[1],
            'height': raster_data.shape[0],
            'count': 1,
            'crs': {'init': 'epsg:4326'},
            'transform': rasterio.transform.from_origin(-119.3,  50.0, 0.01, -0.01),
            'tiled': True,
            'compress': 'ZSTD',
            'bigtiff': 'YES',
            'zstd_level': 1
        }

        raster_path = outpath.join('{}'.format(name))
        with rasterio.open(str(raster_path), 'w', **profile) as dst:
            dst.write(raster_data, 1)

        return raster_path

    return [_make_GCBM_raster(file['dtype'], file['name']) for file in GCBM_TEST_FILES]


@pytest.fixture(scope='session')
def testdb(GCBM_raster_files, tmpdir_factory):
    """A pre-populated Terracotta raster database. (TODO: Add metadata)"""
    from terracotta import get_driver

    keys = ['title', 'year']
    dbpath = tmpdir_factory.mktemp('db').join('db-readonly.sqlite')
    driver = get_driver(dbpath, provider='sqlite')
    driver.create(keys)

    with driver.connect():
        for raster in GCBM_raster_files:
            driver.insert(('val11', 'x'), str(raster))

    return dbpath


@pytest.fixture(scope='module')
def terracotta_server(testdb):
    """Starts a Terracotta server with a test DB."""
    from taswira.scripts.console import start_terracotta
    port = get_free_port()
    proc = Process(target=start_terracotta, args=(str(testdb), port))
    proc.start()
    try:
        time.sleep(5)
        assert proc.is_alive()
        yield f'http://localhost:{port}'
    finally:
        proc.terminate()
        proc.join(5)
        assert not proc.is_alive()
