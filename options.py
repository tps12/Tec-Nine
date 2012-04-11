from optionspresenter import OptionsPresenter
from uiview import UiView

class Options(UiView):
    def __init__(self, uistack):
        UiView.__init__(self, 'options.ui', OptionsPresenter, uistack)
