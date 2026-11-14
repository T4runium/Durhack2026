import pymunk
from SoundEngine import play

SizeOfDrumStick : tuple = (20,5)

def Create_DrumStick(Space : pymunk.Space , Coordinates : tuple):
    global SizeOfDrumStick
    
    Body = pymunk.Body( mass=3 , moment=10 )
    Body.position = 100,200

    Shape = pymunk.Poly.create_box(Space , SizeOfDrumStick )
    Shape.elasticity = 1
    Shape.mass = 1

    Space.add(Body , Shape)
    return Shape

    


    