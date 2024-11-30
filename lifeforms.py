from nicegui import app, ui
from nicegui.elements.row import Row
from lifeformspresenter import LifeformsPresenter

class Lifeforms(Row):
    def __init__(self, on_done):
        super().__init__()

        with self.style('align-items: normal').classes('flex-grow'):
            with ui.column().style('align-items: normal').classes('flex-grow'):
                with ui.row().style('align-items: normal').classes('flex-grow'):
                    self.content = ui.element('div').style('display: flex').classes('world-content flex-grow')
                    with ui.scroll_area().style('width: 300px'):
                        with ui.column():
                            ui.label('Selection')
                            self.details = ui.list()
                with ui.row():
                    self.rotate = ui.slider(min=-180, max=180, value=-90)
                    self.attribute = ui.select(dict(enumerate(['Life', 'Animals', 'Plants'])), value=0)
                with ui.row():
                    ui.label('Season:')
                    self.season = ui.slider(min=0, max=100)
                with ui.row():
                    ui.label('Glaciation:')
                    self.glaciation = ui.slider(min=0, max=100, value=50)
            with ui.column():
                self.load = ui.button('Load...')
                self.done = ui.button('Done')
        LifeformsPresenter(self, on_done)

if __name__ in {'__main__', '__mp_main__'}:
    with ui.card().style('width:100%; align-items: normal'):
        Lifeforms(app.shutdown)
    ui.run(title='Flora and Fauna Simulation')
