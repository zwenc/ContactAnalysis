# -*- coding: utf-8 -*-
# @Time    : 2020/1/22 21:04
# @Author  : zwenc
# @Email   : zwence@163.com
# @File    : aaaa.py

from operator import itemgetter


class contactsLinePointInfo(object):
    """
    线接触点信息，记录所有满足条件的点
    """

    def __init__(self):
        self.PointInfo = []

    def appand(self, index1, index2, point1, point2, dis):
        """
        index1: 石块1
        index2: 接触的石块2
        point1: 接触点中心x坐标
        point1: 接触点中心y坐标
        dis: 半径
        """
        if len(self.PointInfo) == 0:
            self.PointInfo.append(TowBlocksContactsInfo(index1, index2, point1, point2, dis))
            return

            # 查找 index1和index2是否已经存在
        for towBlocksContactsInfo in self.PointInfo:
            if towBlocksContactsInfo.compareIndex(index1, index2):
                # 存在，则在里面加点
                towBlocksContactsInfo.append(point1, point2, dis)
                return

        # 不存在，则new一个两个石块接触信息
        self.PointInfo.append(TowBlocksContactsInfo(index1, index2, point1, point2, dis))

    def __len__(self):
        return len(self.PointInfo)

    def __getitem__(self, item):
        return self.PointInfo[item]


# 将两个石块最小记录的最小单位
class TowBlocksContactsInfo(object):
    def __init__(self, index1, index2, point1, point2, dis):
        self.index1 = index1
        self.index2 = index2

        self.pointInfo = [point1, point2, dis]

    def append(self, point1, point2, dis):
        self.pointInfo.append([point1, point2, dis])

    def compareIndex(self, index1, index2):
        if self.index1 == index1 and self.index2 == index2:
            return True

        if self.index2 == index1 and self.index1 == index2:
            return True

        return False

    def getCoordinateByMiddle(self):
        # 根据坐标，将中间的点作为接触点位置返回

        self.pointInfo.sort(key=itemgetter(0))

        index = int(len(self.pointInfo) / 2)

        return self.pointInfo[index]

    def getCoordinateByMinDis(self):
        # 根据距离返回接触点位置
        self.pointInfo.sort(key=itemgetter(2))

        return self.pointInfo[0]

    def __len__(self):
        return len(self.pointInfo)

    def __getitem__(self, item):
        return self.pointInfo[item]
