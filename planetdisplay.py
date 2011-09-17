from math import sin, cos, pi

import pygame
from pygame.locals import *

def redbluescale(v):
    r = 255 - 255 * v 
    b = 255 * v
    return r, 0, b

def colorscale(v):
    m = 1275
    r = (255 - m * v if v < 0.2 else
         0 if v < 0.6 else
         m * (v - 0.6) if v < 0.8 else
         255)
    g = (0 if v < 0.2 else
         m * (v - 0.2) if v < 0.4 else
         255 if v < 0.8 else
         255 - m * (v - 0.8))
    b = (255 if v < 0.4 else
         255 - m * (v - 0.4) if v < 0.6 else
         0)
    return r, g, b

def warmscale(v):
    m = 510
    r = 255
    g = v * m if v < 0.5 else 255
    b = 0 if v < 0.5 else m * (v - 0.5)
    return r, g, b

def coolscale(v):
    m = 1020
    r = 255 - m * v if v < 0.25 else 0
    g = (255 if v < 0.75 else
         255 - m * (v - 0.75))
    b = (255 - m * v if v < 0.25 else
         m * (v - 0.25) if v < 0.5 else
         255)
    return r, g, b

class PlanetDisplay(object):
    dt = 0.01
    
    def __init__(self, sim):
        self._sim = sim
        self._screen = None
        self.selected = None
        self.dirty = True

    @property
    def rotate(self):
        return self._rotate

    @rotate.setter
    def rotate(self, value):
        self._rotate = value
        self._dirty = True
    
    def handle(self, e):
        if e.type == MOUSEBUTTONUP:
            mx, my = e.pos

            res = max([len(r) for r in self._sim.tiles]), len(self._sim.tiles)

            y = my / (self.size[1]/res[1])
            x = mx / (self.size[0]/res[0]) - (res[0] - len(self._sim.tiles[y]))/2

            r = self.rotate
            o = r * len(self._sim.tiles[y])/360

            xo = x + o
            if xo > len(self._sim.tiles[y])-1:
                xo -= len(self._sim.tiles[y])
            elif xo < 0:
                xo += len(self._sim.tiles[y])
            
            if 0 <= y < len(self._sim.tiles) and 0 <= xo < len(self._sim.tiles[y]):
                if self.selected == (xo,y):
                    self.selected = None
                else:
                    self.selected = (xo,y)
       
                self._dirty = True

                return True

        return False
    
    def draw(self, surface):
        self._sim.update()
        
        if (self._sim.dirty or self._dirty or
            self._screen == None or self._screen.get_size() != surface.get_size()):
            self._screen = pygame.Surface(surface.get_size(), 0, 32)
            
            self.size = self._screen.get_size()
        
            self._screen.fill((0,0,0))

            res = max([len(r) for r in self._sim.tiles]), len(self._sim.tiles)
            template = pygame.Surface((self.size[0]/res[0],
                                       self.size[1]/res[1]), 0, 32)

            for y in range(res[1]):
                for x in range(len(self._sim.tiles[y])):
                    block = template.copy()

                    r = self.rotate
                    o = r * len(self._sim.tiles[y])/360

                    xo = x + o
                    if xo > len(self._sim.tiles[y])-1:
                        xo -= len(self._sim.tiles[y])
                    elif xo < 0:
                        xo += len(self._sim.tiles[y])
                    h = self._sim.tiles[y][xo][2]

                    if self.selected == (xo,y):
                        color = (255, 255, 0)
                    elif h > 0:
                        value = 255 - 25 * h
                        color = (value, value, value)
                    else:
                        color = (255, 255, 255)
                    block.fill(color)
                   
                    self._screen.blit(block,
                                      ((x + (res[0] - len(self._sim.tiles[y]))/2)*block.get_width(),
                                       y*block.get_height()))

            self._dirty = False
                    
        surface.blit(self._screen, (0,0))
