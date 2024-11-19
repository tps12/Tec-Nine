from nicegui import app, ui
from nicegui.elements.row import Row
from mainwindowpresenter import MainWindowPresenter

class MainWindow(Row):
    def __init__(self):
        super().__init__()
        MainWindowPresenter(self)

if __name__ in {'__main__', '__mp_main__'}:
    with ui.card().style('width:100%; align-items: normal'):
        MainWindow()
    ui.run(title='Tec-Nine')
