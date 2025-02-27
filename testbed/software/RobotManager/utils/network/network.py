import concurrent.futures
import subprocess
import re
import threading
import time
import json
from elevate import elevate
import socket
import os
import sys
import time
from utils.logging_utils import Logger
import platform
import subprocess
import re

logger = Logger('network')


def getInterfaceIP(interface_name):
    """
    Retrieves the IP address of a specified interface.
    Args:
    - interface_name (str): The name of the interface.
    Returns:
    - str or None: The IP address of the interface, or None if not found.
    """
    os_name = platform.system()

    try:
        if os_name == "Windows":
            result = subprocess.run(
                ["ipconfig"],
                capture_output=True,
                text=True,
                check=True
            )
            output = result.stdout
            interface_section = re.search(
                rf"{interface_name}.*?(\n\s+[^\n]+)+", output, re.DOTALL)

            if interface_section:
                interface_info = interface_section.group(0)
                match_ip = re.search(
                    r"Autoconfiguration IPv4 Address\\. .*: (\d+\.\d+\.\d+\.\d+)", interface_info)
                if match_ip:
                    return match_ip.group(1)

        elif os_name == "Darwin":  # MacOS
            result = subprocess.run(
                ["ifconfig", interface_name],
                capture_output=True,
                text=True,
                check=True
            )
            output = result.stdout
            match_ip = re.search(r"inet (\d+\.\d+\.\d+\.\d+)", output)
            if match_ip:
                return match_ip.group(1)

        elif os_name == "Linux":  # Linux (Ubuntu)
            result = subprocess.run(
                ["ip", "addr", "show", interface_name],
                capture_output=True,
                text=True,
                check=True
            )
            output = result.stdout
            match_ip = re.search(r"inet (\d+\.\d+\.\d+\.\d+)/", output)
            if match_ip:
                return match_ip.group(1)

    except subprocess.CalledProcessError as e:
        print(f"Failed to retrieve IP address: {e}")

    return None


def getLocalAndUsbIPs():
    """
    Retrieves all local IPs starting with '192.' and USB IPs starting with '169.'.
    :return: A dictionary with two keys: 'local_ips' and 'usb_ips',
             each containing a list of corresponding IP addresses.
    """
    local_ips = []
    usb_ips = []
    try:
        hostname = socket.gethostname()
        # Only append '.local' if there's no dot in the hostname (i.e., no domain suffix)
        if '.' not in hostname:
            hostname = f"{hostname}.local"

        ip_addresses = socket.gethostbyname_ex(hostname)[2]
        local_ips = [ip for ip in ip_addresses if ip.startswith("192.")]
        usb_ips = [ip for ip in ip_addresses if ip.startswith("169.")]
    except Exception as e:
        print(f"Error retrieving IPs: {e}")
        return {"local_ips": [], "usb_ips": []}

    return {"local_ips": local_ips, "usb_ips": usb_ips}


def chooseIpInteractive(ip_data):
    """
    Prompts the user to choose an IP from the provided list of IPs.

    :param ip_data: A dictionary containing 'local_ips' and 'usb_ips'.
    :return: The chosen IP address as a string.
    """
    all_ips = ip_data.get("local_ips", []) + ip_data.get("usb_ips", [])

    if not all_ips:
        logger.info("No IP addresses found.")
        return None

    print("Available IPs:")
    for idx, ip in enumerate(all_ips, 1):
        print(f"{idx}: {ip}")

    while True:
        try:
            choice = int(input("Choose an IP by entering its number: "))
            if 1 <= choice <= len(all_ips):
                return all_ips[choice - 1]
            else:
                print("Invalid choice. Please choose a valid number.")
        except ValueError:
            print("Invalid input. Please enter a number.")


def getValidHostIP():
    ip_data = getLocalAndUsbIPs()
    all_ips = ip_data.get("local_ips", []) + ip_data.get("usb_ips", [])
    if all_ips is None:
        return None
    if len(all_ips) == 0:
        return None
    if len(all_ips) == 1:
        return all_ips[0]

    # If there are more than one: choose
    logger.info("More than one possible IP Address")
    time.sleep(0.2)
    chosen_ip = chooseIpInteractive(ip_data)
    return chosen_ip


def is_ipv4(address):
    """Check if the provided address is a valid IPv4 address."""
    try:
        socket.inet_aton(address)
        return True
    except socket.error:
        return False


def ipv4_to_bytes(ipv4_str):
    """Encode an IPv4 string into 4 bytes."""
    if not is_ipv4(ipv4_str):
        raise ValueError("Invalid IPv4 address.")
    # Use socket library to pack the IPv4 string into 4 bytes
    return socket.inet_aton(ipv4_str)


