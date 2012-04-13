from splitpresenter import SplitPresenter
from uiview import UiView

class Split(UiView):
    def __init__(self, uistack):
        UiView.__init__(self, 'split.ui', SplitPresenter, uistack)
