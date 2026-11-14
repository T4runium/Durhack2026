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

def Create_DrumStick(Space : pymunk.Space):
    body = pymunk.Body(1, 10, body_type= pymunk.Body.DYNAMIC )
    body.position = (400,600)

    shape = pymunk.Poly.create_box(body , (100 , 100) )
    Space.add(body , shape)
    return shape


def UpdateDrumStick(Space : pymunk.Space ):
    pass

    




    




    


    