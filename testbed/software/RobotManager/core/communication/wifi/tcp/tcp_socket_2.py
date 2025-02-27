import threading
import time
import socket

import cobs.cobs as cobs

from utils.callbacks import callback_handler, CallbackContainer
from utils.logging_utils import Logger
import dataclasses
import queue

logger = Logger('tcp')
logger.setLevel('INFO')

PACKAGE_TIMEOUT_TIME = 5
FAULTY_PACKAGES_MAX_NUMBER = 10


@dataclasses.dataclass
class FaultyPackage:
    timestamp: float


@callback_handler
class TCPSocketCallbacks:
    rx: CallbackContainer
    disconnected: CallbackContainer


########################################################################################################################
class TCP_Socket:
    address: str  # IP address of the client

    rx_queue: queue.Queue  # Queue of incoming messages from the client
    tx_queue: queue.Queue  # Queue of outgoing messages to the client
    config: dict

    rx_callback: callable  # Callback function that is called as soon as a message is received
    rx_event: threading.Event

    _connection: socket.socket

    _rxThread: threading.Thread

    _faultyPackages: list

    # === INIT =========================================================================================================
    def __init__(self, connection: socket, address: str):
        self._connection = connection
        self.address = address

        # connect readyRead-Signal to _rxReady function
        # socket.readyRead.connect(self._rxReady)

        self.config = {
            'delimiter': b'\x00',
            'cobs': True
        }

        self.rx_queue = queue.Queue()
        self.tx_queue = queue.Queue()

        self._exit = False

        self.callbacks = TCPSocketCallbacks()

        self.rx_event = threading.Event()

        self._faultyPackages = []

        self._rxThread = threading.Thread(target=self._rx_thread_fun, daemon=True)
        self._rxThread.start()

    # === METHODS ======================================================================================================

    def send(self, data):
        """

        :param data:
        :return:
        """
        data = self._prepareTxData(data)
        self._write(data)

    # ------------------------------------------------------------------------------------------------------------------
    def rxAvailable(self):
        """

        :return:
        """
        return self.rx_queue.qsize()

    # ------------------------------------------------------------------------------------------------------------------
    def close(self):
        """

        :return:
        """
        self._connection.close()
        self._exit = True
        logger.info(f"TCP socket {self.address} closed")

        for callback in self.callbacks.disconnected:
            callback(self)

    # ------------------------------------------------------------------------------------------------------------------
    def setConfig(self, config):
        """
        Overrides the config with other values.
        :param config: New values for the config
        :return: None
        """
        self.config = {**self.config, **config}

    # === PRIVATE METHODS ==============================================================================================
    def _rx_thread_fun(self):

        while not self._exit:
            # noinspection PyBroadException
            try:
                data = self._connection.recv(8092)
            except Exception:
                logger.warning("Error in TCP connection. Close connection")
                self.close()
                return

            if data == b'':
                self.close()
            elif data is not None:
                # noinspection PyBroadException
                try:
                    self._processRxData(data)
                except Exception:
                    ...  # TODO: Not good and hacky

            else:  # data is empty -> Device has disconnected
                self.close()

            # Remove the faulty packages older than PACKAGE_TIMEOUT_TIME
            self._faultyPackages = [package for package in self._faultyPackages if
                                    time.time() < (package.timestamp + PACKAGE_TIMEOUT_TIME)]

            # Send a warning if more than FAULTY_PACKAGES_MAX_NUMBER faulty packages have been received
            # in the last PACKAGE_TIMEOUT_TIME seconds
            if len(self._faultyPackages) > FAULTY_PACKAGES_MAX_NUMBER:
                logger.warning(
                    f"Received {FAULTY_PACKAGES_MAX_NUMBER} of faulty TCP packages in the last {PACKAGE_TIMEOUT_TIME}"
                    f" seconds")

    # ------------------------------------------------------------------------------------------------------------------
    def _prepareTxData(self, data):
        if isinstance(data, list):
            data = bytes(data)

        # Encode the data and add a delimiter of those options are set
        if self.config['cobs']:
            data = cobs.encode(data)
        if self.config['delimiter'] is not None:
            data = data + self.config['delimiter']

        return data

    # ------------------------------------------------------------------------------------------------------------------
    def _write(self, data):
        self._connection.sendall(data)

    # ------------------------------------------------------------------------------------------------------------------

    def _processRxData(self, data):
        """
        - This functions takes the received byte stream and chops it into data packets. This makes the assumption that
        the separator is not used in the byte stream itself. This can be accomplished by only sending strings or
        cobs-encoded data
        cobs-encoded data
        :param data:
        :return:
        """
        data_packets = data.split(self.config['delimiter'])
        if not data_packets[-1] == b'':
            self._faultyPackages.append(FaultyPackage(timestamp=time.time()))
            return

        data_packets = data_packets[0:-1]

        if self.config['cobs']:
            for i, packet in enumerate(data_packets):
                # noinspection PyBroadException
                try:
                    data_packets[i] = cobs.decode(packet)
                except Exception:
                    self._faultyPackages.append(FaultyPackage(timestamp=time.time()))
                    return
                    # logger.warning("Received incompatible message which cannot be COBS decoded")

        for packet in data_packets:
            self.rx_queue.put_nowait(packet)

        self.rx_event.set()

        for callback in self.callbacks.rx:
            callback(self)