def bytes_to_ipv4(byte_data):
    """Decode 4 bytes back into an IPv4 string."""
    if len(byte_data) != 4:
        raise ValueError("Invalid byte length for IPv4 address.")
    # Use socket library to unpack the bytes back into a string
    return socket.inet_ntoa(byte_data)


def resolveHostname(hostname):
    """Resolve a hostname to an IP address and check its network availability.

    Args:
        hostname (str): The hostname to resolve.

    Returns:
        str: The IP address of the hostname, or an error message if unreachable.
    """
    try:
        # Step 1: Resolve the hostname to an IP address
        address = socket.gethostbyname(hostname)
        return address

    except socket.gaierror:
        return None


def pingAddress(address, timeout=1):
    """
    Ping the IP address with a reduced timeout to check if it is reachable on the network.
    Args:
    - address (str): The IP address to ping.
    - timeout (int): The timeout in seconds for the ping.
    Returns:
    - bool: True if the address is reachable, False otherwise.
    """
    os_name = platform.system().lower()
    if os_name == "windows":
        # Windows uses -n for count and -w for timeout in milliseconds
        command = ["ping", "-n", "1", "-w", str(timeout * 1000), address]
    elif os_name == "linux":
        # Linux uses -c for count and -W for timeout in seconds
        command = ["ping", "-c", "1", "-W", str(timeout), address]
    elif os_name == "darwin":
        # MacOS uses -c for count and -t for TTL (not the same as timeout, but closest available)
        command = ["ping", "-c", "1", "-t", str(timeout), address]
    else:
        print(f"Unsupported operating system: {os_name}")
        return False

    try:
        response = subprocess.run(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return response.returncode == 0
    except Exception as e:
        print(f"An error occurred while pinging: {e}")
        return False


def pingAddresses(addresses, timeout=1):
    """
    Ping a list of IP addresses concurrently and return a dictionary indicating reachability.
    Args:
    - addresses (list): A list of IP addresses to ping.
    - timeout (int): The timeout in seconds for each ping.
    Returns:
    - dict: A dictionary with IP addresses as keys and True/False as values indicating reachability.
    """
    results = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        try:
            future_to_address = {executor.submit(pingAddress, address, timeout): address for address in addresses}
        except RuntimeError:
            return None
        for future in concurrent.futures.as_completed(future_to_address):
            address = future_to_address[future]
            try:
                results[address] = future.result()
            except Exception as e:
                print(f"An error occurred while processing {address}: {e}")
                results[address] = False
    return results


def continuousAddressCheck(addresses, interval=5, timeout=1):
    """
    Continuously ping a list of IP addresses every `interval` seconds and print their reachability status.
    Args:
    - addresses (list): A list of IP addresses to ping.
    - interval (int): The interval in seconds between each round of pings.
    - timeout (int): The timeout in seconds for each ping.
    """

    def run_check():
        while True:
            ping_results = pingAddresses(addresses, timeout)
            for address, is_reachable in ping_results.items():
                status = "reachable" if is_reachable else "not reachable"
                print(f"The IP address {address} is {status}.")
            time.sleep(interval)

    check_thread = threading.Thread(target=run_check, daemon=True)
    check_thread.start()


def getHostnameFromIP(ip_address):
    try:
        # Perform a reverse DNS lookup
        hostname, _, _ = socket.gethostbyaddr(ip_address)
        return hostname
    except socket.herror:
        return None
    except socket.gaierror:
        return None
    except Exception as e:
        return None


def getIPAddressOfDevice(address):
    # Check if the address is a valid IPv4 String:
    if is_ipv4(address):
        return address
    else:
        return resolveHostname(address)


def check_internet(timeout=0.25):
    """
    Checks if the device has internet connectivity by pinging 8.8.8.8.

    :param timeout: Timeout in seconds for the ping command.
    :return: True if the device can ping 8.8.8.8, False otherwise.
    """
    try:
        # Determine the platform
        system = platform.system()

        if system == "Windows":
            # Use -n (count) and -w (timeout in ms) for Windows
            result = subprocess.run(
                ["ping", "-n", "1", "-w", str(int(timeout * 1000)), "8.8.8.8"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
        else:
            # Use -c (count) and -W (timeout in s) for Linux/macOS
            result = subprocess.run(
                ["ping", "-c", "1", "-W", str(int(timeout)), "8.8.8.8"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )

        return result.returncode == 0  # Return True if ping was successful (returncode 0)
    except Exception as e:
        print(f"Error while checking internet connectivity: {e}")
        return False


if __name__ == '__main__':
    addresses_to_ping = ['192.168.1.1', 'twipr1', '192.168.2.1', 'twipr3', '8.8.8.8', '192.168.20.1']
    continuousAddressCheck(addresses_to_ping, interval=5)

    time.sleep(20)
