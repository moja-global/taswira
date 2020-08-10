"""Ingest data into a Terracotta DB."""
import glob
import os
import re

import terracotta as tc
import tqdm

from ..units import find_units
from . import get_config
from .metadata import get_metadata

DB_NAME = 'terracotta.sqlite'
GCBM_RASTER_NAME_PATTERN = r'.*_(?P<year>\d{4}).tiff'
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


def ingest(rasterdir, db_results, outputdir):
    """Ingest raster files into a Terracotta database.

    Args:
        rasterdir: Path to directory containing raster files.
        db_results: Path to DB containing non-spatial data.
        outputdir: Path to directory for saving the generated DB.

    Returns:
        Path to generated DB.
    """
    driver = tc.get_driver(os.path.join(outputdir, DB_NAME), provider='sqlite')
    driver.create(GCBM_RASTER_KEYS, GCBM_RASTER_KEYS_DESCRIPTION)

    metadata = get_metadata(db_results)

    progress = tqdm.tqdm(get_config(), desc='Searching raster files')
    raster_files = []
    for config in progress:
        raster_files += [
            (f, config)
            for f in glob.glob(rasterdir + os.sep + config['file_pattern'])
        ]

    with driver.connect():
        progress = tqdm.tqdm(raster_files, desc='Processing raster files')
        for raster_path, config in progress:
            title = config.get('title', config['database_indicator'])
            year = _find_raster_year(raster_path)
            unit = find_units(config.get('graph_units'))
            computed_metadata = driver.compute_metadata(
                raster_path,
                extra_metadata={
                    'colormap': config.get('palette').lower(),
                    'indicator_value': str(metadata[title][year]),
                    'unit': unit.value[2]
                })
            keys = (title, year)
            driver.insert(keys, raster_path, metadata=computed_metadata)

    return driver.path
