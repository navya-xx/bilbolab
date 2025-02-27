import fcntl
import getpass
import ipaddress
import re
import socket
import os
import struct
import subprocess
import sys
import platform


def splitServerAddress(address: str):
    server_address = None
    server_port = None
    try:
        server_address = re.search(r'[0-9.]*(?=:)', address)[0]
    except:
        ...
    try:
        server_port = int(re.search(r'(?<=:)[0-9]*', address)[0])
    except:
        ...

    return server_address, server_port


def getAllIPAdresses():
    """

    :param debug:
    :return:
    """

    local_ip = None
    usb_ip = None

    if os.name == 'nt':

        hostname = socket.gethostname()
        ip_addresses = socket.gethostbyname_ex(hostname)[2]
        local_ips = [ip for ip in ip_addresses if ip.startswith("192.168.0")]
        if len(local_ips) == 0:
            return None

        local_ip = [ip for ip in ip_addresses if ip.startswith("192.168.0")][:1][0]
        usb_ip = ''
        server_address = socket.gethostbyname_ex(socket.gethostname())

    elif os.name == 'posix':
        hostname = socket.gethostname()
        ip_addresses = socket.gethostbyname_ex(hostname)[2]
        local_ips = [ip for ip in ip_addresses if ip.startswith("192.168.")]
        if len(local_ips) == 0:
            return None
        local_ip = [ip for ip in ip_addresses if ip.startswith("192.168.")][:1][0]
        usb_ip = ''
        server_address = socket.gethostbyname_ex(socket.gethostname())

    output = {'hostname': hostname, 'local': local_ip, 'usb': usb_ip, 'all': server_address[2]}

    for i, add in enumerate(server_address[2]):
        if add is not local_ip and add is not usb_ip:
            ...
    return output


def getLocalIP():
    """

        :param debug:
        :return:
        """

    local_ip = None
    usb_ip = None

    if os.name == 'nt':

        hostname = socket.gethostname()
        ip_addresses = socket.gethostbyname_ex(hostname)[2]
        local_ips = [ip for ip in ip_addresses if ip.startswith("192.168.0")]
        if len(local_ips) == 0:
            return None

        local_ip = [ip for ip in ip_addresses if ip.startswith("192.168.0")][:1][0]
        usb_ip = ''
        server_address = socket.gethostbyname_ex(socket.gethostname())

    elif os.name == 'posix':
        hostname = socket.gethostname()
        ip_addresses = socket.gethostbyname_ex(hostname)[2]
        local_ips = [ip for ip in ip_addresses if ip.startswith("192.168.")]
        if len(local_ips) == 0:
            return None
        local_ip = [ip for ip in ip_addresses if ip.startswith("192.168.")][:1][0]
        usb_ip = ''
        server_address = socket.gethostbyname_ex(socket.gethostname())

    return local_ip


def get_ip_address_from_interface(interface_name):
    """
    Retrieve the IP address associated with a specific network interface.

    Args:
        interface_name (str): The name of the network interface (e.g., 'wlan0').

    Returns:
        str: The IP address of the interface, or None if the interface has no IP or does not exist.
    """
    try:
        # Create a socket to interact with the network interface
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        # Use ioctl to get the IP address of the interface
        ip_address = socket.inet_ntoa(
            fcntl.ioctl(
                sock.fileno(),
                0x8915,  # SIOCGIFADDR: Get the interface address
                struct.pack("256s", interface_name[:15].encode("utf-8"))
            )[20:24]
        )
        return ip_address
    except OSError as e:
        print(f"Error retrieving IP address for {interface_name}: {e}")
        return None

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


