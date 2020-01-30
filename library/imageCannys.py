# -*- coding: utf-8 -*-
# @Time    : 2020/1/8 13:47
# @Author  : zwenc
# @Email   : zwence@163.com
# @File    : imageCannys.py

import cv2
import numpy as np
import threading

class imageCannys(threading.Thread):
    def __init__(self, image, callBackFun):
        threading.Thread.__init__(self)

        self.image = np.copy(image)
        self.callback = callBackFun

        self.start()

    def run(self):
        temp_gray = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)
        canny = 255 - cv2.Canny(temp_gray, 50, 150)

        self.image[:, :, 0] = canny
        self.image[:, :, 1] = canny
        self.image[:, :, 2] = canny

        self.callback(True, True, 100)

    def getOutImage(self):
        return self.image


if __name__ == "__main__":
    print("hello word!")
