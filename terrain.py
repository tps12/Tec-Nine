from terrainpresenter import TerrainPresenter
from uiview import UiView

class Terrain(UiView):
    def __init__(self, uistack):
        UiView.__init__(self, 'terrain.ui', TerrainPresenter, uistack)
