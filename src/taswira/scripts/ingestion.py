"""Ingest data into a Terracotta DB."""
import glob
import os
import re

import tqdm
from terracotta import get_driver
from terracotta.cog import validate as is_valid_cog

from ..units import find_units
from . import get_config
from .metadata import get_metadata

DB_NAME = 'terracotta.sqlite'
GCBM_RASTER_NAME_PATTERN = r'.*_(?P<year>\d{4}).tif{1,2}'
GCBM_RASTER_KEYS = ('title', 'year')
GCBM_RASTER_KEYS_DESCRIPTION = {
    'title': 'Name of indicator',
    'year': 'Year of raster data',
}


def _find_raster_year(raster_path):
    raster_filename = os.path.basename(raster_path)
    match = re.match(GCBM_RASTER_NAME_PATTERN, raster_filename)
    if match is None:
        raise ValueError(
            f'Input file {raster_filename} does not match raster pattern')

    return match.group('year')


class UnoptimizedRaster(Exception):
    """Raised when an unoptimized raster file is encountered."""


def ingest(rasterdir, db_results, outputdir, allow_unoptimized=False):
    """Ingest raster files into a Terracotta database.

    Args:
        rasterdir: Path to directory containing raster files.
        db_results: Path to DB containing non-spatial data.
        outputdir: Path to directory for saving the generated DB.
        allow_unoptimized: Should unoptimized raster files be processed?

    Returns:
        Path to generated DB.
    """
    driver = get_driver(os.path.join(outputdir, DB_NAME), provider='sqlite')
    driver.create(GCBM_RASTER_KEYS, GCBM_RASTER_KEYS_DESCRIPTION)

    progress = tqdm.tqdm(get_config(), desc='Searching raster files')
    raster_files = []
    for config in progress:
        for file in glob.glob(rasterdir + os.sep + config['file_pattern']):
            if not is_valid_cog(file) and not allow_unoptimized:
                raise UnoptimizedRaster
            raster_files.append(dict(path=file, **config))

    with driver.connect():
        metadata = get_metadata(db_results)
        progress = tqdm.tqdm(raster_files, desc='Processing raster files')
        for raster in progress:
            title = raster.get('title', raster['database_indicator'])
            year = _find_raster_year(raster['path'])
            unit = find_units(raster.get('graph_units'))
            computed_metadata = driver.compute_metadata(
                raster['path'],
                extra_metadata={
                    'indicator_value': str(metadata[title][year]),
                    'colormap': raster.get('palette').lower(),
                    'unit': unit.value[2]
                })
            driver.insert((title, year),
                          raster['path'],
                          metadata=computed_metadata)

    return driver.path
