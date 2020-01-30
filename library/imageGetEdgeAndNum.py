# -*- coding: utf-8 -*-
# @Time    : 2020/1/12 16:52
# @Author  : zwenc
# @Email   : zwence@163.com
# @File    : imageGetEdgeAndNum.py

import cv2
import threading
import numpy as np

class imageGetEdgeAndNum(threading.Thread):
    def __init__(self, image, callBackFun):
        threading.Thread.__init__(self)

        self.image = np.copy(image)
        self.callback = callBackFun
        self.outImage = np.zeros_like(self.image)
        self.start()

    def run(self):
        temp_image = np.copy(self.image)
        temp_image = 255 - temp_image

        gray_image = cv2.cvtColor(temp_image, cv2.COLOR_BGR2GRAY)

        _, contours, hierarchy = cv2.findContours(gray_image, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
        outlist = self.getContourByDeep(hierarchy, 1)
        self.callback(True, False, 20)

        outlist.pop(0)
        outlist.pop(0)
        outlistLen = len(outlist)
        if outlistLen > 0:
            for index, contourIndex in enumerate(outlist):
                cv2.drawContours(self.outImage, contours, contourIndex, (255, 255, 255), thickness=-1)
                self.callback(True, False, int((index/outlistLen)*80) + 20)

        self.callback(True, True, 100)

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
        return self.outImage

if __name__ == "__main__":
    print("hello word!")