from PySide.QtGui import QListWidgetItem
from languagepresenter import LanguagePresenter
from uiview import UiView

class Language(UiView):
    def __init__(self, uistack):
        UiView.__init__(self, 'language.ui', LanguagePresenter, uistack, QListWidgetItem)
