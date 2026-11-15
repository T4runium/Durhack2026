import pymunk
import pygame

import math

DrumStick_size = (12,181)

def Create_DrumStick(Space : pymunk.Space):
    global DrumStick_size

    body = pymunk.Body(
        2,
        pymunk.moment_for_box(2, DrumStick_size) * 0.4,
        body_type=pymunk.Body.DYNAMIC,
    )
    
    body.position = pygame.mouse.get_pos()

    shape = pymunk.Poly.create_box(body , DrumStick_size )
    shape.elasticity = 1

    
    Space.add(body , shape)

    return shape


def CreateBorder(space : pymunk.Space ,start : tuple , end : tuple):
    body = pymunk.Body(1 , 1 , pymunk.Body.STATIC)
    shape = pymunk.Segment(body , start , end , 1)

    space.add(body,shape)
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
        
        self.image = pygame.transform.rotate(self.originalimage ,-math.degrees(self.shape.body.angle) )
        self.rect = self.image.get_rect(center = self.rect.center)

    

def CreateDrumStick(Space : pymunk.Space):
    return pygame.sprite.Group( DrumStick(Space) )  


class DrumStickDisplay(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()

        self.image = pygame.image.load('graphics/drumstick.png').convert_alpha()

        self.rect = self.image.get_rect(center=((DrumStick_size)))

        self.image.set_alpha(100)

    def update(self):
        mouse_pos = pygame.mouse.get_pos()
        
        if ( pygame.mouse.get_pos()[1] > 300):
            self.image.set_alpha( int(85 - (pygame.mouse.get_pos()[1] - 300) / 4) )
        else:
            self.image.set_alpha(100)
        

        self.rect.center = mouse_pos



def Create_TransparentSource():
    return pygame.sprite.Group( DrumStickDisplay() )    


        


# when it falls down the edge, you should be able to place the drumstick again

    


    