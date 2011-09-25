import gettext
gettext.install('dorftris')

from cPickle import dump, load

from math import asin, acos, atan2, pi, exp, sqrt, sin, cos

import wx, pygame
from pygame.locals import *

from planetsimulation import PlanetSimulation
from planetdisplay import PlanetDisplay

from wxpygame import PygameDisplay

def rotation(i):
    return i*10

class SimulationControls(wx.PyPanel):

    def __init__(self, parent, display):
        wx.PyPanel.__init__(self, parent)
        self._display = display

        lines = wx.BoxSizer(wx.VERTICAL)

        self.SetAutoLayout(True)
        self.SetSizer(lines)
        self.Layout()

class DisplayControls(wx.PyPanel):
    def __init__(self, parent, display):
        wx.PyPanel.__init__(self, parent)
        self._display = display

        lines = wx.BoxSizer(wx.VERTICAL)

        rotate = wx.Slider(self, wx.ID_ANY, 0, -18, 18, style=wx.SL_HORIZONTAL)
        self.Bind(wx.EVT_SCROLL, self._onrotate, rotate)
        self._onrotate(wx.ScrollEvent(pos=rotate.Value))
        lines.Add(rotate, flag=wx.EXPAND)

        self.SetAutoLayout(True)
        self.SetSizer(lines)
        self.Layout()
        
    def _onrotate(self, event):
        self._display.rotate = rotation(-event.Position)

class Frame(wx.Frame):
    def __init__(self, parent):
        wx.Frame.__init__(self, parent, -1, size = (1600, 1000))

        self.map = PlanetDisplay(PlanetSimulation(6400, 5))
        self.display = PygameDisplay(self, -1, self.map)
       
        self.Bind(wx.EVT_SIZE, self.OnSize)
        self.Bind(wx.EVT_CLOSE, self.Kill)
       
        self.curframe = 0
       
        self.SetTitle(u'Planet')
              
        self.sizer = wx.BoxSizer(wx.VERTICAL)

        self.sizer.Add(SimulationControls(self, self.map), flag=wx.EXPAND)

        self.sizer.Add(self.display, 1, flag = wx.EXPAND)

        self.sizer.Add(DisplayControls(self, self.map), flag=wx.EXPAND)
       
        self.SetAutoLayout(True)
        self.SetSizer(self.sizer)
        self.Layout()
 
    def Kill(self, event):
        self.display.Kill(event)
        self.Destroy()
 
    def OnSize(self, event):
        self.Layout()
 
class App(wx.App):
    def __init__(self, redirect=True):
        wx.App.__init__(self, redirect)
        
    def OnInit(self):
        self.frame = Frame(parent = None)
        self.frame.Show()
        self.SetTopWindow(self.frame)
       
        return True
 
if __name__ == "__main__":
    app = App(False)
    app.MainLoop()
