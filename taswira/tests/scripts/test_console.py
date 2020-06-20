import urllib.request


def test_terracotta_integration(terracotta_server):
    """Check Terracotta integration by making requests to its REST API."""

    test_endpoints = ('apidoc', "keys")

    for endpoint in test_endpoints:
        with urllib.request.urlopen(f"{terracotta_server}/{endpoint}") as response:
            assert response.getcode() == 200
