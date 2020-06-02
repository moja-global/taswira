import pytest
import urllib.request
from multiprocessing import Process
import time


@pytest.fixture(scope='module')
def terracotta_server():
    """Starts a Terracotta server with no data (TODO: Create a test db and load it)"""
    from taswira.console import start_terracotta

    proc = Process(target=start_terracotta)
    proc.start()
    try:
        time.sleep(5)
        assert proc.is_alive()
        yield "http://localhost:5000"
    finally:
        proc.terminate()
        proc.join(5)
        assert not proc.is_alive()


class TestTerracotta:
    def test_api_docs(self, terracotta_server):
        """Check if API docs are accessible or not"""

        test_url = f"{terracotta_server}/apidoc"

        with urllib.request.urlopen(test_url) as response:
            assert response.getcode() == 200
