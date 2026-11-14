import pygame,pymunk

class Drumkit(pygame.sprite.Sprite):
    def __init__(self, space, pos):
        super().__init__()
        self.image = pygame.image.load("graphics/drumkit.png").convert_alpha()
        self.rect = self.image.get_rect(center=(pos))
        self.space = space
        self.pos = pos
        self.shape_size = (100,100)  # Default size for the drumkit shape
        self.create_drum()
        
    def create_drum(self):
        self.body = pymunk.Body(1,100,body_type=pymunk.Body.STATIC)
        self.body.position = self.pos
        self.shape = pymunk.Poly.create_box(self.body, self.shape_size)
        self.space.add(self.body, self.shape)

    def update(self):
        # Update the drumkit's position based on physics simulation
        self.rect.center = round(self.body.position.x), round(self.body.position.y)

class Cymbal(Drumkit):
    def __init__(self, space, pos):
        super().__init__(space, pos)
        self.image = pygame.image.load("graphics/cymbal.png").convert_alpha()
        self.rect = self.image.get_rect(center=(pos))
        self.shape_size = (100, 100)

class Snare(Drumkit):
    def __init__(self, space, pos):
        super().__init__(space, pos)
        self.image = pygame.image.load("graphics/snare.png").convert_alpha()
        self.rect = self.image.get_rect(center=(pos))
        self.shape_size = (100, 100)

class Bass(Drumkit):
    def __init__(self, space, pos):
        super().__init__(space, pos)
        self.image = pygame.image.load("graphics/bass.png").convert_alpha()
        self.rect = self.image.get_rect(center=(pos))
        self.shape_size = (100, 100)


    # def check_collision(self, ball):
    #     for drum in self.drums:
    #         if drum.shape.point_query(ball.position).distance < 0:
    #             return True
    #     return False