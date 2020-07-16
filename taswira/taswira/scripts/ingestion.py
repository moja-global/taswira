"""Ingest data into a Terracotta DB."""
import glob
import os
import re

import terracotta as tc

from . import get_config
from .metadata import get_metadata

DB_NAME = 'terracotta.sqlite'
GCBM_RASTER_NAME_PATTERN = r'.*_(?P<year>\d{4}).tiff'
GCBM_RASTER_KEYS = ('title', 'year')
GCBM_RASTER_KEYS_DESCRIPTION = {
    'title': 'Name of indicator',
    'year': 'Year of raster data',
}


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

    with driver.connect():
        for config in get_config():
            raster_files = glob.glob(rasterdir + os.sep +
                                     config['file_pattern'])
            indicator = config['database_indicator']
            title = config.get('title', indicator)
            for raster_path in raster_files:
                raster_filename = os.path.basename(raster_path)

                match = re.match(GCBM_RASTER_NAME_PATTERN, raster_filename)
                if match is None:
                    raise ValueError(
                        f'Input file {raster_filename} does not match raster pattern'
                    )

                year = match.group('year')
                keys = (title, year)
                computed_metadata = driver.compute_metadata(
                    raster_path,
                    extra_metadata={
                        'value': str(metadata[title][year]),
                        'colormap': config.get('palette').lower()
                    })
                driver.insert(keys, raster_path, metadata=computed_metadata)

    return driver.path
