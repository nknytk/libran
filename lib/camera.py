# coding: utf-8

import sys
from threading import Thread
from time import time, sleep
import cv2


class Camera:
    def __init__(self, config):
        self.config = config
        self.camera = cv2.VideoCapture(config['device'])


    def start(self):
        self.capture_thread = Thread(target=self.regularly_capture)
        self.capture_thread.start()

    def capture(self):
        """ カメラから画像を取得して返す """
        if not self.camera.isOpened():
            self.camera.open(self.config['device'])
        ok, img = self.camera.read()
        self.camera.release()
        if not ok:
            raise Exception(ok)
        return img
