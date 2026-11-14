import pygame,pymunk

def create_ball(space): # static body
    body = pymunk.Body(1,100,body_type=pymunk.Body.STATIC)
    body.position = (400, 600)
    shape = pymunk.Circle(body, 80) # edit later to be more specific
    space.add(body, shape)
    return shape

def draw_ball(screen, ball):
    pos = int(ball.body.position.x), int(ball.body.position.y)
    pygame.draw.circle(screen, (255, 255, 255), pos, int(ball.radius))