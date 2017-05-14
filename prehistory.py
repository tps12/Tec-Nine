from prehistorypresenter import PrehistoryPresenter
from uiview import UiView

class Prehistory(UiView):
    def __init__(self, uistack):
        UiView.__init__(self, 'prehistory.ui', PrehistoryPresenter, uistack)
