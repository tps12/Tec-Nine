from nicegui import app, ui
from nicegui.elements.row import Row
from worldpresenter import WorldPresenter

class World(Row):
    def __init__(self, on_done):
        super().__init__(wrap=False)

        with self.classes('flex-grow'):
            with ui.column().classes('flex-grow'):
                with ui.row().classes('flex-grow'):
                    self.content = ui.element('div').style('display: flex').classes('world-content flex-grow')
                    self.details = ui.tree([])
                with ui.row().style('align-self: stretch'):
                    self.rotate = ui.slider(min=-180, max=180, value=-90)
                    self.aspect = ui.select(dict(enumerate(['Climate', 'Color', 'Population'])), value=0)
            with ui.column():
                self.radius = ui.select(dict(enumerate(['very small', 'small', 'medium', 'large', 'very large'])), label='Size', value=2)
                with ui.card():
                    ui.label('Parameters')
                    style = 'min-width: 120px'
                    self.spin = ui.select(dict(enumerate(['8', '12', '24', '48'])), label='Hours in day', value=2).style(style)
                    self.tilt = ui.number(label='Axial tilt', value=23, min=0, max=45, step=1, suffix='°').style(style)
                    self.land = ui.number(label='Land', value=29, min=1, max=50, step=1, suffix='%').style(style)
                    self.atmt = ui.number(label='Atm. Δt', value=125, min=5, max=1000, step=5, suffix='My').style(style)
                    self.lifet = ui.number(label='Life Δt', value=125, min=5, max=1000, step=5, suffix='My').style(style)
                    self.peoplet = ui.number(label='People Δt', value=125, min=5, max=1000, step=5, suffix='My').style(style)
                    self.randomize = ui.checkbox('Randomize')
                self.create_new = ui.button('Create')
                self.start = ui.button('Start')
                self.pause = ui.button('Pause')
                with ui.row():
                    self.years = ui.label('0')
                    ui.label('years')
                with ui.row():
                    self.population = ui.label('0')
                    ui.label('people')
                self.load = ui.button('Load...')
                self.save = ui.button('Save...')
                self.done = ui.button('Done')
        WorldPresenter(self, on_done)

if __name__ in {'__main__', '__mp_main__'}:
    with ui.card().style('width:100%; align-items: normal'):
        World(app.shutdown)
    ui.run(title='World Simulation')
