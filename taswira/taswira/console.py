import argparse
import tempfile

import terracotta as tc
from terracotta.server.app import app


def start_terracotta(dbpath, port):
    """Load given DB and start a Terracotta server.
    
    Arguments:
        
        dbpath: Path to a Terracota-generated DB.
        port: Port number for Terracotta server.
    """
    tc.update_settings(DRIVER_PATH=dbpath, DRIVER_PROVIDER='sqlite')
    app.run(port=port, threaded=False)

    app.run(port=5000, threaded=False)
