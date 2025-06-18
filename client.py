import json
import os
import time
import psutil
import socket
import requests
import platform

CONFIG_FILE = 'client_config.json'


def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE) as f:
            return json.load(f)
    config = {}
    config['host'] = input('Enter host IP: ')
    config['port'] = input('Enter host port [8888]: ') or '8888'
    config['name'] = input('Enter a name for this device: ')
    config['info'] = input('Additional info [Below the image]: ')
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f)
    return config


def count_cpu_sockets():
    """
    Parse /proc/cpuinfo to count unique physical CPU sockets (Linux).
    """
    sockets = set()
    try:
        with open('/proc/cpuinfo') as f:
            for line in f:
                if line.startswith('physical id'):
                    _, val = line.split(':')
                    sockets.add(val.strip())
    except Exception:
        return 1
    return max(len(sockets), 1)


def get_local_ip():
    """
    Determine the primary local IP address by opening a UDP socket.
    """
    ip = '127.0.0.1'
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    except Exception:
        pass
    finally:
        try:
            s.close()
        except:
            pass
    return ip


def collect_metrics():
    temps = psutil.sensors_temperatures() if hasattr(psutil, 'sensors_temperatures') else {}
    metrics = {}

    # OS version
    metrics['OS Version'] = platform.platform()

    # Local IP
    metrics['Local IP'] = get_local_ip()

    # CPU sockets: temp & util per socket
    cpu_temps = temps.get('coretemp') or temps.get('cpu_thermal') or []
    num_sockets = count_cpu_sockets()
    cpu_utils = psutil.cpu_percent(percpu=True)
    for idx in range(num_sockets):
        if idx < len(cpu_temps):
            metrics[f'CPU {idx+1} temp'] = f"{cpu_temps[idx].current} °C"
        util = cpu_utils[idx] if idx < len(cpu_utils) else 0
        metrics[f'CPU {idx+1} util'] = f"{util} %"

    # RAM usage
    mem = psutil.virtual_memory()
    metrics['RAM'] = f"{mem.used // (1024**2)}MB / {mem.total // (1024**2)}MB"

    # Single disk space used
    disk = psutil.disk_usage('/')
    used_gb = disk.used // (1024**3)
    total_gb = disk.total // (1024**3)
    metrics['Disk space used'] = f"{used_gb}GB / {total_gb}GB"

    # GPU temperatures per GPU if available
    gpu_sensors = (
        temps.get('gpu')
        or temps.get('amdgpu')
        or temps.get('nvidia')
        or temps.get('nouveau')
        or []
    )
    for i, entry in enumerate(gpu_sensors, start=1):
        metrics[f'GPU {i} temp'] = f"{entry.current} °C"

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
        time.sleep(15)


if __name__ == '__main__':
    main()
