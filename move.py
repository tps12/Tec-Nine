from movepresenter import MovePresenter
from uiview import UiView

class Move(UiView):
    def __init__(self, uistack):
        UiView.__init__(self, 'move.ui', MovePresenter, uistack)
