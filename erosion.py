from erosionpresenter import ErosionPresenter
from uiview import UiView

class Erosion(UiView):
    def __init__(self, uistack):
        UiView.__init__(self, 'erosion.ui', ErosionPresenter, uistack)
