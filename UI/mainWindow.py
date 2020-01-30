# -*- coding: utf-8 -*-
# @Time    : 2020/1/5 21:21
# @Author  : zwenc
# @Email   : zwence@163.com
# @File    : mainWindow.py

from UI.UImainWindow import Ui_MainWindow
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QInputDialog, QMessageBox
from PyQt5 import QtGui
from PyQt5.QtCore import pyqtSignal
import sys
import os
import numpy as np
import matplotlib.pyplot as plt

# 各种图像处理文件
import cv2
from library.imageBinaryzation import imageBZ
from library.imageRemoveOuterArea import imageROuterArea
from library.imageRemoveNoise import imageRNoise
from library.imageCannys import imageCannys
from library.imageRemoveSmallArea import imageRSmallArea
from library.imageWatershed import imageWatershed
from library.imageGetEdgeAndNum import imageGetEdgeAndNum
from library.imageCalcContacts import imageCalcContacts

# 输出信息
from OutFun.MarbleInfomation import MarbleInfomation
from OutFun.OutputMarbleInfomation import OutputInfo

logoPath = "image/logo.png"  # 兼容从 main.py 启动， 目录能够对应上
if __name__ == "__main__":
    logoPath = "../image/logo.png"

class mainw(QMainWindow, Ui_MainWindow):
    BZSignal = pyqtSignal(bool, bool, int)
    disImageSignal = pyqtSignal()
    removeOuterAreaSignal = pyqtSignal(bool, bool, int)
    removeNoiseSignal = pyqtSignal(bool, bool, int)
    cannysSignal = pyqtSignal(bool, bool, int)
    removeSmallAreaSignal = pyqtSignal(bool, bool, int)
    WatershedSignal = pyqtSignal(bool, bool, int)
    EdgeAndNumSignal = pyqtSignal(bool, bool, int)
    calcContactsSignal = pyqtSignal(bool, bool, int)
    outputParmSignal = pyqtSignal(bool, bool, int)

    def __init__(self):
        super(mainw, self).__init__()
        self.setupUi(self)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(logoPath), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.setWindowTitle("沥青混合料细观结构分析")
        self.setWindowIcon(icon)

        self.BZSignal.connect(self.BinaryzationDisplay)
        self.disImageSignal.connect(self.ImageDisplay)
        self.removeOuterAreaSignal.connect(self.ROuterAreaDisplay)
        self.removeNoiseSignal.connect(self.RNoiseDisplay)
        self.cannysSignal.connect(self.CannysDispaly)
        self.removeSmallAreaSignal.connect(self.RSmallAreaDisplay)
        self.WatershedSignal.connect(self.WatershedDisplay)
        self.EdgeAndNumSignal.connect(self.EdgeAndNumDisplay)
        self.calcContactsSignal.connect(self.CalcContactsDisplay)
        self.outputParmSignal.connect(self.OutputSParmDisplay)

        self.pushButtonBackOne.setEnabled(False)

        # 初始化变量
        self.image = None  # 原始图片
        self.currentImage = None  # 当前要处理的图片
        self.displayImage = None  # 显示图片，当确认修改之后，会将显示图片赋值到currentImage中
        self.imageRealSize = [0, 0]
        self.imageSizeCoef = 1
        self.MarbleInfo = MarbleInfomation()
        self.lineCoef = 1.0

    def pushButtonLoadimage(self):
        fileName, fileType = QFileDialog.getOpenFileName(self, "选取文件", os.getcwd(),
                                                         "All Files(*);;Text Files(*.txt)")
        self.imageRealSize[0], okPressed = QInputDialog.getInt(self, "物理尺寸", "高度（单位：mm）:", 150, 50, 500, 1)
        if okPressed == False:
            return
        self.imageRealSize[1], okPressed = QInputDialog.getInt(self, "物理尺寸", "宽度（单位：mm）:", 150, 50, 500, 1)
        if okPressed == False:
            return

        if fileName == '':
            return

        self.image = cv2.imread(fileName)
        tempSize = self.image.shape  # 计算比例系数使用

        fx = 1.0 / (self.image.shape[0] / self.imageDis.height())
        fy = 1.0 / (self.image.shape[1] / self.imageDis.width())
        ff = min(fx, fy)
        ff = min(1, ff)
        self.image = cv2.resize(self.image, (0, 0), fx=ff, fy=ff)
        self.currentImage = np.copy(self.image)
        self.displayImage = np.copy(self.image)

        # 计算每个像素对应的真实物理尺寸
        H = int(tempSize[0] * ff)
        W = int(tempSize[1] * ff)
        H_1 = self.imageRealSize[0] / H
        W_1 = self.imageRealSize[1] / W
        self.imageSizeCoef = H_1 * W_1
        self.MarbleInfo.imageSizeCoef = self.imageSizeCoef
        self.lineCoef = min(H_1, W_1)
        self.MarbleInfo.image = np.copy(self.image)

        self.statusBar().showMessage("Load Image: " + fileName + "        imageSizeCoef is " +
                                     str(self.imageSizeCoef) + " mm2", 2000)

        self.disImageSignal.emit()

    def pushButtonBinaryzation(self):
        if isinstance(self.currentImage, type(None)):
            self.statusBar().showMessage("请先导入图片", 2000)
            return
        blockSize, okPressed = QInputDialog.getInt(self, "设定块大小(奇数)", "数值:", 61, 1, 201, 10)
        threshold, okPressed = QInputDialog.getInt(self, "设定阈值  ", "数值:", 10, 1, 255, 2)
        self.statusBar().showMessage("二值化参数：blockSize = " + str(blockSize) + "threshold = " + str(threshold), 1000)

        self.BZProcess = imageBZ(self.image, blockSize, threshold, self.BinaryzationCallback)

    def BinaryzationDisplay(self, ret, state, count):
        """
        ret: 状态，如果为false，则处理失败
        state: 是否处理结束
        count: 处理进度
        """
        self.statusBar().showMessage("处理进度：" + str(count) + "%", 2000)
        if ret == False:
            return

        if state == True and count == 100:
            temp = self.BZProcess.getOutImage()
            self.displayImage[:, :, 0] = temp
            self.displayImage[:, :, 1] = temp
            self.displayImage[:, :, 2] = temp
            self.disImageSignal.emit()

        self.pushButtonBackOne.setEnabled(True)

    def BinaryzationCallback(self, ret, state, count):
        self.BZSignal.emit(ret, state, count)

    def ROuterAreaDisplay(self, ret, state, count):
        self.statusBar().showMessage("处理进度：" + str(count) + "%", 2000)
        if ret == False:
            return

        if state == True and count == 100:
            self.displayImage = self.ROuterArea.getOutImage()
            self.MarbleInfo.MarbleSize = self.ROuterArea.getMaxAreaSize()
            self.disImageSignal.emit()

        self.pushButtonBackOne.setEnabled(True)

    def pushButtonROuterArea(self):
        self.currentImage = np.copy(self.displayImage)

        self.ROuterArea = imageROuterArea(self.currentImage, self.ROuterAreaCallback)

    def ROuterAreaCallback(self, ret, state, count):
        self.removeOuterAreaSignal.emit(ret, state, count)

    def pushButtonBOne(self):  # 返回上一步
        self.displayImage = np.copy(self.currentImage)
        self.pushButtonBackOne.setEnabled(False)
        self.disImageSignal.emit()

    def pushButtonRNoise(self):
        self.currentImage = np.copy(self.displayImage)
        deep, okPressed = QInputDialog.getInt(self, "设置噪声深度", "数值:", 2, 1, 5, 1)
        self.RNoise = imageRNoise(self.currentImage, deep, self.RNoiseCallback)

    def RNoiseCallback(self, ret, state, count):
        self.removeNoiseSignal.emit(ret, state, count)

    def RNoiseDisplay(self, ret, state, count):
        if ret == False:
            return

        self.statusBar().showMessage("处理进度：" + str(count) + "%", 2000)

        self.displayImage = self.RNoise.getOutImage()
        self.disImageSignal.emit()

        self.pushButtonBackOne.setEnabled(True)

    def pushButtonCannys(self):
        self.currentImage = np.copy(self.displayImage)
        self.cannysProcess = imageCannys(self.currentImage, self.CannysCallback)

    def CannysCallback(self, ret, state, count):
        self.cannysSignal.emit(ret, state, count)

    def CannysDispaly(self, ret, state, count):
        if ret == False:
            return
        self.statusBar().showMessage("处理进度：" + str(count) + "%", 2000)

        self.displayImage = self.cannysProcess.getOutImage()
        self.disImageSignal.emit()

        # 可以通过plt对图像放大查看
        plt.imshow(self.displayImage)
        plt.pause(1)

        self.pushButtonBackOne.setEnabled(True)

    def pushButtonWatershed(self):
        self.currentImage = np.copy(self.displayImage)
        self.watershedProcess = imageWatershed(self.currentImage, self.image, self.WatershedCallback)

    def WatershedCallback(self, ret, state, count):
        self.WatershedSignal.emit(ret, state, count)

    def WatershedDisplay(self, ret, state, count):
        if ret == False:
            return
        self.statusBar().showMessage("处理进度：" + str(count) + "%", 2000)

        self.displayImage = self.watershedProcess.getOutImage()
        self.disImageSignal.emit()

        if count == 100:
            self.statusBar().showMessage("注意，红线表示区块分界", 2000)

        # 可以通过plt对图像放大查看
        plt.imshow(self.displayImage[:, :, [2, 1, 0]])
        plt.pause(1)

        self.pushButtonBackOne.setEnabled(True)

    def pushButtonGetEdgeAndNum(self):
        self.currentImage = np.copy(self.displayImage)
        self.currentImage[self.currentImage[:] == 254] = 0
        self.GetEdgeProcess = imageGetEdgeAndNum(self.currentImage, self.EdgeAndNumCallBack)

    def EdgeAndNumCallBack(self, ret, state, count):
        self.EdgeAndNumSignal.emit(ret, state, count)

    def EdgeAndNumDisplay(self, ret, state, count):
        if ret == False:
            return

        self.statusBar().showMessage("处理进度：" + str(count) + "%", 2000)

        self.displayImage = self.GetEdgeProcess.getOutImage()

        self.MarbleInfo.blockImage = np.copy(self.displayImage)           # 保存无边框图片
        self.disImageSignal.emit()
        self.pushButtonBackOne.setEnabled(True)

    def pushButtonCalcContacts(self):
        self.currentImage = np.copy(self.displayImage)
        self.MarbleInfo.blockImage = np.copy(self.displayImage)
        # plt.imshow(self.currentImage[:,:,[2,1,0]])
        #         # plt.pause(1)
        defaultsize = float(self.lineCoef * 5.0)
        size, okPressed = QInputDialog.getDouble(self, "接触半径", "接触半径（单位：mm）:", defaultsize, 1, 200, decimals=3)
        if okPressed == False:
            return
        rsize = int(size / self.lineCoef)
        blocksize, okPressed = QInputDialog.getDouble(self, "目标石块大小", "大小（单位：mm2）:", 4.37, 1, 200, decimals=2)

        if okPressed == False:
            return
        self.calcContactsProcess = imageCalcContacts(self.currentImage, rsize, int(blocksize/self.imageSizeCoef), self.CalcContactsCallBack)

    def CalcContactsCallBack(self, ret, state, count):
        self.calcContactsSignal.emit(ret, state, count)

    def CalcContactsDisplay(self, ret, state, count):
        if ret == False:
            return

        self.statusBar().showMessage("处理进度：" + str(count) + "%", 100000)
        self.displayImage = self.calcContactsProcess.getOutImage()
        self.disImageSignal.emit()

        if count == 100:
            self.MarbleInfo.blockNum = self.calcContactsProcess.getblockNum()
            self.MarbleInfo.blocksSize = self.calcContactsProcess.getBlocksSize()
            self.MarbleInfo.ContactPointInfo = self.calcContactsProcess.getContactPointInfo()
            QMessageBox.information(self,"tips","接触分析完毕", QMessageBox.Yes)

        self.pushButtonBackOne.setEnabled(True)

    def pushButtonOutPutSize(self):
        pass

    def pushButtonRSmallArea(self):
        self.currentImage = np.copy(self.displayImage)
        size, okPressed = QInputDialog.getDouble(self, "移除石块的最大值", "数值（单位：mm）:", 4.37, 1, 200, decimals=2)
        size = int(size / self.imageSizeCoef)
        self.removeSmallAreaProcess = imageRSmallArea(self.currentImage, size, self.RSmallAreaCallback)

    def RSmallAreaCallback(self, ret, state, count):
        self.removeSmallAreaSignal.emit(ret, state, count)

    def RSmallAreaDisplay(self, ret, state, count):
        if ret == False:
            return

        self.statusBar().showMessage("处理进度：" + str(count) + "%", 2000)
        self.displayImage = self.removeSmallAreaProcess.getOutImage()
        self.disImageSignal.emit()

        self.pushButtonBackOne.setEnabled(True)

    def ImageDisplay(self):
        if isinstance(self.displayImage, type(None)):
            self.statusBar().showMessage("请先导入图片", 2000)
            return

        temp = cv2.cvtColor(self.displayImage, cv2.COLOR_BGR2RGB)
        qtImage = QtGui.QImage(temp.data, temp.shape[1],
                               temp.shape[0], temp.shape[1] * 3, QtGui.QImage.Format_RGB888)

        self.imageDis.setPixmap(QtGui.QPixmap(qtImage))

    def pushButtonSaveImage(self):
        cv2.imwrite("temp.png", self.displayImage)
        self.statusBar().showMessage("图片已经保存至：temp.png", 2000)

    def pushButtonOutputParm(self):
        self.outputInfoProcess = OutputInfo(self.MarbleInfo,self.OutputSParmCallback)

    def OutputSParmCallback(self, ret, state, count):
        self.outputParmSignal.emit(ret, state, count)

    def OutputSParmDisplay(self, ret, state, count):
        if ret == False:
            return

        if count == 1:
            self.statusBar().showMessage("1", 2000)
            return

        if count == 2:
            self.statusBar().showMessage("2", 2000)
            return

        if count == 3:
            self.statusBar().showMessage("3", 2000)
            return

        if count == 4:
            self.statusBar().showMessage("4", 2000)
            return

        if count == 5:
            self.statusBar().showMessage("5", 2000)
            plt.figure("线连接图")
            plt.imshow(self.MarbleInfo.contactsImageLine[:, :, [2, 1, 0]])
            cv2.imwrite("OutDir/contactsImageLine.jpg", self.MarbleInfo.contactsImageLine)
            return

        if count == 6:
            self.statusBar().showMessage("6", 2000)
            plt.figure("点连接图")
            plt.imshow(self.MarbleInfo.contactsImageDot[:, :, [2, 1, 0]])
            cv2.imwrite("OutDir/contactsImageDot.jpg", self.MarbleInfo.contactsImageDot)
            return

        if count == 7:
            self.statusBar().showMessage("7", 2000)
            plt.figure("Voronoi图")
            plt.imshow(self.MarbleInfo.contactsVoronoiImage[:, :, [2, 1, 0]])
            cv2.imwrite("OutDir/contactsVoronoiImage.jpg", self.MarbleInfo.contactsVoronoiImage)
            return

        if count == 8:
            self.statusBar().showMessage("8", 2000)
            plt.figure("质心图")
            plt.imshow(self.MarbleInfo.CentroidImage[:, :, [2, 1, 0]])
            cv2.imwrite("OutDir/CentroidImage.jpg", self.MarbleInfo.CentroidImage)

            plt.figure("质心图连接图")
            plt.imshow(self.MarbleInfo.blockCentroidImage[:, :, [2, 1, 0]])
            cv2.imwrite("OutDir/blockCentroidImage.jpg", self.MarbleInfo.blockCentroidImage)
            return




if __name__ == "__main__":
    app = QApplication(sys.argv)  # 必须创建一个应用空间，由它来负责程序的运行和信号的调用
    ex = mainw()  # 创建一个widget
    ex.show()  # 显示
    sys.exit(app.exec_())  # 捕捉程序退出信息
