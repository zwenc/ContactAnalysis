# -*- coding: utf-8 -*-
# @Time    : 2020/1/6 15:58
# @Author  : zwenc
# @Email   : zwence@163.com
# @File    : imageRemoveOuterArea.py

import cv2
import numpy as np
import threading

class imageROuterArea(threading.Thread):
    def __init__(self, image, callBackFun):
        threading.Thread.__init__(self)

        self.image = np.copy(image)
        self.callback = callBackFun
        self.outImage = self.image
        self.maxAreaSize = 0

        self.start()

    def run(self):
        # 背景一定要是黑色，不是黑色的要取反
        temp_image = np.copy(self.image)
        temp_image = 255 - temp_image

        gray_image = cv2.cvtColor(temp_image, cv2.COLOR_BGR2GRAY)

        # 求取轮廓
        _, contours, hierarchy = cv2.findContours(gray_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # 判断轮廓数量
        if len(contours) <= 1:
            self.outImage = self.image
            self.maxAreaSize = cv2.contourArea(contours[0])
            self.callback(True, True, 100)
            return

        # 找到最大轮廓的index
        maxSize = 0
        maxIndex = 0
        for index, contour in enumerate(contours):
            temp = cv2.contourArea(contour)
            if temp > maxSize and temp >= 1:
                maxSize = temp
                maxIndex = index
                self.maxAreaSize = maxSize

        # 不是最大轮廓的，全部涂黑
        for index, contour in enumerate(contours):
            if index == maxIndex:
                continue

            cv2.drawContours(self.image, contours, index, (255, 255, 255), thickness=-1)

        self.outImage = self.image
        self.callback(True, True, 100)

    def getOutImage(self):
        return self.outImage

    def getMaxAreaSize(self):
        return self.maxAreaSize

if __name__ == "__main__":
    print("hello word!")