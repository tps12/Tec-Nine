from mainmenupresenter import MainMenuPresenter
from uiview import UiView

class MainMenu(UiView):
    def __init__(self, uistack):
        UiView.__init__(self, 'mainmenu.ui', MainMenuPresenter, uistack)
