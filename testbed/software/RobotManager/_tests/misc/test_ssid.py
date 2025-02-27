import socket
import psutil
import subprocess
import platform

def get_interface_for_ip(ip_address):
    """Find the network interface associated with the given IP address."""
    for interface, addrs in psutil.net_if_addrs().items():
        for addr in addrs:
            if addr.family == socket.AF_INET and addr.address == ip_address:
                return interface
    return None

def get_wifi_ssid_by_interface(interface):
    """Get the Wi-Fi SSID for a specific network interface."""
    try:
        system = platform.system()
        if system == "Windows":
            # Use netsh to get SSID for Windows
            output = subprocess.check_output(["netsh", "wlan", "show", "interfaces"], encoding="utf-8")
            ssid = None
            found_interface = False
            for line in output.splitlines():
                if "Name" in line and interface in line:
                    found_interface = True
                if found_interface and "SSID" in line:
                    ssid = line.split(":", 1)[1].strip()
                    break
            return ssid
        elif system == "Darwin":
            # Use networksetup for macOS
            try:
                output = subprocess.check_output(
                    ["networksetup", "-getairportnetwork", interface],
                    encoding="utf-8"
                )
                print(output)
                if "Current Wi-Fi Network" in output:
                    ssid = output.split(":")[1].strip()
                    return ssid
            except subprocess.CalledProcessError:
                return None
        elif system == "Linux":
            # Use iwconfig for Linux
            output = subprocess.check_output(["iwconfig", interface], encoding="utf-8", stderr=subprocess.DEVNULL)
            for line in output.splitlines():
                if "ESSID" in line:
                    ssid = line.split(":")[1].strip().strip('"')
                    return ssid
            return None
        else:
            return "Unsupported OS"
    except Exception as e:
        return f"Error retrieving SSID: {e}"


def find_network_name_for_ip(ip_address):
    """Find the SSID of the network associated with the given IP address."""
    interface = get_interface_for_ip(ip_address)
    print(interface)
    if interface:
        ssid = get_wifi_ssid_by_interface(interface)
        return ssid
    else:
        return "No interface found for this IP address."

def get_wifi_interface():
    """Identify the Wi-Fi interface on macOS."""
    try:
        output = subprocess.check_output(["networksetup", "-listallhardwareports"], encoding="utf-8")
        lines = output.splitlines()
        for i, line in enumerate(lines):
            if "Wi-Fi" in line:
                # Wi-Fi found, return the next line with Device:
                return lines[i + 1].split(":")[1].strip()
    except Exception as e:
        return f"Error identifying Wi-Fi interface: {e}"


print(get_wifi_interface())
