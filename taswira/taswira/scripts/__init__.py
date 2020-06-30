"""Top-level module of CLI."""
_CONFIG = []


def update_config(config):
    """Set new config.

    Args:
        config: dict of new config
    """
    global _CONFIG  # pylint: disable=global-statement
    _CONFIG = config


def get_config():
    """Return the config.

    Returns:
        A dict of config.
    """
    return _CONFIG
