import socket
import asyncio
from typing import Union, Callable
from uuid import uuid4
from math import ceil
from datetime import datetime
from threading import Thread

PACKET_PART_HEADER_EXPONENT = 5  # assumes max of 99999 parts


def pad(num: int, length: int = 2):
    final = str(num)
    current_len = len(final)
    if current_len < length:
        final = ("0" * (length - current_len)) + final

    return final


def generate_packet_id():
    now = datetime.utcnow()
    return f"{now.year}{pad(now.month)}{pad(now.day)}{pad(now.second)}{pad(now.microsecond,6)}"


def encode_header(packet_id: str, packet: bytes, index: int = 0, total: int = 1):
    index_s = str(index)
    total_s = str(total - 1)
    index_s = ("0"*(PACKET_PART_HEADER_EXPONENT - len(index_s))) + index_s
    total_s = ("0"*(PACKET_PART_HEADER_EXPONENT - len(total_s))) + total_s

    return f"{packet_id}|{index_s}|{total_s}".encode('utf-8') + packet


HEADER_LENGTH = len(encode_header(generate_packet_id(), b''))
MAX_PACKET_DATA = int(1024 * 0.5)
SOCKET_BUFF_LENGTH = MAX_PACKET_DATA + HEADER_LENGTH


def decode_header(packet: bytes):
    packet_id, part, total = packet[0:HEADER_LENGTH].decode('utf-8').split("|")
    packet = packet[HEADER_LENGTH:len(packet)]

    return packet_id, int(part), int(total) + 1, packet


class UdpSocket:
    def __init__(self, address: tuple[str, int]) -> None:
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind(address)
        self.client = None
        self.callbacks = []
        self.pending_messages = {}
        self.active = True
        self.t1 = Thread(group=None, target=self._recv_packets, daemon=True)
        self.t1.start()
        self.pending_bytes: dict[str, list[tuple[int, bytes]]] = {}

    def get_complete_packet(self):
        raw_packet, sender = self.socket.recvfrom(SOCKET_BUFF_LENGTH)
        packet_id, index, total, packet = decode_header(raw_packet)
        "<PACKET_BOUNDRY>Hello world<PACKET_BOUNDTRY/>"
        # print(
        #     f"<< ID {packet_id} | Part {index + 1}/{total}          ")

        if index == 0 and index == total:
            return packet, sender
        else:
            if packet_id not in self.pending_bytes.keys():
                self.pending_bytes[packet_id] = []

            self.pending_bytes[packet_id].append((index, packet))

            if len(self.pending_bytes[packet_id]) == total:
                all_parts = self.pending_bytes[packet_id]
                del self.pending_bytes[packet_id]
                all_parts.sort(key=lambda x: x[0])
                combined = b''.join(map(lambda a: a[1], all_parts))
                return combined, sender
        return None

    def _recv_packets(self):
        while True:
            try:
                data = self.get_complete_packet()
                if data is not None:
                    packet, add = data
                    self.handle_new_packet(packet, add)
            except socket.timeout:
                break

        self.socket.close()

    def handle_new_packet(self, packet: bytes, address: tuple[str, int]):
        self.on_packet(packet, address)

    def send(self, packet: bytes, address: tuple[str, int]):
        self._send(packet, address)

    def _send(self, packet: bytes, address: tuple[str, int]):
        if len(packet) > SOCKET_BUFF_LENGTH:
            packet_id = generate_packet_id()
            packet_size = len(packet)
            parts_total = int(ceil(packet_size / MAX_PACKET_DATA))
            parts = [packet[i * MAX_PACKET_DATA:(i + 1) * MAX_PACKET_DATA] if i <
                     parts_total - 1 else packet[i * MAX_PACKET_DATA:packet_size] for i in range(parts_total)]
            for i in range(parts_total):
                # print(
                #     f">> ID {packet_id} | Part {i + 1}/{parts_total}          ")
                final_packet = encode_header(
                    packet_id, parts[i], i, parts_total)
                self.socket.sendto(final_packet, address)
        else:
            final_packet = encode_header(generate_packet_id(), packet)
            self.socket.sendto(final_packet, address)

    def kill(self):
        self.socket.settimeout(1)

    def on_packet(self, packet: bytes, address: tuple[str, int]):
        pass


class UDP_OPCODES:
    UNKNOWN = 0
    CLIENT_SIGNALING = 1
    SERVER_SIGNALING = 2
    CLIENT_DEBUG = 3
    CLIENT_IMAGE = 4


class UdpSocketWithOp(UdpSocket):
    def __init__(self, address: tuple[str, int], op_encoding_size=4) -> None:
        super().__init__(address)
        self.op_encoding_size = op_encoding_size

    def handle_new_packet(self, packet: bytes, address: tuple[str, int]):
        op = int.from_bytes(packet[0:self.op_encoding_size], "big")
        packet = packet[self.op_encoding_size:len(packet)]
        self.on_packet(packet, address, op)

    def send(self, packet: bytes, address: tuple[str, int], op=0):
        super().send(op.to_bytes(
            self.op_encoding_size, 'big') + packet, address)

    def on_packet(self, packet: bytes, address: tuple[str, int], op: int):
        pass
