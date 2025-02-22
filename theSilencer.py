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
except ModuleNotFoundError:
    print("Try installing the dependencies")

console = Console()
back = False
wifi = False
bluetooth = False
sysinfo = False

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

def handleBluetooth():
    global bluetooth, back

    os.system("clear")

    btable = Table(title= "[bold red] Bluetooth Menu [/bold red]")
    btable.add_column("Nr.")
    btable.add_column("Option")

    btable.add_row("n/a", "LOL, come back later. Still under development")
    btable.add_row("0", "Back")

    while bluetooth and not back:
        printBluetoothLogo()
        console.print(btable)

        option = int(input(Fore.GREEN + "> " + Fore.RESET))

        if option != 0:
            print()
            print(Fore.RED + "Your fucking moron. Can't u read?? Come back later. Still under development !!!" + Fore.RESET)
        else:
            back = True
            bluetooth = False
            os.system("clear")
    
def handleWiFi():
    global wifi, back

    os.system("clear")
    
    wifi = True
    back = False

    wtable = Table(title= "[bold red] Wifi Menu [/bold red]")
    wtable.add_column("Nr.")
    wtable.add_column("Option")

    wtable.add_row("0", "Show available networks adapters")
    wtable.add_row("1", "Scan for clients")
    wtable.add_row("2", "Deauth client")
    wtable.add_row("3", "Deauth clients")
    wtable.add_row("4", "Jammer (will block the entire network)")
    wtable.add_row("5", "Back")

    while wifi and not back:
        printWIFILogo()
        console.print(wtable)

        option = int(input(Fore.GREEN + "> " + Fore.RESET))

        if option >= 0 and option <= 5:
            if option == 0:
                print("Show available networks adapters")
            if option == 1:
                print("Scan for clients")
            if option == 2:
                print("Deauth client")
            if option == 3:
                print("Deauth clients")
            if option == 4:
                print("Jammer (will block the entire network)")
            if option == 5:
                back = True
                wifi = False
                os.system("clear")
        else:
            print()
            print(Fore.RED + "Your fucking moron. Can't u read?? Choose a option between 0 and 4 !!" + Fore.RESET)

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
        print(Fore.YELLOW + "[+] Program closed bu user" + Fore.RESET)