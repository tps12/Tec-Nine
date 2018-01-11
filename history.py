from PySide.QtGui import QTreeWidgetItem
from historypresenter import HistoryPresenter
from uiview import UiView

class History(UiView):
    def __init__(self, uistack):
        UiView.__init__(self, 'history.ui', HistoryPresenter, uistack, QTreeWidgetItem)
        self.ui.details.setColumnCount(0)
        self.ui.details.setHeaderLabels(['Selection'])
