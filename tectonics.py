from tectonicspresenter import TectonicsPresenter
from uiview import UiView

class Tectonics(UiView):
    def __init__(self, uistack):
        UiView.__init__(self, 'tectonics.ui', TectonicsPresenter, uistack)
