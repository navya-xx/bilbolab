import ipaddress
import subprocess
import socket


def get_connected_devices(subnet_filters=None, excluded_ips=None):
    """
    Get a list of all connected devices to the Soft AP with hostname and IP, filtered by subnets and exclusions.

    Args:
        subnet_filters (list): List of subnets to include (e.g., ['192.168.8.0/24', '192.168.4.0/24']).
        excluded_ips (list): List of IPs to exclude (e.g., ['192.168.8.1']).

    Returns:
        list of dict: A list of dictionaries with keys 'hostname' and 'ip' for devices meeting the criteria.
    """
    if subnet_filters is None:
        subnet_filters = []  # No filters, include everything
    if excluded_ips is None:
        excluded_ips = []  # No excluded IPs

    try:
        # Parse subnets for filtering
        subnets = [ipaddress.ip_network(subnet) for subnet in subnet_filters]
        excluded_ips = set(excluded_ips)  # Convert exclusions to a set for quick lookups

        # Use `ip neigh` to get connected devices' IPs and MAC addresses
        result = subprocess.run(["ip", "neigh"], stdout=subprocess.PIPE, text=True)
        lines = result.stdout.splitlines()
        print(lines)
        devices = []
        for line in lines:
            parts = line.split()
            if len(parts) >= 4 and parts[3] == "lladdr":
                ip = parts[0]
                # Check if it's a valid IPv4 address
                try:
                    ip_obj = ipaddress.ip_address(ip)
                    if ip_obj.version != 4:  # Skip non-IPv4 addresses
                        continue
                except ValueError:
                    continue

                # Check subnet filters
                if subnets and not any(ip_obj in subnet for subnet in subnets):
                    continue

                # Check exclusions
                if ip in excluded_ips:
                    continue

                # Resolve hostname
                try:
                    hostname = socket.gethostbyaddr(ip)[0]
                except socket.herror:
                    hostname = "Unknown"

                devices.append({"hostname": hostname, "ip": ip})

        return devices
    except Exception as e:
        print(f"Error fetching connected devices: {e}")
        return []


def is_soft_ap_running(interface="wlan0_ap"):
    """
    Check if the Soft AP is running on the specified interface.

    Args:
        interface (str): The network interface of the Soft AP (default is "wlan0_ap").

    Returns:
        bool: True if the Soft AP is running, False otherwise.
    """
    try:
        # Check the interface status using `ip`
        result = subprocess.run(["ip", "link", "show", interface], stdout=subprocess.PIPE, text=True)
        return "state UP" in result.stdout
    except Exception as e:
        print(f"Error checking Soft AP status: {e}")
        return False


# Example usage
if __name__ == "__main__":
    subnet_filters = ['192.168.8.0/24', '192.168.4.0/24']
    excluded_ips = ['192.168.8.1', '192.168.4.1']

    devices = get_connected_devices(subnet_filters=subnet_filters, excluded_ips=excluded_ips)
    print("Connected devices:")
    for device in devices:
        print(f"Hostname: {device['hostname']}, IP: {device['ip']}")

    ap_status = is_soft_ap_running()
    print(f"Is Soft AP running? {'Yes' if ap_status else 'No'}")
