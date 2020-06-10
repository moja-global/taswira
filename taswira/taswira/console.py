import argparse
import tempfile

import terracotta as tc
from terracotta.server.app import app


def start_terracotta(dbpath):
    tc.update_settings(DRIVER_PATH=dbpath, DRIVER_PROVIDER='sqlite')
    app.run(port=5000, threaded=False)
