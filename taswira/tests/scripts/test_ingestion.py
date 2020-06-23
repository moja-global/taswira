import os.path

from tests.scripts.conftest import GCBM_TEST_FILES


def test_ingest(set_config, GCBM_raster_files, GCBM_compiled_output, tmpdir):
    from taswira.scripts.ingestion import ingest
    from terracotta import get_driver

    set_config()

    rasterdir = GCBM_raster_files[0].dirname
    dbpath = ingest(rasterdir, GCBM_compiled_output, tmpdir)

    assert os.path.exists(dbpath)

    driver = get_driver(dbpath, provider='sqlite')
    assert driver.key_names == ('title', 'year')

    datasets = driver.get_datasets()
    for i, f in enumerate(GCBM_TEST_FILES):
        assert datasets[(f['title'], f['year'])] == str(GCBM_raster_files[i])
