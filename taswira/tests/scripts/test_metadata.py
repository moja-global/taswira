def test_metadata(set_config, GCBM_compiled_output):
    from taswira.scripts.metadata import get_metadata

    set_config()

    metadata = get_metadata(GCBM_compiled_output)

    assert not len(metadata) == 0
    for _, indicator_values in metadata.items():
        assert not len(indicator_values) == 0
