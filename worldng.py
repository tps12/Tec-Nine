from world import World
import color

from nicegui import ui

with ui.card().style('width:100%; align-items: normal'):
    #view = WorldDisplay(model, print)
    #view.aspect = 1
    def rotate_view(event):
      view.rotate = event.value
    #rotate = ui.slider(min=-180, max=180, value=-90, on_change=rotate_view)
    w = World([])

ui.run(port=8082)
