from racinationpresenter import RacinationPresenter
from uiview import UiView

class Racination(UiView):
    def __init__(self, uistack):
        UiView.__init__(self, 'racination.ui', RacinationPresenter, uistack)
