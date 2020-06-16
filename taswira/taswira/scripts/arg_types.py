import argparse
import json
import os


def validate_path(path):
    if not os.path.exists(path):
        raise argparse.ArgumentTypeError(f"{path} not found.")


def indicator_file(path):
    validate_path(path)
    with open(path) as f:
        return json.load(f)


def spatial_results(path):
    validate_path(path)
    return os.path.abspath(path)
