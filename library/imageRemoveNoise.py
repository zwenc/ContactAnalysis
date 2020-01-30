# -*- coding: utf-8 -*-
# @Time    : 2020/1/8 12:05
# @Author  : zwenc
# @Email   : zwence@163.com
# @File    : imageRemoveNoise.py

import cv2
import numpy as np
import threading

class imageRNoise(threading.Thread):
    def __init__(self, image, deep,callBackFun):
        threading.Thread.__init__(self)

        self.image = np.copy(image)
        self.callback = callBackFun
        self.deep = deep

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

        outlist = self.getContourByDeep(hierarchy, self.deep)
        self.callback(True, False, 20)

        outlistLen = len(outlist)
        if outlistLen > 0:
            for index,contourIndex in enumerate(outlist):
                cv2.drawContours(self.image, contours, contourIndex, (255, 255, 255), thickness=-1)
                self.callback(True, False, int((index/outlistLen)*80) + 20)

        self.callback(True, True, 100)
        return self.image

    def getContourByDeep(self, hierarchy, deep):
        start = 0
        outlist = []
        hierarchy = hierarchy[0]

        queue_point = []
        queue_point.append(0)
        while queue_point != []:
            index = queue_point.pop()

            if start >= deep:
                outlist.append(index)

            if hierarchy[index][0] != -1:
                queue_point.append(hierarchy[index][0])
            else:
                if start > 0:
                    start = start - 1

            if hierarchy[index][2] != -1:
                queue_point.append(hierarchy[index][2])
                start = start + 1

        return outlist

    def getOutImage(self):
        return self.image

if __name__ == "__main__":
    print("hello word!")