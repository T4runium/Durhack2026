import pymunk
import pygame

import math

DrumStick_size = (125,50)

def Create_DrumStick(Space : pymunk.Space):
    global DrumStick_size

    body = pymunk.Body(1, 100, body_type= pymunk.Body.DYNAMIC )
    
    body.position = (640,0)

    shape = pymunk.Poly.create_box(body , DrumStick_size )
    shape.elasticity = 1
    Space.add(body , shape)

    return shape





class DrumStick(pygame.sprite.Sprite):
    shape : pymunk.Shape
    
    space : pymunk.Space
    
    def __init__(self , space : pymunk.Space):
        # Create the Physics to it

        global DrumStick_size

        super().__init__()
        
        self.shape = Create_DrumStick(space)
        self.space = space
        
        self.image = pygame.image.load("graphics/drumstick.png").convert_alpha()
        self.originalimage = self.image
        
        self.rect = self.image.get_rect(center=((DrumStick_size)))
        self.shape.collision_type = 1


    def update(self):
        # Update the drumkit's position based on physics simulation

        self.rect.center = round(self.shape.body.position.x), round(self.shape.body.position.y)
        
        self.image = pygame.transform.rotate(self.originalimage , self.shape.body.angle )
        self.rect = self.originalimage.get_rect(center = self.rect.center)
        


def CreateDrumStick(Space : pymunk.Space):
    return pygame.sprite.Group( DrumStick(Space) )
    




    


    