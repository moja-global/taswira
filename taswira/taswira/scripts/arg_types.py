import argparse
import json
import os

INDICATOR_REQUIRED_KEYS = ("database_indicator", "file_pattern")


def validate_path(path):
    if not os.path.exists(path):
        raise argparse.ArgumentTypeError(f"{path} not found.")


def indicator_file(path):
    validate_path(path)
    with open(path) as f:
        config = json.load(f)
        for i, c in enumerate(config):
            for k in INDICATOR_REQUIRED_KEYS:
                if not k in c:
                    raise argparse.ArgumentTypeError(
                        f"Required key `{k}` missing in config element {i}.")

        return config


def spatial_results(path):
    validate_path(path)
    return os.path.abspath(path)


def db_results(path):
    validate_path(path)
    return os.path.abspath(path)
