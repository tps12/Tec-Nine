from mainwindowpresenter import MainWindowPresenter
from uiview import UiView

class MainWindow(UiView):
    def __init__(self):
        UiView.__init__(self, 'mainwindow.ui', MainWindowPresenter)

