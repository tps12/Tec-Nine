from options import Options
from tectonics import Tectonics

class MainMenuPresenter(object):
    def __init__(self, view, uistack):
        self._view = view
        self._view.start.clicked.connect(self.start)
        self._view.options.clicked.connect(self.options)
        self._view.exit.clicked.connect(self.exit)
        self._uistack = uistack

    def exit(self):
        self._uistack.pop()

    def start(self):
        self._uistack.push(Tectonics(self._uistack))

    def options(self):
        self._uistack.push(Options(self._uistack))
