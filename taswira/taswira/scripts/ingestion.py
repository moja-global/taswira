"""Ingest data into a Terracotta DB."""
import glob
import os
import re

import terracotta as tc

from . import get_config
from .metadata import get_metadata

DB_NAME = 'terracotta.sqlite'
GCBM_RASTER_NAME_PATTERN = r'(?P<title>\w+)_(?P<year>\d{4}).tiff'
GCBM_RASTER_KEYS = ('title', 'year')
GCBM_RASTER_KEYS_DESCRIPTION = {
    'title': 'Title of raster.',
    'year': 'Year of raster.',
}


def _get_raster_db_rows(raster_files, indicator, indicator_metadata):
    """Generate rows for a Terracotta raster DB.

    Args:
        raster_files: List of raster file paths.
        indicator: Name of indicator.
        indicator_metadata: Dict of year-wise values of `indicator`.

    Returns:
        List of tuples (keys, filepath, metadata) that can be unpacked and
        then passed to `driver.insert()`.
    """
    rows = []

    for raster_path in raster_files:
        raster_filename = os.path.basename(raster_path)

        match = re.match(GCBM_RASTER_NAME_PATTERN, raster_filename)
        if match is None:
            raise ValueError(
                f'Input file {raster_filename} does not match raster pattern')

        keys = _, year = match.groups()
        metadata = {indicator: str(indicator_metadata[year])}
        rows.append({
            'keys': keys,
            'filepath': raster_path,
            'metadata': metadata
        })

    return rows


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
            for raster_path in raster_files:
                raster_filename = os.path.basename(raster_path)

                match = re.match(GCBM_RASTER_NAME_PATTERN, raster_filename)
                if match is None:
                    raise ValueError(
                        f'Input file {raster_filename} does not match raster pattern'
                    )

                keys = _, year = match.groups()
                computed_metadata = driver.compute_metadata(
                    raster_path,
                    extra_metadata={indicator: str(metadata[indicator][year])})
                driver.insert(keys, raster_path, metadata=computed_metadata)

    return driver.path
