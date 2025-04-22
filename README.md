# The-Silencer

======================================================================

This was developed and tested on a Raspberry Pi 4 running Raspbian OS.

======================================================================

🔥 Wireless Attack Toolkit (WiFi & Bluetooth)
============================================

Welcome to the **Wireless Attack Toolkit**, a terminal-based Python tool for **wireless network and Bluetooth reconnaissance and attacks**. This suite uses the `aircrack-ng` suite and `hciconfig` tools alongside Python automation to simplify WiFi and Bluetooth-based analysis and exploitation.

⚠️ **This tool is strictly for educational and ethical penetration testing on networks you own or have explicit permission to test.**

📦 Features
-----------

### 🛜 WiFi Attacks
- List available wireless adapters and their modes (monitor/managed)
- Scan nearby WiFi networks and extract:
  - SSID
  - BSSID (MAC address)
  - Channel
  - Signal strength
  - Security type
- Scan clients connected to a chosen access point
- Perform:
  - Targeted deauthentication on a single client
  - Deauthentication on multiple clients
  - Full network jamming (constant deauth flood)

### 📶 Bluetooth Attacks
- Scan and choose available Bluetooth adapters (`hci0`, `hci1`, etc.)
- List nearby Bluetooth devices
- Load scan history
- Simulated attacks (custom scripts can be defined)

### 💻 System Information
- Disk usage overview
- Network adapters and IP configurations
- Neofetch-style system summary

⚙️ Requirements
----------------

- Python 3.8+
- Root privileges (`sudo`)
- Aircrack-ng suite installed (`sudo apt install aircrack-ng`)
- Bluetooth utilities (`hciconfig`, `bluetoothctl`, etc.)
- Neofetch (`sudo apt install neofetch`)

### Python Libraries
Install dependencies using pip:

```bash
pip install -r req.txt
```

You'll also need two local modules:
- `wifi.py`: Contains the `WiFi` class with scanning and deauth methods
- `bluetooth.py`: Contains the `Bluetooth` class for scanning and simulated attack logic

🧠 Usage
--------

Run the tool with root permissions:

```bash
sudo python3 theSilencer.py
```

Then, follow the menus:
- `[0]` WiFi attacks
- `[1]` Bluetooth attacks
- `[2]` System info
- `[3]` Exit

🔐 Legal Disclaimer
-------------------

This tool is designed **only for authorized penetration testing**, learning, and ethical hacking purposes. Misusing it on unauthorized networks or devices may be illegal and is not supported by the author.

💡 TODO
--------
- Improve Bluetooth attack module with l2ping or rfcomm-based attacks
- Add logging of attack history
- Modular UI improvements (menu navigation, curses/tui?)
- Add packet sniffing support via `scapy`

