from sys import argv, exit
from PySide.QtGui import QApplication, QFont, QFontMetrics, QX11Info
from mainwindow import MainWindow

app = QApplication(argv)
font = QFont(QApplication.font())
font.setPointSize(9)
QApplication.setFont(font)
w = MainWindow()
metrics = QFontMetrics(font)
w.resize(metrics.width('M') * 80, metrics.height() * 24)
w.show()
exit(app.exec_())
