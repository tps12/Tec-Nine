from nicegui import app, ui
from nicegui.elements.row import Row
from historypresenter import HistoryPresenter

class History(Row):
    def __init__(self, on_done):
        super().__init__(wrap=False)

        with self.classes('flex-grow'):
            with ui.column().classes('flex-grow'):
                self.content = ui.element('div').style('display: flex').classes('world-content flex-grow')
                ui.label('Selection')
                self.details = ui.tree([])
                with ui.row().style('align-self: stretch'):
                    self.rotate = ui.slider(min=-180, max=180, value=-90)
                    self.aspect = ui.select(dict(enumerate(['States', 'Species', 'Population', 'Capacity'])), value=0)
                    self.rivers = ui.checkbox('Rivers')
            with ui.column():
                self.start = ui.button('Start')
                self.pause = ui.button('Pause')
                self.pause.set_visibility(False)
                self.step = ui.button('Step')
                self.phase = ui.label()
                with ui.row():
                    self.ticks = ui.label('0')
                    ui.label('genticks')
                self.load = ui.button('Load...')
                self.save = ui.button('Save...')
                self.done = ui.button('Done')
        HistoryPresenter(self, on_done)

if __name__ in {'__main__', '__mp_main__'}:
    with ui.card().style('width:100%; align-items: normal'):
        History(app.shutdown)
    ui.run(title='History Simulation')
