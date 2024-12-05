import pygame as pg
import bucket
import level

class hud:

    def __init__(self,things,x,y):
        self.level = level.Level()
        self.font = pg.font.SysFont(None, 36)
        self.things = things
        self.x = x
        self.y = y 
        


    def set_up(self):
        text_surface = self.font.render(self.things, True, (255, 255, 255))
        return text_surface
            
         
