import pygame,pymunk

class Drumkit(pygame.sprite.Sprite):
    def __init__(self, space, pos, sound_files=None):
        super().__init__()
        self.image = pygame.image.load("graphics/drumkit.png").convert_alpha()
        self.rect = self.image.get_rect(center=(pos))
        self.space = space
        self.pos = pos
        self.create_drum()
        
    def create_drum(self):
        self.body = pymunk.Body(1,100,body_type=pymunk.Body.STATIC)
        self.body.position = self.pos
        self.shape = pymunk.Poly.create_box(self.body, (100, 100))
        self.space.add(self.body, self.shape)

    def update(self):
        # Update the drumkit's position based on physics simulation
        self.rect.center = round(self.body.position.x), round(self.body.position.y)

    # def check_collision(self, ball):
    #     for drum in self.drums:
    #         if drum.shape.point_query(ball.position).distance < 0:
    #             return True
    #     return False