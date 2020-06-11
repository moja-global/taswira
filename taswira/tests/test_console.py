import time
import urllib.request
from multiprocessing import Process

import numpy as np
import pytest
import rasterio

from taswira.helpers import get_free_port

@pytest.fixture(scope='session')
def make_GCBM_raster(tmpdir_factory):
    def _make_GCBM_raster(dtype, name):
        """
        Generate a GeoTIFF rasters.

        These properties are taken from GCBM/FLINT.
        """
        raster_data = np.arange(-200 * 400, 200 * 400,
                                dtype=dtype).reshape(400, 400)

        raster_data.flat[::5] = 10000  # Add some nodata points

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
            'bigtiff': True,
            'zstd_level': 1
        }

        outpath = tmpdir_factory.mktemp('raster')
        raster_path = outpath.join('{}.tif'.format(name))
        with rasterio.open(str(raster_path), 'w', **profile) as dst:
            dst.write(raster_data, 1)

        return raster_path

    return _make_GCBM_raster


@pytest.fixture(scope='session')
def testdb(make_GCBM_raster, tmpdir_factory):
    """A pre-populated Terracotta raster database. (TODO: Add metadata)"""
    from terracotta import get_driver

    keys = ['title', 'year']
    dbpath = tmpdir_factory.mktemp('db').join('db-readonly.sqlite')
    driver = get_driver(dbpath, provider='sqlite')
    driver.create(keys)

    with driver.connect():
        for dtype, name in [('float32', 'AGBiomassC_2010'), ('int16', 'Age_2013')]:
            driver.insert(('val11', 'x'), str(make_GCBM_raster(dtype, name)))

    return dbpath


@pytest.fixture(scope='module')
def terracotta_server(testdb):
    """Starts a Terracotta server with a test DB."""
    from taswira.console import start_terracotta
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


def test_terracotta_integration(terracotta_server):
    """Check Terracotta integration by making requests to its REST API."""

    test_endpoints = ('apidoc', "keys")

    for endpoint in test_endpoints:
        with urllib.request.urlopen(f"{terracotta_server}/{endpoint}") as response:
            assert response.getcode() == 200