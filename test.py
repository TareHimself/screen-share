import time
from soc import encode_header, UdpSocket, SOCKET_BUFF_LENGTH


class UdpTest(UdpSocket):
    def __init__(self, address: tuple[str, int]) -> None:
        super().__init__(address)

    def on_packet(self, packet: bytes, address: tuple[str, int]):
        print(address, "Recieved ", packet.decode('utf-8'))


client_add = ("127.0.0.1", 10000)
server_add = ("127.0.0.1", 11000)
client = UdpTest(client_add)
server = UdpTest(server_add)

client.send(
    "Can you see this text? It should be longer than the recieve size".encode('utf-8'), server_add)

while True:
    time.sleep(10)
