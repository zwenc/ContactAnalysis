# -*- coding: utf-8 -*-
# @Time    : 2020/1/13 13:33
# @Author  : zwenc
# @Email   : zwence@163.com
# @File    : imageCalcContacts.py

import cv2
import numpy as np
import threading
import matplotlib.pyplot as plt


class imageCalcContacts(threading.Thread):
    def __init__(self, image, maxArea, blocksize, callBackFun):
        threading.Thread.__init__(self)

        self.image = np.copy(image)
        self.maxArea = maxArea
        self.callback = callBackFun
        self.blockNum = 0
        self.ContactPointInfo = []
        self.blocksSize = []
        self.blocksize = blocksize

        self.start()

    def generateMasker(self, contour):
        masker = np.zeros_like(self.image)

        for contourIndex, contrs in enumerate(contour):
            if cv2.contourArea(contrs) < self.blocksize:
                continue
            # 对每一个块进行编码
            x1 = int((contourIndex + 1) / (256 * 256))
            x2 = int(((contourIndex + 1) - 256 * 256 * x1) / 256)
            x3 = int((contourIndex + 1) - 256 * 256 * x1 - 256 * x2)
            cv2.drawContours(masker, contour, contourIndex, (x1, x2, x3), thickness=1)

        return masker

    def generateCircular(self, coordinate, r):
        a = coordinate[0]
        b = coordinate[1]

        theta = np.arange(0, 2 * np.pi, 0.01)

        x = a + r * np.cos(theta)
        y = b + r * np.sin(theta)

        # x 坐标转化为整型
        x_1 = np.zeros_like(x)
        for index in range(x.size):
            temp = int(x[index])
            if x[index] > (temp + 0.5):
                x_1[index] = int(temp) + 1
            else:
                x_1[index] = int(temp)

            if x_1[index] < 0:
                x_1[index] = 0

        # y 坐标转化为整型
        y_1 = np.zeros_like(y)
        for index in range(y.size):
            temp = int(y[index])
            if y[index] > (temp + 0.5):
                y_1[index] = int(temp) + 1
            else:
                y_1[index] = int(temp)

            if y_1[index] < 0:
                x_1[index] = 0

        # 去掉重复的点
        coordinates = []
        coordinate = [0, 0]
        for index in range(x_1.size):
            temp = [x_1[index], y_1[index]]
            if coordinate == temp:
                continue

            coordinates.append(temp)
            coordinate = temp

        return coordinates

    def calcDistance(self, masker, index, coordinate, maxR):
        """
        masker : 模板
        coordinate： 当前坐标（本函数就是求该坐标距离最近的白色点的距离）
        maxR： 在这个半径内查找（可以降低计算量）
        """

        distance = np.inf
        minDistanceCoordinate = coordinate  # 如果没有找到，则返回原坐标
        ret = False  # 按照半径进行查找，找到则直接退出
        returnIndex = 0

        for r in range(1, maxR):
            coordinates = self.generateCircular(coordinate, r)
            for x, y in coordinates:
                if x < 0 or y < 0 or x >= masker.shape[1] or y >= masker.shape[0]:
                    continue

                x_1, x_2, x_3 = masker[int(y), int(x), :]
                maskIndex = int(x_1 * 256 * 256 + x_2 * 256 + x_3)
                if (int(index) == maskIndex) or (maskIndex == 0):
                    continue

                # self.image[int(y),int(x)] = [0, 255, 0]
                ret = True
                tempDis = np.sqrt(np.power(x - coordinate[0], 2) + np.power(y - coordinate[1], 2))
                if tempDis < distance:
                    returnIndex = maskIndex
                    distance = tempDis
                    minDistanceCoordinate = [x, y]

            if ret:  # 找到直接退出
                break

        return distance, minDistanceCoordinate, returnIndex

    def run(self):
        temp = np.copy(self.image)
        temp_gray = cv2.cvtColor(temp, cv2.COLOR_BGR2GRAY)
        _, contours, hierarchy = cv2.findContours(temp_gray, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)

        masker = self.generateMasker(contours)

        contourslen = len(contours)
        self.blockNum = contourslen
        # 暴力计算距离
        for contourIndex, contrs in enumerate(contours):
            if cv2.contourArea(contrs) < self.blocksize:
                continue
            for crs in contrs:
                x, y = crs[0]
                distance, minDistanceCoordinate, maskIndex = self.calcDistance(masker, contourIndex + 1, (x, y),
                                                                               self.maxArea)
                if maskIndex == 0 or maskIndex == (contourIndex + 1):
                    masker[int(y), int(x)] = [0, 0, 0]  # 找过的点，将不会参与计算
                    self.image[int(y), int(x)] = [0, 255, 0]
                    continue

                MiddleCoordinate = (
                int((x + minDistanceCoordinate[0]) / 2.0), int((y + minDistanceCoordinate[1]) / 2.0))
                # print(minDistanceCoordinate , [x, y])
                dis = int(distance / 2.0)
                if dis == 0:
                    dis = 1

                cv2.circle(self.image, MiddleCoordinate, dis, [0, 0, 255], thickness=-1)
                self.callback(True, False, int(contourIndex * 100 / contourslen))

                self.ContactPointInfo.append([MiddleCoordinate[0], MiddleCoordinate[1],
                                              dis, contourIndex + 1, maskIndex
                                              ])  # 保留每个接触点的信息
                # print((x, y), minDistanceCoordinate)
                # print(contourIndex + 1, maskIndex)

                if x < 0 or y < 0 or x >= masker.shape[0] or y >= masker.shape[1]:
                    continue
                masker[int(y), int(x)] = [0, 0, 0]  # 找过的点，将不会参与计算
                self.image[int(y), int(x)] = [0, 255, 0]
            self.blocksSize.append([contourIndex, cv2.contourArea(contrs)])  # 保存每个石块的大小

        self.callback(True, True, 100)

    def getOutImage(self):
        return self.image

    def getblockNum(self):
        return self.blockNum

    def getContactPointInfo(self):
        return self.ContactPointInfo

    def getBlocksSize(self):
        return self.blocksSize


def callbacktest(ret, state, count):
    pass


if __name__ == "__main__":
    img = cv2.imread("../image/temp1.png")
    aa = imageCalcContacts(img, callbacktest)
