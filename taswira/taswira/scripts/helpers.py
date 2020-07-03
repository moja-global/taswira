"""Utilites"""
import socket


def get_free_port():
    """Returns a free port.

    https://stackoverflow.com/a/1365284
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        try:
            sock.bind(("", 5000))
        except OSError:
            sock.bind(("", 0))
            sock.listen(1)
        return sock.getsockname()[1]
