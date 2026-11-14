import pymunk
import pygame
"""
SizeOfDrumStick : tuple = (20,5)
BorderSize : tuple = (300,400)


def Create_DrumStick(Space : pymunk.Space , Coordinates : tuple):
    global SizeOfDrumStick
    
    Body = pymunk.Body(1,100)
    Body.position = (100,300)


    Shape = pymunk.Poly.create_box(Body , SizeOfDrumStick )


    Space.add(Body , Shape)
    return Shape


def CreateSegments(Space : pymunk.Space , Point1 : tuple , Point2 : tuple):
    Segment = pymunk.Segment(Space.static_body , Point1 , Point2 )



class DrumStick:

    Shape : pymunk.Shape

    def __init__(self , Space : pymunk.Shape , Coordinates : tuple):
        self.Shape = Create_DrumStick(Space , Coordinates)

    def Show_DrumStick(self, Window : pygame.surface):
        global SizeOfDrumStick
        
        ShapeToWindow = pygame.Rect(int(self.Shape.body.position.x) , int(self.Shape.body.position.y) , SizeOfDrumStick[0] , SizeOfDrumStick[1])

        ShapeToWindow.center = (int(SizeOfDrumStick[0] / 2) , int(SizeOfDrumStick[1] / 2))

        pygame.draw.rect(Window , (255,255,255) , ShapeToWindow )

    def RemoveDrumStick(self , Space : pymunk.Space):
        Space.remove(self.Body,self.Shape)
"""

DrumStick_size = (10,10)

def Create_DrumStick(Space : pymunk.Space):
    global DrumStick_size

    body = pymunk.Body(1, 1, body_type= pymunk.Body.DYNAMIC )
    
    body.position = (400,0)

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
        self.image = pygame.image.load("graphics/bass.png").convert_alpha()
        self.rect = self.image.get_rect(center=((DrumStick_size)))
        self.shape.collision_type = 1

    def update(self):
        # Update the drumkit's position based on physics simulation
        self.rect.center = round(self.shape.body.position.x), round(self.shape.body.position.y)

        


def CreateDrumStick(Space : pymunk.Space):
    return pygame.sprite.Group( DrumStick(Space) )
    




    


    