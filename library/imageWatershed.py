# -*- coding: utf-8 -*-
# @Time    : 2020/1/12 10:15
# @Author  : zwenc
# @Email   : zwence@163.com
# @File    : imageWatershed.py

import cv2
import threading
import numpy as np

class imageWatershed(threading.Thread):
    def __init__(self, image, Oimage, callBackFun):
        """
        image:  已经经过二值化并且去噪的图像
        Oimage: 原始图像
        callBackFun: 回调函数（你不用管它）
        """
        threading.Thread.__init__(self)

        self.image = np.copy(image)
        self.OImage = np.copy(Oimage)
        self.callback = callBackFun
        self.outImage = np.zeros_like(self.image)
        self.start()

    def run(self):
        gray = 255 - cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
        opening = cv2.morphologyEx(gray, cv2.MORPH_CLOSE, kernel)
        # opening = gray
        sure_bg = cv2.dilate(opening, kernel, iterations=1)  # sure background area

        dist_transform = cv2.distanceTransform(opening, cv2.DIST_L2, 5)
        cv2.normalize(dist_transform, dist_transform, 0, 1.0, cv2.NORM_MINMAX)

        ret, sure_fg = cv2.threshold(dist_transform, 0.005 * dist_transform.max(), 255, 0)
        sure_fg = np.uint8(sure_fg)

        unknown = cv2.subtract(sure_bg, sure_fg)
        ret, markers = cv2.connectedComponents(sure_fg)
        markers = markers + 100
        markers[unknown == 255] = 0

        markers = cv2.watershed(self.OImage, markers)
        self.outImage[markers == 100] = [255, 255, 255]
        self.outImage[markers == -1] = [0, 0, 254]

        self.callback(True, True, 100)

    def getOutImage(self):
        return self.outImage

def callBackTestFun(ret, state, count):
    pass

if __name__ == "__main__":
    img = cv2.imread("../image/temp.png")
    a = imageWatershed(img, callBackTestFun)

