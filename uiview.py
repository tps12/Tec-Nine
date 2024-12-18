from PySide6.QtWidgets import QWidget, QGridLayout
from PySide6.QtUiTools import QUiLoader

class UiView(QWidget):
    def __init__(self, uifile, presenterclass, *presenterargs):
        QWidget.__init__(self)
        self.ui = QUiLoader().load(uifile)
        self.setLayout(QGridLayout())
        self.layout().addWidget(self.ui)
        self._presenter = presenterclass(self.ui, *presenterargs)
