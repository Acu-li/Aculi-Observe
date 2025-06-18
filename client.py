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
    cpu_temps = temps.get('coretemp') or temps.get('cpu_thermal') or []
    cpu_utils = psutil.cpu_percent(percpu=True)
    for idx in range(2):
        if idx < len(cpu_temps):
            metrics[f'CPU {idx + 1}'] = f"{cpu_temps[idx].current} °C"
        else:
            metrics[f'CPU {idx + 1}'] = 'Not applicable'
        util = cpu_utils[idx] if idx < len(cpu_utils) else 0
        metrics[f'CPU {idx + 1} util'] = f"{util} %"
    mem = psutil.virtual_memory()
    metrics['RAM'] = f"{mem.used // (1024**2)}MB / {mem.total // (1024**2)}MB"
    metrics['Disk util'] = f"{psutil.disk_usage('/').percent} %"
    gpu_temps = (temps.get('gpu') or temps.get('amdgpu') or temps.get('nvidia') or
                 temps.get('nouveau') or [])
    if gpu_temps:
        for i, entry in enumerate(gpu_temps[:10], start=1):
            metrics[f'GPU {i}'] = f"{entry.current} °C"
    else:
        metrics['GPU'] = 'Not applicable'
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
