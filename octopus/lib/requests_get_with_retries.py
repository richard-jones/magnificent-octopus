import requests
from time import sleep

def http_get_with_backoff_retries(url, max_retries=5, timeout=30):
    if not url:
        return
    attempt = 0
    r = None

    while attempt <= max_retries:
        try:
            r = requests.get(url, timeout=timeout)
            break
        except requests.exceptions.Timeout:
            attempt += 1
        sleep(2 ** attempt)

    return r