@callback_handler
class TCPSocketsHandlerCallbacks:
    client_connected: CallbackContainer
    client_disconnected: CallbackContainer
    server_error: CallbackContainer


class TCP_SocketsHandler:
    address: str
    port: int
    sockets: list[TCP_Socket]  # List of the connected clients

    _thread: threading.Thread

    _server: socket.socket
    config: dict
    callbacks: TCPSocketsHandlerCallbacks

    _exit: bool

    # ------------------------------------------------------------------------------------------------------------------
    def __init__(self, address, hostname: bool = False, config: dict = None):
        """

        :param address:
        :param hostname:
        """
        super().__init__()

        default_config = {
            'max_clients': 100,
            'port': 6666,
        }

        if config is None:
            config = {}

        self.config = {**default_config, **config}

        self.sockets = []
        self.address = address

        # if address is None and hostname is True:
        #     self.address = getAllIPAdresses()['hostname']
        # elif address is not None:
        #     self.address = address
        # else:
        #     logger.error("No valid IP Address provided. Connect to a private network (192.168. ...)")
        #     exit()

        self.port = self.config['port']

        self.callbacks = TCPSocketsHandlerCallbacks()

        self._exit = False

        self._server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    # ------------------------------------------------------------------------------------------------------------------
    def init(self):
        ...

    # ------------------------------------------------------------------------------------------------------------------
    def start(self):
        self._thread = threading.Thread(target=self._threadFunction, daemon=True)
        self._thread.start()

    # ------------------------------------------------------------------------------------------------------------------
    def close(self):
        logger.info(f"TCP host closed on {self.address}:{self.port}")
        self._server.close()
        self._exit = True
        self._thread.join()

    # ------------------------------------------------------------------------------------------------------------------
    def send(self):
        pass

    # ------------------------------------------------------------------------------------------------------------------
    def _threadFunction(self):
        server_address = (self.address, self.port)
        try:
            self._server.bind(server_address)
        except OSError:
            raise Exception("Address already in use. Please wait until the address is released")

        self._server.listen(self.config['max_clients'])
        logger.info(f"Starting TCP host on {self.address}:{self.port}")

        while not self._exit:
            connection, client_address = self._server.accept()
            self._acceptNewClient(connection, client_address)

    # ------------------------------------------------------------------------------------------------------------------
    def _acceptNewClient(self, connection, address):
        """
         -handling of accepting a new client
         -create a new client object with the socket of the newly accepted client
         :return: nothing
         """
        client = TCP_Socket(connection, address)

        self.sockets.append(client)

        logger.info(f"New client connected: {client.address}")
        # emit new connection signal with peer address and peer port to the interface

        client.callbacks.disconnected.register(self._clientClosed_callback)

        for callback in self.callbacks.client_connected:
            callback(client)

    # ------------------------------------------------------------------------------------------------------------------
    def _clientClosed_callback(self, client: TCP_Socket):
        """
        close a socket once the client has disconnected
        :param client:
        :return: nothing
        """
        # remove client from list
        self.sockets.remove(client)
        for cb in self.callbacks.client_disconnected:
            cb(client)
