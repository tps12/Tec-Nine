from sys import argv, exit
from PySide.QtGui import QApplication, QFont, QFontMetrics, QX11Info
from mainwindow import MainWindow

app = QApplication(argv)
#QX11Info.setAppDpiX(0, 139)
#QX11Info.setAppDpiY(0, 144)
font = QFont(QApplication.font())
font.setPointSize(9)
QApplication.setFont(font)
w = MainWindow()
metrics = QFontMetrics(font)
w.setFixedSize(metrics.width('M') * 80, metrics.height() * 25)
w.show()
exit(app.exec_())
