from sphereview import SphereView
from worldsimulation import WorldSimulation

from nicegui import ui

with ui.card():
    dt = WorldSimulation.tecdt
    model = WorldSimulation(2100, 4, 24, 23, 29, 3, 3, 3)
    view = SphereView(model.grid.faces)

ui.run(port=8082)
