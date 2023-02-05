import time
import cv2
import numpy as np
from queue import Queue
from threading import Thread
from windows import WindowCapture
from constants import CAPTURE_PARAMS, DOWNSCALE_PERCENT, FRAME_RATE
from client import SignalingClient, UDP_OPCODES
from utils import encode_image

client_a = SignalingClient(
    "capture", "stream", ("127.0.0.1", 9100), ("127.0.0.1", 9000))
frame_buffer = Queue()


def capture_frames():
    global client_a
    cap = WindowCapture()
    while True:
        if client_a.other_address is not None:
            frame: np.ndarray = cap.capture(*CAPTURE_PARAMS)
            frame: np.ndarray = cv2.resize(frame, (int(CAPTURE_PARAMS[0] * DOWNSCALE_PERCENT), int(
                CAPTURE_PARAMS[1] * DOWNSCALE_PERCENT)), interpolation=cv2.INTER_CUBIC)
            frame_buffer.put(frame)
        else:
            time.sleep(0.1)


Thread(target=capture_frames, daemon=True, group=None).start()

while True:
    if client_a.other_address is not None:
        frame = frame_buffer.get()
        start = time.time()

        client_a.send(encode_image(frame), client_a.other_address,
                      UDP_OPCODES.CLIENT_IMAGE)
        print("Frame Sent, Took", time.time() - start)
