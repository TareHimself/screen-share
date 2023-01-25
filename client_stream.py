from pygame.locals import *
import time
import pygame
import numpy as np
from queue import Queue
from constants import CAPTURE_PARAMS, DOWNSCALE_PERCENT
from soc import SignalingClient, UDP_OPCODES
from utils import decode_image

client_b = SignalingClient(
    "stream", "capture", ("127.0.0.1", 9200), ("127.0.0.1", 9000))

frame_buff = []


def on_recieve_pack(d: bytes, add: tuple[str, int], op: int):
    global frame_buff
    if op == UDP_OPCODES.CLIENT_IMAGE:
        frame_buff.append(d)


client_b.add_on_packet(on_recieve_pack)


flags = DOUBLEBUF

pygame.init()
pygame.event.set_allowed([QUIT])

display = pygame.display.set_mode((int(CAPTURE_PARAMS[0] * DOWNSCALE_PERCENT),
                                   int(CAPTURE_PARAMS[1] * DOWNSCALE_PERCENT)), flags, 16)

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    if len(frame_buff) > 0:
        frame = frame_buff.pop()
        frame = decode_image(frame)

        display.blit(pygame.image.frombuffer(
            frame.tostring(), frame.shape[1::-1], "BGR").convert(), (0, 0))

    pygame.display.update()

pygame.quit()
