import socket


def get_free_port():
    """Returns a free port.

    https://stackoverflow.com/a/1365284
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(("", 0))
    sock.listen(1)
    port = sock.getsockname()[1]
    sock.close()
    return port
