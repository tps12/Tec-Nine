from mainmenu import MainMenu

class MainWindowPresenter(object):
    def __init__(self, view):
        self._view = view
        self._widgets = []

        m = MainMenu(self)
        self.push(m)

    def setwidget(self, widget):
        layout = self._view.centralwidget.layout()
        if layout.count():
            layout.removeItem(layout.itemAt(0))
        layout.addWidget(widget)

    def push(self, widget):
        if len(self._widgets):
            self._widgets[-1].hide()
        self._widgets.append(widget)
        self.setwidget(widget)

    def replace(self, widget):
        self.pop()
        self.push(widget)

    def pop(self):
        widget = self._widgets.pop()
        widget.setParent(None)
        if len(self._widgets):
            widget = self._widgets[-1]
            widget.show()
            self.setwidget(widget)
        else:
            self._view.parent().close()
