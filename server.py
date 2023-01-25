import time
from soc import SignalingServer

ser = SignalingServer(("127.0.0.1", 9000))

while True:
    time.sleep(10)
