import time
from typing import Union, Callable
from soc import UdpSocketWithOp, UDP_OPCODES


class SignalingClient(UdpSocketWithOp):
    def __init__(self, my_id: str, other_id: str, my_address: tuple[str, int], server_address: tuple[str, int]) -> None:
        super().__init__(my_address)
        self.my_id = my_id
        self.other_id = other_id
        self.callbacks = []
        self.send(f"{my_id}|{other_id}".encode('utf-8'),
                  server_address, UDP_OPCODES.CLIENT_SIGNALING)
        self.other_address: Union[tuple[str, int], None] = None

    def add_on_packet(self, callback: Callable[[int, bytes, tuple[str, int]], None]):
        self.callbacks.append(callback)

    def on_packet(self, packet: bytes, address: tuple[str, int], op: int):
        if op == UDP_OPCODES.SERVER_SIGNALING:
            ip, port = packet.decode('utf-8').split("|")
            port = int(port)
            self.other_address = (ip, port)
            print("Connected to", self.other_id)
        elif op == UDP_OPCODES.CLIENT_DEBUG:
            print(f"Debug {packet.decode('utf-8')}")

        [callback(packet, address, op) for callback in self.callbacks]
