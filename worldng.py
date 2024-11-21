from worlddisplay import WorldDisplay
from worldsimulation import WorldSimulation
import color

from nicegui import ui

with ui.card():
    model = WorldSimulation(2100, 5, 24, 23, 29, 3, 3, 3)
    view = WorldDisplay(model, print)
    view.aspect = 1
    def rotate_view(event):
      view.rotate = event.value
    rotate = ui.slider(min=-180, max=180, value=-90, on_change=rotate_view)

ui.run(port=8082)
