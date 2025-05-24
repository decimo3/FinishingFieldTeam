'''Provider module.

This module provides utilities for retrieving device and environment information,
including system specs and geolocation data.
'''

import platform
import psutil
import socket
import requests

def get_device_info():
    '''Retrieve device and geolocation information.

    Returns:
        dict: Dictionary containing system specs and geolocation data.
    '''
    info = {}

    # Sistema operacional
    info['system'] = platform.system()
    info['node_name'] = platform.node()
    info['release'] = platform.release()
    info['version'] = platform.version()
    info['machine'] = platform.machine()
    info['processor'] = platform.processor()

    # CPU
    info['cpu_count'] = psutil.cpu_count(logical=True)
    info['cpu_freq'] = psutil.cpu_freq()._asdict() if psutil.cpu_freq() else None

    # Memória
    virtual_mem = psutil.virtual_memory()
    info['memory_total'] = round(virtual_mem.total / (1024 ** 3), 2)  # Convert to GB
    info['memory_available'] = round(virtual_mem.available / (1024 ** 3), 2)  # Convert to GB

    # Rede
    try:
        info['hostname'] = socket.gethostname()
        info['local_ip'] = socket.gethostbyname(info['hostname'])
    except Exception:
        info['hostname'] = None
        info['local_ip'] = None

    # Geolocalização aproximada via IP público
    try:
        response = requests.get('https://ipinfo.io/json', timeout=5)
        if response.status_code == 200:
            geo_data = response.json()
            info['geolocation'] = {
                'ip': geo_data.get('ip'),
                'city': geo_data.get('city'),
                'region': geo_data.get('region'),
                'country': geo_data.get('country'),
                'loc': geo_data.get('loc'),
                'org': geo_data.get('org')
            }
        else:
            info['geolocation'] = None
    except Exception as e:
        info['geolocation'] = None

    return info

def main():
    '''Main entry point for provider module.'''
    print("Running provider...")
    device_info = get_device_info()
    for key, value in device_info.items():
        print(f"{key}: {value}")
