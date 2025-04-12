import dataclasses
import threading
import time

from core.communication.wifi.udp.protocols.udp_json_protocol import UDP_JSON_Protocol, UDP_JSON_Message
from core.communication.wifi.udp.udp_socket import UDP_Socket
from core.communication.wifi.udp.protocols.udp_base_protocol import UDP_Base_Protocol
from core.utils.callbacks import callback_definition, CallbackContainer
from core.utils.network.network import getIPAddressOfDevice
import atexit
from core.utils.logging_utils import Logger

logger = Logger('UDP')
logger.setLevel('INFO')


@callback_definition
class UDP_Callbacks:
    rx: CallbackContainer


@dataclasses.dataclass
class UDP_Broadcast:
    message: UDP_JSON_Message = None
    port: int = None
    time: float = 1
    _last_sent: float = 0


########################################################################################################################
class UDP:
    base_protocol = UDP_Base_Protocol
    protocols = [UDP_JSON_Protocol]
    callbacks: UDP_Callbacks
    address: str
    _sockets: dict[int, UDP_Socket]
    _ports: list
    _broadcasts: list[UDP_Broadcast]

    _thread: threading.Thread
    _exit: bool

    def __init__(self, address, port=None):
        atexit.register(self.close)

        self.address = address

        if self.address is None:
            raise Exception('No Local IP found')

        if port is None:
            raise Exception('No UDP ports specified')

        if not isinstance(port, (int, list)):
            raise Exception('ports must be a list or int')

        if isinstance(port, int):
            port = [port]

        self._ports = port
        self._sockets = {}

        for port in self._ports:
            socket = UDP_Socket(address=self.address, port=port, config={'filterBroadcastEcho': True})
            socket.callbacks.rx.register(self._rxCallback)
            self._sockets[port] = socket

        self._broadcasts = []
        self._thread = threading.Thread(target=self._threadFunction)
        self._exit = False

        self.callbacks = UDP_Callbacks()

    # ------------------------------------------------------------------------------------------------------------------
    def init(self):
        ...

    # ------------------------------------------------------------------------------------------------------------------
    def start(self):
        logger.info(f"Starting UDP on {self.address}")
        for socket in self._sockets.values():
            socket.start()
        self._thread.start()

    # ------------------------------------------------------------------------------------------------------------------
    def close(self):
        for socket in self._sockets.values():
            socket.close()

        if self._thread.is_alive():
            self._thread.join()

    # ------------------------------------------------------------------------------------------------------------------
    def send(self, message, address='<broadcast>', port: int = None):

        if address is None:
            return

        if port is None:
            for socket in self._sockets.values():
                payload = self._encodeMessage(message, address, port=0)
                socket.send(payload, address)
        else:
            if port in self._sockets:
                payload = self._encodeMessage(message, address, port)
                self._sockets[port].send(payload, address)

    # ------------------------------------------------------------------------------------------------------------------
    def addBroadcast(self, broadcast: UDP_Broadcast):

        if not isinstance(broadcast, UDP_Broadcast):
            raise Exception('broadcast must be a UDP_Broadcast')
        self._broadcasts.append(broadcast)

    # ------------------------------------------------------------------------------------------------------------------
    def _threadFunction(self):

        while not self._exit:
            current_time = time.time()
            # Check the broadcasts
            for broadcast in self._broadcasts:
                if current_time > (broadcast.time + broadcast._last_sent):
                    broadcast._last_sent = current_time
                    self.send(message=broadcast.message, address='<broadcast>', port=broadcast.port)
            time.sleep(0.01)

    # ------------------------------------------------------------------------------------------------------------------
    def _rxCallback(self, data, address, port, *args, **kwargs):
        message = self._decodeMessage(data, *args, **kwargs)

        if message is not None:
            for callback in self.callbacks.rx:
                callback(message, address, port, *args, **kwargs)

    # ------------------------------------------------------------------------------------------------------------------
    def _encodeMessage(self, message, address, port):

        # Check if the message is in an allowed protocol
        if message._protocol not in self.protocols and message._protocol is not self.base_protocol:
            logger.warning("Unknown protocol")
            return

        # Get the source address
        source_address = self.address

        # Get the target address
        target_address = getIPAddressOfDevice(address)

        # Generate the payload
        data = message.encode(source_address=source_address, target_address=target_address, port=port)

        # Check if it is the base protocol
        if message._protocol is not self.base_protocol:
            # Generate the overall message
            base_message = self.base_protocol.Message()
            base_message.data_protocol_id = message._protocol.identifier

            if target_address is None:
                logger.warning(f'Invalid Target Address {address}')
                return

            base_message.source = source_address
            base_message.address = target_address
            base_message.data = data
            buffer = base_message.encode()
        else:
            buffer = data

        return buffer

    # ------------------------------------------------------------------------------------------------------------------
    def _decodeMessage(self, data, *args, **kwargs):
        # Try to decode the message into a UDP Base Message
        base_message = self.base_protocol.decode(data)
        if base_message is None:
            return None

        # Check the Protocol
        protocol_id = base_message.data_protocol_id

        protocol = next((protocol for protocol in self.protocols if protocol.identifier == protocol_id), None)

        if protocol is None:
            print("Wrong protocol ID for UDP")
            return None

        message = protocol.decode(base_message.data)
        if message is None:
            return None

        return message
