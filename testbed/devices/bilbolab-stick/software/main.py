import os
import sys
import threading
import time

top_level_module = os.path.expanduser("~/software")
if top_level_module not in sys.path:
    sys.path.insert(0, top_level_module)

import utils.network as network
from lib_display.displays import BigDisplay, SmallDisplayRobots
from utils.delayed_executor import delayed_execution
from utils.time import Timer




class MainProgram:
    display_large: BigDisplay
    display_left: SmallDisplayRobots
    display_right: SmallDisplayRobots

    _exit: bool

    def __init__(self):
        self.display_large = BigDisplay()
        self.display_left = SmallDisplayRobots(1, 'LOCAL')
        self.display_right = SmallDisplayRobots(2, 'LOCAL')

        self.display_thread = threading.Thread(target=self.display_task, daemon=True)
        self.network_thread = threading.Thread(target=self.network_task, daemon=True)
        self._exit = False

        self.timer_network_check = Timer(1000)
        self.timer_display_update = Timer(1000)
        self.timer_network_scan = Timer(1000)

        self.display_mutex = threading.Lock()

        self.local_devices = {}
        self.bridge_devices = {}

    # ------------------------------------------------------------------------------------------------------------------
    def init(self):
        self.display_large.init()
        self.display_left.init()
        self.display_right.init()

    # ------------------------------------------------------------------------------------------------------------------
    def start(self):
        self.display_large.start()
        self.display_left.start()
        self.display_right.start()

        self.display_thread.start()
        self.network_thread.start()

    # ------------------------------------------------------------------------------------------------------------------
    def updateDisplays(self):
        self.display_large.updateTime()
        self.display_large.update()
        self.display_left.update()
        self.display_right.update()

    # ------------------------------------------------------------------------------------------------------------------
    def check_network(self):

        # Check if the AP is running
        ap_is_running = network.is_interface_up('wlan0_ap')
        if ap_is_running:
            ap_ssid = network.get_ap_ssid('wlan0_ap')
            with self.display_mutex:
                self.display_large.setSSID(ap_ssid, 'LIGHTGREEN')
                self.display_large.setPassword('bilbobeutlin', 'LIGHTGREEN')
            ap_ip = network.get_ip_address_from_interface('wlan0_ap')
            with self.display_mutex:
                self.display_large.setIP(ap_ip, 'LIGHTGREEN')
        else:
            ap_ssid = None
            with self.display_mutex:
                self.display_large.setSSID('---', 'RED')
                self.display_large.setPassword('')
                self.display_large.setIP('')

        has_internet = network.check_internet(0.5)

        wlan0_is_running = network.is_interface_up('wlan0')
        if wlan0_is_running:
            wlan0_ssid = network.get_connected_ssid('wlan0')
            if wlan0_ssid is not None:
                if has_internet:
                    with self.display_mutex:
                        self.display_large.setBridge(wlan0_ssid, 'LIGHTGREEN')
                else:
                    with self.display_mutex:
                        self.display_large.setBridge(wlan0_ssid, 'RED')
            else:
                with self.display_mutex:
                    self.display_large.setBridge('---', 'RED')
        else:
            with self.display_mutex:
                self.display_large.setBridge('---', 'RED')

        with self.display_mutex:
            self.display_large.setInternet(has_internet)

    # ------------------------------------------------------------------------------------------------------------------
    def scan_network(self):
        # Maximum number of consecutive scans a device can be missing before removal
        MAX_MISSING_SCANS = 3

        # Scan the own WiFi AP
        wlan0_ap_is_running = network.is_interface_up('wlan0_ap')
        if wlan0_ap_is_running:
            wlan0_ip = network.get_ip_address_from_interface('wlan0_ap')
            subnet_filter = network.get_subnet_filter(wlan0_ip)
            excluded_ips = [wlan0_ip]
            devices = network.scan_network(ip_range='192.168.4.2-20')
            devices = network.filter_devices(devices, subnet_filter, excluded_ips)
            if devices is not None:
                # Convert the discovered devices into a set of IPs
                discovered_ips = set(device['ip'] for device in devices)

                # Add new devices to self.devices and call placeholder1
                for device in devices:
                    if device['ip'] not in self.local_devices:
                        self.local_devices[device['ip']] = {
                            'ip': device['ip'],
                            'hostname': device.get('hostname', 'unknown'),
                            'missing_scans': 0  # Initialize missing scans counter
                        }
                        with self.display_mutex:
                            self.display_left.addDevice(self.local_devices[device['ip']])
                    else:
                        # Reset the missing scans counter if the device is found
                        self.local_devices[device['ip']]['missing_scans'] = 0

                # Identify devices in self.devices that are no longer discovered
                existing_ips = set(self.local_devices.keys())
                missing_ips = existing_ips - discovered_ips

                # Increment the missing scans counter for missing devices
                for ip in missing_ips:
                    self.local_devices[ip]['missing_scans'] += 1

                # Remove devices that have exceeded the MAX_MISSING_SCANS threshold
                for ip in list(self.local_devices.keys()):  # Create a list to avoid modifying the dictionary during iteration
                    if self.local_devices[ip]['missing_scans'] > MAX_MISSING_SCANS:
                        removed_device = self.local_devices.pop(ip)
                        with self.display_mutex:
                            self.display_left.removeDevice(ip)

    def network_task(self):
        while not self._exit:
            if self.timer_network_check > 2.0:
                self.timer_network_check.reset()
                self.check_network()

            if self.timer_network_scan > 5.0:
                self.timer_network_scan.reset()
                self.scan_network()


            time.sleep(0.25)

    def display_task(self):
        while not self._exit:

            if self.timer_display_update > 0.5:
                self.timer_display_update.reset()
                # Update the displays
                with self.display_mutex:
                    self.updateDisplays()

            time.sleep(0.01)

def main():
    mp = MainProgram()
    mp.init()
    mp.start()


    while True:
        time.sleep(1)

if __name__ == '__main__':
    main()