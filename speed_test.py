import requests
import time


def speed_test_download(proxy_port: int) -> float:
    proxies = get_proxies(proxy_port)

    # Test download speed through the SOCKS5 proxy
    url = "https://ash-speed.hetzner.com/100MB.bin"  # A file of known size for testing
    start_time = time.time()
    response = requests.get(url, proxies=proxies)
    end_time = time.time()

    # Check the size of the file
    file_size = len(response.content) / 1_000_000  # Size in MB
    download_time = end_time - start_time  # Time in seconds

    # Calculate download speed
    download_speed = file_size / download_time  # Speed in MB/s
    download_speed_mbps = download_speed * 8  # Convert to Mbps

    return download_speed_mbps


def speed_test_instagram(proxy_port: int) -> float:
    proxies = get_proxies(proxy_port)

    url = "https://www.instagram.com/cristiano/"
    start_time = time.time()
    requests.get(url, proxies=proxies)
    end_time = time.time()

    return end_time - start_time


def get_proxies(proxy_port: int):
    proxy_address = "127.0.0.1"
    proxy_url = f"socks5://{proxy_address}:{proxy_port}"

    return {
        'http': proxy_url,
        'https': proxy_url,
    }