# -*- coding: utf-8 -*-
# @Time    : 2020/1/9 20:36
# @Author  : zwenc
# @Email   : zwence@163.com
# @File    : imageRemoveSmallArea.py

import cv2
import numpy as np
import threading

class imageRSmallArea(threading.Thread):
    def __init__(self, image, areaSize, callBackFun):
        threading.Thread.__init__(self)
        self.image = np.copy(image)
        self.callback = callBackFun
        self.areaSize = areaSize

        self.blockNum = 0

        self.start()

    def run(self):
        self.removeInnermostArea()

    def removeInnermostArea(self):
        # 背景一定要是黑色，不是黑色的要取反
        temp_image = 255 - np.copy(self.image)
        gray_image = cv2.cvtColor(temp_image, cv2.COLOR_BGR2GRAY)

        ret, gray_image = cv2.threshold(gray_image, 127, 255, 0)

        # 求取轮廓
        _, contours, hierarchy = cv2.findContours(gray_image, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
        self.callback(True,False, 10)

        outlistLen = len(contours)
        self.blockNum = outlistLen
        if outlistLen > 0:
            for index in range(outlistLen):
                cnt = contours[index]
                area = cv2.contourArea(cnt)
                if area < self.areaSize:
                    cv2.drawContours(self.image, contours, index, (0, 0, 0), thickness=-1)
                    self.blockNum = self.blockNum - 1
                self.callback(True, False, int((index/outlistLen)*90) + 10)

        self.callback(True, True, 100)

    def getOutImage(self):
        return self.image

if __name__ == "__main__":
    print("hello word!")