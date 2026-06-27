from urllib.request import urlopen


response = urlopen("http://127.0.0.1:8000/health/", timeout=3)
if response.status != 200:
    raise RuntimeError(f"Unexpected status: {response.status}")
