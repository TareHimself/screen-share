import numpy as np
import cv2


def encode_image(frame):
    '''
    :param frame: WxHx3 ndarray
    '''
    _, bts = cv2.imencode('.jpg', frame)
    bts = bts.tostring()
    return bts


def decode_image(bts):
    '''
    :param bts: results from image_to_bts
    '''
    buff = np.fromstring(bts, np.uint8)
    buff = buff.reshape(1, -1)
    img = cv2.imdecode(buff, cv2.IMREAD_COLOR)
    return img
