# -*- coding: utf-8 -*-
# @Time    : 2020/1/15 18:22
# @Author  : zwenc
# @Email   : zwence@163.com
# @File    : MarbleInfomation.py

import cv2
import numpy
import matplotlib.pyplot as plt

class contactsPoint():
    def __init__(self):
        pass

class MarbleInfomation():
    def __init__(self):
        self.blockDiam = []                # 石料面积                        完成
        self.contactsNum = 0               # 接触点数量（每两个石块之间只算一次接触）  完成
        self.averageMatches = 0            # 平均匹配数  接触点数量/总石块数量        预完成
        self.MarbleSize = 0                # 石块总面积                        完成
        self.contactsMarbleSize = 0        # 有接触石块面积                     完成
        self.noneContactsMarbleSize = 0    # 无接触石块面积                     完成
        self.parameterA = 0                # 接触石料的总面积/石块总面积         预完成
        self.parameterB = 0                # 无接触石料的总面积/石块总面积       预完成
        self.contactsImageLine = None      # 接触图（线连接图）                 预完成
        self.contactsImageDot = None       # 接触图（点连接图）                有了
        self.contactsVoronoiImage = None   # 接触点Voronoi图                  最后弄
        self.CentroidImage = None
        self.blockCentroidImage = None     # 石块形心连接图                    最后弄

        self.blockNum = 0             # 石块总数                              完成
        self.ContactPointInfo = []    # 接触点位置  计算接触点数量              完成
        self.blocksSize = []          # 记录石块大小                              完成
        self.MarbleImage = None       # 石块图（有最外层边框的那种，用来计算石块大小）  完成，但是遗弃不用
        self.blockImage = None        # 石块图（无最外层边框的那种，用来计算形心）      完成
        self.imageSizeCoef = 1        # 像素与真实值面积比例                          完成
        self.image = None


if __name__ == "__main__":
    print("hello word!")