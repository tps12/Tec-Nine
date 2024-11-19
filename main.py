from nicegui import ui
from mainwindow import MainWindow

with ui.card().style('width:100%; align-items: normal'):
    MainWindow()
ui.run(title='Tec-Nine')
