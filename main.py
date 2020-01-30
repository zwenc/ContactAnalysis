# -*- coding: utf-8 -*-
# @Time    : 2020/1/5 21:08
# @Author  : zwenc
# @Email   : zwence@163.com
# @File    : main.py

from UI.mainWindow import mainw
from PyQt5.QtWidgets import QApplication
import sys

if __name__ == "__main__":
    app = QApplication(sys.argv)  # 必须创建一个应用空间，由它来负责程序的运行和信号的调用
    ex = mainw()  # 创建一个widget
    ex.show()  # 显示
    sys.exit(app.exec_())  # 捕捉程序退出信息