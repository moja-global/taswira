"""CLI argument types.

These functions are used with `argparse` to validate command-line
arguments.
"""
import argparse
import json
import os

INDICATOR_REQUIRED_KEYS = ("database_indicator", "file_pattern")


def validate_path(path):
    """Validates if a path exists.

    Args:
        path: String passed with command.

    Raises:
        ArgumentTypeError: If the path doesn't exist.
    """
    if not os.path.exists(path):
        raise argparse.ArgumentTypeError(f"{path} not found.")


def indicator_file(path):
    """Validates a JSON formatted indicator config file.

    Args:
        path: String passed with command.

    Raises:
        ArgumentTypeError: If a required key is missing in the file.
    """
    validate_path(path)
    with open(path) as file:
        config = json.load(file)
        for i, indicator in enumerate(config):
            for key in INDICATOR_REQUIRED_KEYS:
                if not key in indicator:
                    raise argparse.ArgumentTypeError(
                        f"Required key `{key}` missing in config element {i}.")

        return config


def spatial_results(path):
    """Validates and converts spatial results path.

    Args:
        path: String passed with command.

    Returns:
        Absolute path to the spatial results.
    """
    validate_path(path)
    return os.path.abspath(path)


def db_results(path):
    """Validates and converts DB results path.

    Args:
        path: String passed with command.

    Returns:
        Absolute path to the spatial results.
    """
    validate_path(path)
    return os.path.abspath(path)
