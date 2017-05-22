from PySide.QtGui import QListWidgetItem
from worldpresenter import WorldPresenter
from uiview import UiView

class World(UiView):
    def __init__(self, uistack):
        UiView.__init__(self, 'world.ui', WorldPresenter, uistack, QListWidgetItem)
