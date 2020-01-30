# -*- coding: utf-8 -*-
# @Time    : 2020/1/5 21:48
# @Author  : zwenc
# @Email   : zwence@163.com
# @File    : imageBinaryzation.py

import cv2
import threading

class imageBZ(threading.Thread):
    def __init__(self, image, blockSize, threshold, callBackFun):
        threading.Thread.__init__(self)

        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        self.image = image
        self.blockSize = blockSize
        self.c = threshold           # 自适应均值之后，阀值相差为threshold，为二值化
        self.callback = callBackFun
        self.outImage = image
        self.start()

    def run(self):
        self.outImage = cv2.adaptiveThreshold(self.image, 255,
                                     cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                     cv2.THRESH_BINARY, self.blockSize, self.c)

        self.callback(True, True, 100)

    def getOutImage(self):
        return self.outImage


# 这里是功能测试区，已经废弃
def callBackTestFun(ret, state, count):
    if ret:
        print("BZ finished")
    else:
        print("BZ failed")

if __name__ == "__main__":
    testFilePath = "../image/test.jpg"
    image = cv2.imread(testFilePath)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    imageBZ(image, callBackTestFun)
    print("safd")
