from mainmenu import MainMenu

class MainWindowPresenter(object):
    def __init__(self, view):
        self._view = view
        with self._view:
            self._menu = MainMenu(self.push, self.pop)

    def push(self, add_child):
        self._menu.set_visibility(False)
        with self._view:
            self._child = add_child()

    def pop(self):
        self._view.remove(self._child)
        self._menu.set_visibility(True)
