from PySide6.QtWidgets import QTreeWidgetItem
from worldpresenter import WorldPresenter
from uiview import UiView

class World(UiView):
    def __init__(self, uistack):
        UiView.__init__(self, 'world.ui', WorldPresenter, uistack, QTreeWidgetItem)
        self.ui.details.setColumnCount(0)
        self.ui.details.setHeaderLabels(['Selection'])
