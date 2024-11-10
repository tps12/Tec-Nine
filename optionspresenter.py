from PySide6.QtWidgets import QApplication

class OptionsPresenter(object):
    def __init__(self, view, uistack):
        self._view = view
        self._view.fontBox.currentFontChanged.connect(self.fontchanged)
        self._view.done.clicked.connect(self.done)
        self._uistack = uistack

    def done(self):
        self._uistack.pop()

    def fontchanged(self, font):
        QApplication.setFont(font)
