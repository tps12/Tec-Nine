from options import Options
from tectonics import Tectonics
from split import Split
from move import Move

class MainMenuPresenter(object):
    def __init__(self, view, uistack):
        self._view = view
        self._view.start.clicked.connect(self.start)
        self._view.split.clicked.connect(self.split)
        self._view.movepoints.clicked.connect(self.move)
        self._view.options.clicked.connect(self.options)
        self._view.exit.clicked.connect(self.exit)
        self._uistack = uistack

    def exit(self):
        self._uistack.pop()

    def start(self):
        self._uistack.push(Tectonics(self._uistack))

    def split(self):
        self._uistack.push(Split(self._uistack))

    def move(self):
        self._uistack.push(Move(self._uistack))

    def options(self):
        self._uistack.push(Options(self._uistack))
