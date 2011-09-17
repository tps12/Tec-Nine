import pygame, wx

class PygameDisplay(wx.Window):
    def __init__(self, parent, ID, display):
        wx.Window.__init__(self, parent, ID)

        pygame.font.init()
                
        self.display = display

        self.size = self.GetSizeTuple()
        self.size_dirty = True
       
        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_TIMER, self.Update, self.timer)
        self.Bind(wx.EVT_SIZE, self.OnSize)
        self.Bind(wx.EVT_LEFT_UP, self.OnClick)
       
        self.timer.Start(self.display.dt * 1000, False)

    def Update(self, event):
        # Any update tasks would go here (moving sprites, advancing animation frames etc.)        
	self.Redraw()
        wx.Yield()

    def OnClick(self, event):
        self.display.handle(pygame.event.Event(pygame.locals.MOUSEBUTTONUP,
                                               {'button': 1,
                                                'pos': event.Position.Get()}))

    def Redraw(self):
        if self.size_dirty:
            self.screen = pygame.Surface(self.size, 0, 32)
            self.size_dirty = False
	    dirty = True
	else:
	    dirty = self.display.dirty

	if not dirty:
	    return

        self.display.draw(self.screen)

        s = pygame.image.tostring(self.screen, 'RGB')  # Convert the surface to an RGB string
        img = wx.ImageFromData(self.size[0], self.size[1], s)  # Load this string into a wx image
        bmp = wx.BitmapFromImage(img)  # Get the image in bitmap form
        dc = wx.ClientDC(self)  # Device context for drawing the bitmap
        dc.DrawBitmap(bmp, 0, 0, False)  # Blit the bitmap image to the display
        del dc
 
    def OnPaint(self, event):
        self.Redraw()
        event.Skip()  # Make sure the parent frame gets told to redraw as well
 
    def OnSize(self, event):
        self.size = self.GetSizeTuple()
        self.size_dirty = True
 
    def Kill(self, event):
        # Make sure Pygame can't be asked to redraw /before/ quitting by unbinding all methods which
        # call the Redraw() method
        # (Otherwise wx seems to call Draw between quitting Pygame and destroying the frame)
        # This may or may not be necessary now that Pygame is just drawing to surfaces
        self.Unbind(event = wx.EVT_PAINT, handler = self.OnPaint)
        self.Unbind(event = wx.EVT_TIMER, handler = self.Update, source = self.timer)
