from climatepresenter import ClimatePresenter
from uiview import UiView

class Climate(UiView):
    def __init__(self, uistack):
        UiView.__init__(self, 'climate.ui', ClimatePresenter, uistack)
