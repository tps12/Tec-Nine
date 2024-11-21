from sphereview import SphereView
from worldsimulation import WorldSimulation
import color

from nicegui import ui

selected = None

def select(sim, view, x, y, z):
    global selected
    tile = sim.nearest((z,-x,y)) if abs(z) < 2 else None
    selected = tile if tile is not selected else None
    view.usecolors({ v: tilecolor(t) for (v, t) in model.tiles.items() })

def tilecolor(tile):
    global selected
    if tile is selected:
        return (255,0,0)
    return color.value(tile)

with ui.card():
    model = WorldSimulation(2100, 5, 24, 23, 29, 3, 3, 3)
    view = SphereView(model.grid.faces, on_click=lambda x, y, z: select(model, view, x, y, z))
    view.usecolors({ v: tilecolor(t) for (v, t) in model.tiles.items() })
    rotate = ui.slider(min=-180, max=180, value=-90, on_change=view.rotate)

ui.run(port=8082)
