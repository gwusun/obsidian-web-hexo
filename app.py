import os
import subprocess
import sys

from PyQt6.QtCore import QTimer
from PyQt6.QtGui import QGuiApplication
from PyQt6.QtWidgets import *

os.chdir("/Users/sunwu/SW-Research/hexo-websit")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    screen = QGuiApplication.primaryScreen().geometry()  # 获取屏幕类并调用geometry()方法获取屏幕大小
    screen_width = screen.width()  # 获取屏幕的宽
    screen_height = screen.height()  # 获取屏幕的高

    pipe = subprocess.Popen("make d",
                            shell=True,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)

    text_area = QPlainTextEdit()
    text_area.resize(int(screen_width * 0.8), int(screen_height * 0.8))
    text_area.show()


    def run(pipe, text_area):
        text = pipe.stdout.readline()
        text_area.appendPlainText(str(text).replace("b", ""))


    timer = QTimer()
    # fun1是监听的函数，如果fun1(x,y)带参，则使用"lambda:fun1(x,y)" 代替下面的“fun1”
    timer.timeout.connect(lambda: run(pipe, text_area))
    timer.start(1)

    sys.exit(app.exec())
