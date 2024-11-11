import time
from soc import UdpSocketWithOp, UDP_OPCODES


class SignalingServer(UdpSocketWithOp):
    def __init__(self, address: tuple[str, int]) -> None:
        super().__init__(address)
        self.clients = {}
        self.pending_connections = {}

    def on_packet(self, packet: bytes, address: tuple[str, int], op: int):
        try:
            if op == UDP_OPCODES.CLIENT_SIGNALING:
                print("Got Signalling Request")
                data = packet.decode('utf-8')   
                user_id, waiting_for_id = data.split("|")
                if waiting_for_id in self.pending_connections.keys():
                    waiting_for_ip, waiting_for_port = self.pending_connections[waiting_for_id]
                    self.send(f"{address[0]}|{address[1]}".encode(
                        'utf-8'),
                        (waiting_for_ip, waiting_for_port), UDP_OPCODES.SERVER_SIGNALING)

                    self.send(f"{waiting_for_ip}|{waiting_for_port}".encode(
                        'utf-8'), address, UDP_OPCODES.SERVER_SIGNALING)
                    del self.pending_connections[waiting_for_id]
                else:
                    self.pending_connections[user_id] = address
        except:
            pass


ser = SignalingServer(("127.0.0.1", 9000))

while True:
    time.sleep(10)
