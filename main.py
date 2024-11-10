from sys import argv, exit
from PySide6.QtGui import QFont, QFontMetrics
from PySide6.QtWidgets import QApplication
from mainwindow import MainWindow

app = QApplication(argv)
font = QFont(QApplication.font())
font.setPointSize(9)
QApplication.setFont(font)
w = MainWindow()
metrics = QFontMetrics(font)
w.resize(metrics.maxWidth() * 80, metrics.height() * 24)
w.show()
exit(app.exec())
