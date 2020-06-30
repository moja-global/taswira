"""Utilites"""
import socket
from contextlib import closing


def get_free_port():
    """Returns a free port.

    https://stackoverflow.com/a/1365284
    """
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as sock:
        sock.bind(("", 0))
        sock.listen(1)
        return sock.getsockname()[1]
