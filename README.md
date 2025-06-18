![download.png](https://raw.githubusercontent.com/Fischherboot/Aculi/main/watermark-no-bg.png)

# Aculi Observe

Aculi Observe is a lightweight system monitoring tool for your homelab. It consists of two components:

- **Host**: Displays real-time system information from connected clients via a web interface.
- **Client**: Runs on each monitored machine and periodically sends system stats to the Host.

---

## Prerequisites

- Python 3.7 or higher
- `pip`

---

## Host Setup

1. **Clone or copy** this repository to your Host machine (e.g., a server or Raspberry Pi).
2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
3. **Start the Host server**:
   ```bash
   python host.py
   ```
4. **Note** the IP address and port printed by `host.py` (default port can be changed in the script).
5. **Open** your browser and navigate to:
   ```
   http://<HOST_IP>:<PORT>/
   ```

---

## Client Setup

> Make sure the Host is already running and accessible from the network.

1. **Copy** the project directory to the client machine you want to monitor.

2. **Install dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

3. **Run the client**:

   ```bash
   python client.py
   ```

   - When prompted, **enter the Host IP**.

   - Press Enter, then **enter the Host port** (default: `8888`).

   - Provide an **additional identifier** for this client.

   - Optionally, you can add extra information of the client. (Can be skipped)

4. To **stop** the client at any time, press `Ctrl+C`.

5. **Install as a system service** (optional):

   ```bash
   chmod +x client_setup.sh
   ./client_setup.sh
   ```

   This script will:

   - Copy `client.py` and the configuration file (client_config.json).
   - Create a systemd service that keeps the client running and updates it automatically.

---

## License

This project is licensed under the Apache License, Version 2.0. 
