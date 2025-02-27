from utils.network import scan_network, filter_devices, get_ip_address_from_interface, get_default_gateway, get_subnet_filter, is_interface_up

if __name__ == "__main__":
    interface = 'wlan0_ap'
    if is_interface_up(interface):
        own_ip = get_ip_address_from_interface(interface)
        print(own_ip)
        default_gateway = get_default_gateway(interface)
        print(default_gateway)
        subnet_filter = get_subnet_filter(own_ip)
        excluded_ips = [default_gateway]
        if own_ip is not None:
            excluded_ips.append(own_ip)


        devices = scan_network(subnet=subnet_filter)
        devices = filter_devices(devices, subnet_filter, excluded_ips)
        for device in devices:
            print(f"IP: {device['ip']}, Hostname: {device['hostname']}")
