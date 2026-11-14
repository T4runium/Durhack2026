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
        self.shape.elasticity = 1
        self.space.add(self.body, self.shape)

    def mouse_input(self):
        if pygame.mouse.get_pressed()[0] and self.rect.collidepoint(pygame.mouse.get_pos()):
            for drum in self.groups()[0]:  # Assuming all drums are in the same group
                if drum != self and drum.rect.colliderect(self.rect):
                    return  # Prevent moving if colliding with another drumkit
            mouse_pos = pygame.mouse.get_pos()
            self.body.position = mouse_pos
            self.space.reindex_shapes_for_body(self.body)
            self.rect.center = mouse_pos
        

    def update(self):
        # Update the drumkit's position based on physics simulation
        self.rect.center = round(self.body.position.x), round(self.body.position.y)
        self.mouse_input()

class Cymbal(Drumkit):
    def __init__(self, space, pos):
        super().__init__(space, pos)
        self.image = pygame.image.load("graphics/cymbal.png").convert_alpha()
        self.rect = self.image.get_rect(center=(pos))
        self.shape_size = (100, 100)
        self.shape.collision_type = 2

class Snare(Drumkit):
    def __init__(self, space, pos):
        super().__init__(space, pos)
        self.image = pygame.image.load("graphics/snare.png").convert_alpha()
        self.rect = self.image.get_rect(center=(pos))
        self.shape_size = (100, 100)
        self.shape.collision_type = 3

class Bass(Drumkit):
    def __init__(self, space, pos):
        super().__init__(space, pos)
        self.image = pygame.image.load("graphics/bass.png").convert_alpha()
        self.rect = self.image.get_rect(center=(pos))
        self.shape_size = (100, 100)
        self.shape.collision_type = 4

class Kick(Drumkit):
    def __init__(self, space, pos):
        super().__init__(space, pos)
        self.image = pygame.image.load("graphics/kick.png").convert_alpha()
        self.rect = self.image.get_rect(center=(pos))
        self.shape_size = (100, 100)
        self.shape.collision_type = 5

def create_drums(space: pymunk.Space) -> pygame.sprite.Group:
    return pygame.sprite.Group(
        Cymbal(space, (600, 600)),
        # Snare(space, (400, 400)),
        Bass(space, (200, 600)),
    )