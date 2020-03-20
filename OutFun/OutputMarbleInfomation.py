# -*- coding: utf-8 -*-
# @Time    : 2020/1/15 23:03
# @Author  : zwenc
# @Email   : zwence@163.com
# @File    : OutputMarbleInfomation.py

import cv2
import numpy as np
import threading
import random
import networkx
from OutFun.MarbleInfomation import MarbleInfomation


class OutputInfo(threading.Thread):
    def __init__(self, marbleinformation, callBackFun):
        threading.Thread.__init__(self)

        self.marbleinformation = marbleinformation  # type: MarbleInfomation
        self.callBackFun = callBackFun

        self.contactsBlockInfo = []  # 接触点连接的两个石块下表
        self.contactsPoints = []
        self.blocksSize = self.marbleinformation.blocksSize
        self.start()

    def run(self):
        self.CalcContactsNum()
        self.callBackFun(True, False, 1)

        self.CalcContactBlocksSize()
        self.callBackFun(True, False, 2)

        self.printblockSize()
        self.callBackFun(True, False, 3)

        self.printMarbleinfo()
        self.callBackFun(True, False, 4)

        self.disContactsImageLine()
        self.callBackFun(True, False, 5)

        self.disContactsImageDot()
        self.callBackFun(True, False, 6)

        self.disVoronoiImage()
        self.callBackFun(True, False, 7)

        self.disBlockCentroidImage()
        self.connectGraph()
        self.callBackFun(True, False, 8)

    def disContactsImageLine(self):
        """
        显示线连接图
        """
        temp = np.copy(self.marbleinformation.image)
        for x, y, dis, index1, index2 in self.marbleinformation.ContactPointInfo:
            cv2.circle(temp, (x, y), dis, [0, 0, 255], thickness=-1)

        self.marbleinformation.contactsImageLine = np.copy(temp)

    def disContactsImageDot(self):
        """
        显示点连接图
        """
        temp = np.copy(self.marbleinformation.image)
        for x, y, dis, _ , _ in self.contactsPoints:
            cv2.circle(temp, (x, y), dis, [0, 0, 255], thickness=-1)

        self.marbleinformation.contactsImageDot = np.copy(temp)

    def disVoronoiImage(self):
        """
        显示Voronoi
        """
        img = np.zeros_like(self.marbleinformation.image)
        size = self.marbleinformation.image.shape
        rect = (0, 0, size[1], size[0])
        subdiv = cv2.Subdiv2D(rect)
        for x, y, _, _, _ in self.contactsPoints:
            subdiv.insert((x, y))

        (facets, centers) = subdiv.getVoronoiFacetList([])

        for i in range(0, len(facets)):
            ifacet_arr = []
            for f in facets[i]:
                ifacet_arr.append(f)

                ifacet = np.array(ifacet_arr, np.int)
                color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

                cv2.fillConvexPoly(img, ifacet, color)
                ifacets = np.array([ifacet])
                cv2.polylines(img, ifacets, True, (0, 0, 0), thickness=1)
                cv2.circle(img, (centers[i][0], centers[i][1]), 3, (0, 0, 0), thickness=-1)

        self.marbleinformation.contactsVoronoiImage = np.copy(img)

    def drawCross(self, image, point, color, size, thickness):
        cv2.line(image, (int(point[0] - size / 2), point[1]), (int(point[0] + size / 2), point[1]), color,
                 thickness=thickness)
        cv2.line(image, (point[0], int(point[1] - size / 2)), (point[0], int(point[1] + size / 2)), color,
                 thickness=thickness)

    def disBlockCentroidImage(self):
        CentroidImage = np.copy(self.marbleinformation.blockImage)
        CentroidConnectImage = np.zeros_like(self.marbleinformation.blockImage)

        im_gray = cv2.cvtColor(self.marbleinformation.blockImage, cv2.COLOR_RGB2GRAY)
        _, thresh = cv2.threshold(im_gray, 128, 255, cv2.THRESH_BINARY)

        retval, labels, stats, centroids = cv2.connectedComponentsWithStats(thresh)
        size = self.marbleinformation.image.shape
        rect = (0, 0, size[1], size[0])
        subdiv = cv2.Subdiv2D(rect)

        for index in range(centroids.shape[0]):
            x, y = centroids[index]
            if index == 0:
                continue

            self.drawCross(CentroidImage, (int(x), int(y)), (0, 0, 255), 4, 1)
            subdiv.insert((x, y))

        triangleList = subdiv.getTriangleList()

        for t in triangleList:
            pt1 = (t[0], t[1])
            pt2 = (t[2], t[3])
            pt3 = (t[4], t[5])
            if self.rect_contains(rect, pt1) and self.rect_contains(rect, pt2) and self.rect_contains(rect, pt3):
                cv2.line(CentroidConnectImage, pt1, pt2, [255, 255, 255], thickness=2)
                cv2.line(CentroidConnectImage, pt2, pt3, [255, 255, 255], thickness=2)
                cv2.line(CentroidConnectImage, pt3, pt1, [255, 255, 255], thickness=2)

        self.marbleinformation.CentroidImage = np.copy(CentroidImage)
        self.marbleinformation.blockCentroidImage = np.copy(CentroidConnectImage)

    def printblockSize(self):
        outFile = open("OutDir/blockSize.txt", mode="w+")

        outFile.write("块大小：\n")
        for index, blockSize in self.marbleinformation.blocksSize:
            outFile.write(str(index) + ": " +
                          str(round(blockSize * self.marbleinformation.imageSizeCoef, 3)) +
                          " mm2 \n")

        outFile.close()

    def printMarbleinfo(self):
        outFile = open("OutDir/Marbleinfor.txt", mode="w+")
        outFile.write("接触点数量：" + str(self.marbleinformation.contactsNum) + "\n")
        outFile.write(
            "平均匹配数: " + str(round(self.marbleinformation.contactsNum / self.marbleinformation.blockNum, 2)) + "\n")
        outFile.write(
            "石块总面积: " + str(
                round(self.marbleinformation.MarbleSize * self.marbleinformation.imageSizeCoef, 2)) + " mm2 \n")
        outFile.write("有接触石块面积: " + str(
            round(self.marbleinformation.contactsMarbleSize * self.marbleinformation.imageSizeCoef, 2)) + " mm2 \n")
        outFile.write("无接触石块面积: " + str(
            round(self.marbleinformation.noneContactsMarbleSize * self.marbleinformation.imageSizeCoef, 2)) + " mm2 \n")
        outFile.write("参数A(接触石料的总面积/石块总面积): " + str(
            round(self.marbleinformation.contactsMarbleSize / self.marbleinformation.MarbleSize * 100, 2)) + " % \n")
        outFile.write("参数B(无接触石料的总面积/石块总面积): " + str(
            round(self.marbleinformation.noneContactsMarbleSize / self.marbleinformation.MarbleSize * 100,
                  2)) + " % \n")

    def CalcContactsNum(self):
        """
        计算接触点数量
        储存接触点
        """
        count = 0

        for x, y, dis, index1, index2 in self.marbleinformation.ContactPointInfo:
            if [index1, index2] in self.contactsBlockInfo:
                continue
            elif [index2, index1] in self.contactsBlockInfo:
                continue
            else:
                self.contactsBlockInfo.append([index1, index2])
                self.contactsPoints.append([x, y, dis,index1,index2])
                count = count + 1

        self.marbleinformation.contactsNum = count

    def getBlockSize(self, index):

        for idx, BlockSize in self.blocksSize:
            if idx == index:
                return BlockSize

        return 0

    def CalcContactBlocksSize(self):
        """
        有接触的石块的面积
        无接触的石块面积
        石块总数
        """
        temp = []

        for index1, index2 in self.contactsBlockInfo:
            if index1 not in temp:
                temp.append(index1)

            if index2 not in temp:
                temp.append(index2)

        contactsallSize = 0
        for index in temp:
            contactsallSize = contactsallSize + self.getBlockSize(index)

        allBlockSize = 0
        for index, blockSize in self.marbleinformation.blocksSize:
            allBlockSize = allBlockSize + blockSize

        self.marbleinformation.blockNum = len(self.marbleinformation.blocksSize)  # 石块总数
        self.marbleinformation.contactsMarbleSize = contactsallSize  # 有接触石块面积
        self.marbleinformation.noneContactsMarbleSize = allBlockSize - contactsallSize  # 无接触石块面积

    def connectGraph(self):
        connectImage = np.copy(self.marbleinformation.blockImage)
        G = networkx.Graph()
        edges = []
        for x, y, dis, index1 , index2 in self.contactsPoints:
            edges.append((index1,index2,1))

        G.add_weighted_edges_from(edges)

        G = networkx.minimum_spanning_tree(G, algorithm='kruskal')

        for index1, index2, _ in G.edges(data=True):
            contour1 = self.marbleinformation.contourInfo[index1 - 1]
            M = cv2.moments(contour1)  # 求矩
            point1 = (int(M['m10'] / M['m00']), int(M['m01'] / M['m00']))

            contour1 = self.marbleinformation.contourInfo[index2 - 1]
            M = cv2.moments(contour1)  # 求矩
            point2 = (int(M['m10'] / M['m00']), int(M['m01'] / M['m00']))

            cv2.line(connectImage, point1, point2, [0, 0, 255], thickness=2)

        self.marbleinformation.miniConnectTree = np.copy(connectImage)













    def rect_contains(self, rect, point):
        if point[0] < rect[0]:
            return False
        elif point[1] < rect[1]:
            return False
        elif point[0] > rect[2]:
            return False
        elif point[1] > rect[3]:
            return False
        return True


if __name__ == "__main__":
    print("hello word!")
