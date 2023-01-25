import time
import cv2
import numpy as np
from windows import WindowCapture
from constants import CAPTURE_PARAMS, DOWNSCALE_PERCENT
from soc import SignalingClient, UDP_OPCODES
from utils import encode_image

client_a = SignalingClient(
    "capture", "stream", ("127.0.0.1", 9100), ("127.0.0.1", 9000))

cap = WindowCapture()
while True:
    if client_a.other_address is not None:
        frame: np.ndarray = cap.capture(*CAPTURE_PARAMS)
        frame: np.ndarray = cv2.resize(frame, (int(CAPTURE_PARAMS[0] * DOWNSCALE_PERCENT), int(
            CAPTURE_PARAMS[1] * DOWNSCALE_PERCENT)), interpolation=cv2.INTER_LINEAR)

        client_a.send(encode_image(frame), client_a.other_address,
                      UDP_OPCODES.CLIENT_IMAGE)
    time.sleep(0.01)
