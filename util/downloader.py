import requests
from pathlib import Path


def download_by_requests(url: str, out: Path):
    response = requests.get(url, stream=True)
    if response.status_code == 200:
        block_size = 1024
        with open(out, 'wb') as file:
            for data in response.iter_content(block_size):
                file.write(data)
