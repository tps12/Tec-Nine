from populationpresenter import PopulationPresenter
from uiview import UiView

class Population(UiView):
    def __init__(self, uistack):
        UiView.__init__(self, 'population.ui', PopulationPresenter, uistack)
