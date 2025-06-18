import json
import os
import time
import psutil
import requests

CONFIG_FILE = 'client_config.json'


def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE) as f:
            return json.load(f)
    config = {}
    config['host'] = input('Enter host IP: ')
    config['port'] = input('Enter host port [5000]: ') or '5000'
    config['name'] = input('Enter a name for this device: ')
    config['info'] = input('Additional info: ')
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f)
    return config


def collect_metrics():
    temps = psutil.sensors_temperatures() if hasattr(psutil, 'sensors_temperatures') else {}
    metrics = {}
    cpu_temps = temps.get('coretemp') or []
    for i, entry in enumerate(cpu_temps[:2], start=1):
        metrics[f'CPU {i}'] = f"{entry.current} °C"
        metrics[f'CPU {i} util'] = f"{psutil.cpu_percent(percpu=True)[i-1]} %"
    mem = psutil.virtual_memory()
    metrics['RAM'] = f"{mem.used // (1024**2)}MB / {mem.total // (1024**2)}MB"
    metrics['Disk util'] = f"{psutil.disk_usage('/').percent} %"
    gpu_temps = temps.get('gpu') or temps.get('amdgpu') or []
    for i, entry in enumerate(gpu_temps[:10], start=1):
        metrics[f'GPU {i}'] = f"{entry.current} °C"
    return metrics


def main():
    config = load_config()
    host = f"http://{config['host']}:{config['port']}" 
    while True:
        metrics = collect_metrics()
        payload = {
            'name': config['name'],
            'info': config['info'],
            'metrics': metrics
        }
        try:
            requests.post(f"{host}/update", json=payload, timeout=5)
        except Exception:
            pass
        time.sleep(120)


if __name__ == '__main__':
    main()
