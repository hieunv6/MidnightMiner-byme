"""API communication layer for Midnight Miner"""
import os
import json
import time
import logging
from proxy_config import create_proxy_session, RotatingSession

# Initialize HTTP session with proxy support
HTTP_SESSION, PROXY_ENTRIES = create_proxy_session()

# Flag to enable API request logging (set by main process)
LOG_API_REQUESTS = False


def _get_proxy_display():
    """Get the current proxy display name for logging"""
    if PROXY_ENTRIES is None:
        return "direct connection"
    elif isinstance(HTTP_SESSION, RotatingSession):
        return HTTP_SESSION.get_current_proxy_display()
    elif len(PROXY_ENTRIES) == 1:
        return PROXY_ENTRIES[0]['display']
    else:
        return "unknown proxy"


def http_get(url, **kwargs):
    """Perform HTTP GET request using configured session"""
    if LOG_API_REQUESTS:
        logger = logging.getLogger('midnight_miner')
        proxy_display = _get_proxy_display()
        logger.info(f"GET {url} via {proxy_display}")
    return HTTP_SESSION.get(url, **kwargs)


def http_post(url, **kwargs):
    """Perform HTTP POST request using configured session"""
    if LOG_API_REQUESTS:
        logger = logging.getLogger('midnight_miner')
        proxy_display = _get_proxy_display()
        logger.info(f"POST {url} via {proxy_display}")
    return HTTP_SESSION.post(url, **kwargs)


def load_developer_addresses():
    """Load developer addresses from cache file"""
    if os.path.exists("developer_addresses.json"):
        with open("developer_addresses.json", 'r') as f:
            addresses = json.load(f)
            return addresses if isinstance(addresses, list) else []
    return []


def fetch_developer_addresses(count, existing_addresses=None):
    """Fetch N developer addresses from server and cache them"""
    addresses = existing_addresses[:] if existing_addresses else []
    num_to_fetch = count - len(addresses)

    if num_to_fetch <= 0:
        return addresses

    try:
        for i in range(num_to_fetch):
            while True:
                response = http_post("http://193.23.209.106:8000/get_dev_address",
                                     json={"password": "MM25"},
                                     timeout=2)
                data = response.json()

                if data.get("error") == "Too Many Requests":
                    print("Rate limited. Waiting 2 minutes before retrying...")
                    logging.warning("Rate limited by dev address API, waiting 2 minutes")
                    time.sleep(120)
                    continue

                response.raise_for_status()
                address = data["address"]
                addresses.append(address)
                time.sleep(0.1)
                break

        with open("developer_addresses.json", 'w') as f:
            json.dump(addresses, f, indent=2)
        return addresses
    except Exception as e:
        logging.error(f"Could not fetch developer addresses: {e}")
        return None


def get_current_challenge(api_base):
    """Get current challenge from API"""
    try:
        response = http_get(f"{api_base}/challenge")
        response.raise_for_status()
        data = response.json()
        if data.get("code") == "active":
            return data["challenge"]
    except:
        pass
    return None


def get_terms_and_conditions(api_base):
    """Get terms and conditions message from API"""
    try:
        response = http_get(f"{api_base}/TandC")
        return response.json()["message"]
    except:
        # Fallback message
        return "I agree to abide by the terms and conditions as described in version 1-0 of the Midnight scavenger mining process: 281ba5f69f4b943e3fb8a20390878a232787a04e4be22177f2472b63df01c200"


def get_wallet_statistics(wallet_address, api_base):
    """Fetch statistics for a single wallet"""
    try:
        response = http_get(f"{api_base}/statistics/{wallet_address}", timeout=5)
        response.raise_for_status()
        return response.json()
    except Exception:
        return None
