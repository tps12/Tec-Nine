from PySide6.QtWidgets import QListWidgetItem
from lifeformspresenter import LifeformsPresenter
from uiview import UiView

class Lifeforms(UiView):
    def __init__(self, uistack):
        UiView.__init__(self, 'lifeforms.ui', LifeformsPresenter, uistack, QListWidgetItem)
