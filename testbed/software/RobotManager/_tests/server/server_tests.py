import time

from core.communication.wifi.tcp.protocols.tcp_json_protocol import TCP_JSON_Message
from core.communication.wifi.tcp.tcp_connection import TCP_Connection
from core.communication.wifi.tcp.tcp_server import TCP_Server
from core.communication.wifi.tcp.tcp_socket import TCP_SocketsHandler, TCP_Socket
from core.device import Device
from core.device_manager import DeviceManager


def TCP_SocketsHandler_test():
    tcp_socket: TCP_Socket = None

    def new_socket_callback(socket, *args, **kwargs):
        print("New Socket")
        nonlocal tcp_socket
        tcp_socket = socket

    server = TCP_SocketsHandler('192.168.8.199')
    server.callbacks.client_connected.register(new_socket_callback)
    server.start()

    while True:
        if tcp_socket is not None:
            tcp_socket.send(b"Hello")
        time.sleep(1)


def TCP_Server_test():
    tcp_connection: TCP_Connection = None
    time1 = 0

    def rx_callback(*args, **kwargs):
        print(f"Time: {((time.perf_counter() - time1) * 1000):.1f}ms")

    def connected_callback(connection, *args, **kwargs):
        nonlocal tcp_connection
        tcp_connection = connection
        tcp_connection.callbacks.rx.register(rx_callback)
        print("Client Connected")

    server = TCP_Server('192.168.8.200')
    server.callbacks.connected.register(connected_callback)
    server.start()

    while True:
        if tcp_connection is not None:
            time1 = time.perf_counter()

            msg = TCP_JSON_Message()
            msg.data = {"a": 1, "b": "Hello"}
            msg.type = 'write'
            tcp_connection.send(msg)
        time.sleep(0.1)


def DeviceManager_Test():
    g_device: Device = None
    time1 = 0
    manager = DeviceManager()

    def rx_callback(*args, **kwargs):
        print(f"Time: {((time.perf_counter() - time1) * 1000):.1f}ms")

    def new_device_callback(device, *args, **kwargs):
        print("New Device")
        nonlocal g_device
        g_device = device
        g_device.callbacks.rx.register(rx_callback)

    manager.init()

    manager.callbacks.new_device.register(new_device_callback)

    manager.start()

    while True:

        if g_device is not None:
            msg = TCP_JSON_Message()
            msg.data = {"a": 1, "b": "Hello"}
            msg.type = 'write'

            time1 = time.perf_counter()
            g_device.send(msg)

        time.sleep(0.1)


if __name__ == '__main__':
    DeviceManager_Test()
