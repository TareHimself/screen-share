from pygame.locals import *
import time
import pygame
import cv2
import numpy as np
from queue import Queue, Empty
from constants import CAPTURE_PARAMS, DOWNSCALE_PERCENT, FRAME_RATE
from client import SignalingClient, UDP_OPCODES
from utils import decode_image

client_b = SignalingClient(
    "stream", "capture", ("127.0.0.1", 9200), ("127.0.0.1", 9000))

frame_buff = Queue()

QUEUING_VIDEO = True
TARGET_QUEUE_SIZE = 60


def on_recieve_pack(d: bytes, add: tuple[str, int], op: int):
    global frame_buff
    if op == UDP_OPCODES.CLIENT_IMAGE:
        frame_buff.put(d)


client_b.add_on_packet(on_recieve_pack)

while 1:
    if not QUEUING_VIDEO:
        try:
            start = time.time()
            frame = frame_buff.get(timeout=10)
            print("Current Queued Frames",
                  frame_buff.qsize(), "          ", end="\r")
            cv2.imshow('stream', decode_image(frame))
            cv2.waitKey(1)
            time.sleep(FRAME_RATE)
        except Empty as e:
            print("No More Data From Capture")
            break
    else:
        print("Queueing video frames", frame_buff.qsize(), "          ", end="\r")
        if frame_buff.qsize() > TARGET_QUEUE_SIZE:
            QUEUING_VIDEO = False


# flags = DOUBLEBUF

# pygame.init()
# pygame.event.set_allowed([QUIT])

# display = pygame.display.set_mode((int(CAPTURE_PARAMS[0] * DOWNSCALE_PERCENT),
#                                    int(CAPTURE_PARAMS[1] * DOWNSCALE_PERCENT)), flags, 16)

# running = True
# while running:
#     for event in pygame.event.get():
#         if event.type == pygame.QUIT:
#             running = False

#     if len(frame_buff) > 0:
#         frame = frame_buff.pop()
#         frame = decode_image(frame)

#         display.blit(pygame.image.frombuffer(
#             frame.tostring(), frame.shape[1::-1], "BGR").convert(), (0, 0))

#     pygame.display.update()

# pygame.quit()