def resolve_hostname(hostname, check_availability=False):
    """Resolve a hostname to an IP address and check its network availability.

    Args:
        hostname (str): The hostname to resolve.
        check_availability (bool): Whether to check if the host is reachable on the network.

    Returns:
        str: The IP address of the hostname, or an error message if unreachable.
    """
    try:
        # Step 1: Resolve the hostname to an IP address
        ip_address = socket.gethostbyname(hostname)

        # Step 2: Optionally check if the host is available on the network
        if check_availability:
            if is_host_reachable(ip_address):
                return f"{hostname} is available at IP: {ip_address}"
            else:
                return f"{hostname} resolved to {ip_address}, but is not reachable on the network."

        return ip_address

    except socket.gaierror:
        return None


def is_host_reachable(ip_address):
    """Ping the IP address to check if it is reachable on the network."""
    # Use different commands depending on the operating system
    param = "-n" if platform.system().lower() == "windows" else "-c"
    command = ["ping", param, "1", ip_address]

    try:
        # Send the ping command and check for a successful response
        response = subprocess.run(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return response.returncode == 0
    except Exception as e:
        print(f"An error occurred while pinging: {e}")
        return False


def get_hostname(ip_address):
    # hostname, _, _ = socket.gethostbyaddr(ip_address)
    # return hostname
    # """Resolve an IP address to a hostname.
    #
    # Args:
    #     ip_address (str): The IP address to resolve.
    #
    # Returns:
    #     str: The hostname associated with the IP address, or an error message if not found.
    # """
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


def getIPAdress(address):
    # Check if the address is a valid IPv4 String:
    if is_ipv4(address):
        return address
    else:
        return resolve_hostname(address)


def getLocalIP_RPi():
    network_information = getNetworkInformation()

    if network_information['local_ip'] is not None:
        return network_information['local_ip']
    elif network_information['usb_ip'] is not None:
        return network_information['usb_ip']
    else:
        return None


def get_current_user():
    """
    Returns the name of the currently logged-in user.
    """
    return getpass.getuser()


def get_own_hostname():
    hostname = socket.gethostname()
    return hostname


def get_wifi_ssid():
    try:
        # Get the SSID of the current Wi-Fi network
        ssid = subprocess.check_output(['/sbin/iwgetid', '-r']).decode().rstrip()
        if ssid == '':
            ssid = None
    except Exception:
        ssid = None

    return ssid


def check_internet(timeout=0.25):
    """
    Checks if the device has internet connectivity by pinging 8.8.8.8.

    :param timeout: Timeout in seconds for the ping command.
    :return: True if the device can ping 8.8.8.8, False otherwise.
    """
    try:
        # Use subprocess to ping 8.8.8.8 with a single packet and specified timeout
        result = subprocess.run(
            ["ping", "-c", "1", "-W", str(timeout), "8.8.8.8"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        return result.returncode == 0  # Return True if ping was successful (returncode 0)
    except Exception as e:
        print(f"Error while checking internet connectivity: {e}")
        return False


def getNetworkInformation():
    try:
        # Get the username from the /home directory
        usernames = os.listdir('/home/')
        username = usernames[0] if usernames else None
    except Exception:
        username = None

    try:
        # Get the hostname of the device
        hostname = socket.gethostname()
    except Exception:
        hostname = None

    try:
        # Get the SSID of the current Wi-Fi network
        ssid = subprocess.check_output(['/sbin/iwgetid', '-r']).decode().rstrip()
        if ssid == '':
            ssid = None
    except Exception:
        ssid = None

    try:
        # Get the list of IP addresses
        ip_string = subprocess.check_output(['hostname', '-I']).decode()
        ips = re.findall(r'[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}', ip_string)

        # Separate IPs into local and USB IPs
        local_ips = [ip for ip in ips if ip.startswith('192.')]
        usb_ips = [ip for ip in ips if ip.startswith('169.')]

        # Use the first local IP or set to None if not found
        local_ip = local_ips[0] if local_ips else None

        usb_ips = usb_ips[0] if usb_ips else None

    except Exception:
        local_ip = None
        usb_ips = None

    return {
        "username": username,
        "hostname": hostname,
        "ssid": ssid,
        "local_ip": local_ip,
        "usb_ip": usb_ips
    }


def scan_network(ip_range):
    """
    Scan the specified range of IP addresses for active devices using nmap.

    Args:
        ip_range (str): The range of IPs to scan (e.g., '192.168.4.2-20').

    Returns:
        list of dict: A list of devices with keys 'hostname', 'ip', and optionally 'mac'.
    """
    try:
        # Run the nmap command with the specified IP range
        result = subprocess.run(
            ["nmap", "-sn", ip_range],
            stdout=subprocess.PIPE,
            text=True,
            timeout=10  # Adjust timeout as needed for the scan size
        )
        lines = result.stdout.splitlines()

        devices = []
        current_device = {}
        for line in lines:
            if "Nmap scan report for" in line:
                parts = line.split()
                ip = parts[-1].strip("()")
                hostname = parts[4] if len(parts) > 5 else "Unknown"
                current_device = {"hostname": hostname, "ip": ip}
            elif "MAC Address" in line:
                mac = line.split()[2]
                current_device["mac"] = mac
            elif current_device:
                devices.append(current_device)
                current_device = {}
        # Append the last device if it wasn't added
        if current_device:
            devices.append(current_device)



        return devices
    except Exception as e:
        print(f"Error scanning the network: {e}")
        return []


# def scan_network(subnet):
#     """
#     Scan the bilbo_net network for active devices using nmap.
#
#     Args:
#         subnet (str): The subnet to scan (e.g., '192.168.1.0/24').
#
#     Returns:
#         list of dict: A list of devices with keys 'hostname' and 'ip'.
#     """
#     try:
#         result = subprocess.run(
#             ["nmap", "-sn", subnet],
#             stdout=subprocess.PIPE,
#             text=True,
#             timeout=6
#         )
#         lines = result.stdout.splitlines()
#
#
#         devices = []
#         current_device = {}
#         for line in lines:
#             if "Nmap scan report for" in line:
#                 parts = line.split()
#                 ip = parts[-1].strip("()")
#                 current_device = {"hostname": parts[4] if len(parts) > 5 else "Unknown", "ip": ip}
#             elif "MAC Address" in line:
#                 mac = line.split()[2]
#                 current_device["mac"] = mac
#             elif current_device:
#                 devices.append(current_device)
#                 current_device = {}
#         return devices
#     except Exception as e:
#         print(f"Error scanning the network: {e}")
#         return []


def filter_devices(devices, subnet_filter=None, excluded_ips=None):
    """
    Filters a list of devices based on subnet and excluded IPs.

    Args:
        devices (list): A list of dictionaries with 'ip' (and optionally other keys).
        subnet_filter (str): The subnet range to include (e.g., '192.168.1.0/24').
        excluded_ips (list): List of IPs to exclude.

    Returns:
        list of dict: Filtered list of devices.
    """
    if excluded_ips is None:
        excluded_ips = []

    filtered_devices = []
    try:
        subnet = ipaddress.ip_network(subnet_filter) if subnet_filter else None

        for device in devices:
            ip = device.get("ip")
            if not ip:
                continue

            try:
                ip_obj = ipaddress.ip_address(ip)
                if ip_obj.version != 4:  # Skip non-IPv4 addresses
                    continue
                if subnet and ip_obj not in subnet:
                    continue
                if ip in excluded_ips:
                    continue
                filtered_devices.append(device)
            except ValueError:
                continue

    except Exception as e:
        print(f"Error filtering devices: {e}")

    return filtered_devices



def get_default_gateway(interface_name):
    """
    Retrieve the default gateway for a specific network interface.

    Args:
        interface_name (str): The name of the network interface (e.g., 'wlan0').

    Returns:
        str: The default gateway IP address, or None if no gateway is found for the interface.
    """
    try:
        with open("/proc/net/route", "r") as route_file:
            for line in route_file:
                fields = line.strip().split()
                if fields[0] == interface_name and fields[1] == "00000000":  # Default route
                    gateway_hex = fields[2]
                    # Convert the gateway from hex to dotted decimal format
                    gateway = ".".join(str(int(gateway_hex[i:i+2], 16)) for i in (6, 4, 2, 0))
                    return gateway
    except Exception as e:
        print(f"Error retrieving default gateway for {interface_name}: {e}")
        return None

def get_subnet_filter(default_gateway, subnet_mask=24):
    """
    Generate a subnet filter for scanning based on the default gateway.

    Args:
        default_gateway (str): The IP address of the default gateway (e.g., '192.168.8.1').
        subnet_mask (int): The subnet mask (default is 24, corresponding to '255.255.255.0').

    Returns:
        str: The subnet filter in CIDR notation (e.g., '192.168.8.0/24').
    """
    try:
        # Parse the default gateway IP and calculate the network
        gateway_ip = ipaddress.ip_address(default_gateway)
        network = ipaddress.ip_network(f"{gateway_ip}/{subnet_mask}", strict=False)
        return str(network)
    except ValueError as e:
        print(f"Error calculating subnet filter: {e}")
        return None

def is_interface_up(interface_name):
    """
    Check whether a specific network interface is UP or DOWN.

    Args:
        interface_name (str): The name of the network interface (e.g., 'wlan0').

    Returns:
        bool: True if the interface is UP, False if it is DOWN or not found.
    """
    try:
        # Run the `ip link show` command for the given interface
        result = subprocess.run(
            ["ip", "link", "show", interface_name],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

        # Check if the output contains 'state UP'
        if "state UP" in result.stdout:
            return True
        elif "state DOWN" in result.stdout:
            return False
        else:
            print(f"Unknown state for interface {interface_name}.")
            return False
    except Exception as e:
        print(f"Error checking interface status: {e}")
        return False



def strip_hostname(hostname):
    """
    Strip the domain from a fully qualified hostname.

    Args:
        hostname (str): The full hostname (e.g., 'bilbo0.lan').

    Returns:
        str: The base name without the domain (e.g., 'bilbo0').
    """
    if not hostname:
        return None

    # Split the hostname by '.' and return the first part
    return hostname.split('.')[0]



def get_ap_ssid(interface_name):
    """
    Retrieve the SSID of the Access Point (AP) running on the given interface.

    Args:
        interface_name (str): The name of the AP interface (e.g., 'wlan0_ap').

    Returns:
        str: The SSID of the AP, or None if the SSID could not be retrieved.
    """
    try:
        # Use the full path to the `iw` command
        result = subprocess.run(
            ["/usr/sbin/iw", "dev", interface_name, "info"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

        # Check for errors in the command
        if result.returncode != 0:
            print(f"Error retrieving SSID for {interface_name}: {result.stderr.strip()}")
            return None

        # Parse the output to find the SSID
        for line in result.stdout.splitlines():
            line = line.strip()
            if line.startswith("ssid"):
                return line.split(" ", 1)[1]  # Return the SSID part

    except Exception as e:
        print(f"Error retrieving SSID for {interface_name}: {e}")
        return None


def get_connected_ssid(interface_name):
    """
    Retrieve the SSID of the wireless network a non-AP device is connected to.

    Args:
        interface_name (str): The name of the wireless interface (e.g., 'wlan0').

    Returns:
        str: The SSID of the connected network, or None if not connected or unable to retrieve.
    """
    try:
        # Use the `iw dev` command to get information about the wireless device
        result = subprocess.run(
            ["/usr/sbin/iw", "dev", interface_name, "link"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

        # Check for errors in the command
        if result.returncode != 0:
            print(f"Error retrieving SSID for {interface_name}: {result.stderr.strip()}")
            return None

        # Parse the output for the SSID
        for line in result.stdout.splitlines():
            line = line.strip()
            if line.startswith("SSID:"):
                return line.split(":", 1)[1].strip()  # Return the SSID value
    except Exception as e:
        print(f"Error retrieving SSID for {interface_name}: {e}")
        return None