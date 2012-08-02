from holespresenter import HolesPresenter
from uiview import UiView

class Holes(UiView):
    def __init__(self, uistack):
        UiView.__init__(self, 'holes.ui', HolesPresenter, uistack)
