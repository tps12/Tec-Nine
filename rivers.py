from riverspresenter import RiversPresenter
from uiview import UiView

class Rivers(UiView):
    def __init__(self, uistack):
        UiView.__init__(self, 'rivers.ui', RiversPresenter, uistack)
