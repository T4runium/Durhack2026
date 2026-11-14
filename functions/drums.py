import pygame,pymunk

class Drumkit(pygame.sprite.Sprite):
    def __init__(self, space, pos, shape_size=(100, 100), collision_type=0):
        super().__init__()
        self.image = pygame.image.load("graphics/bass.png").convert_alpha()
        self.rect = self.image.get_rect(center=(pos))
        self.space = space
        self.pos = pos
        self.shape_size = shape_size  # Default size for the drumkit shape
        self.clicked = False
        self.space.collision_type = collision_type  # Default collision type, can be overridden in subclasses
        self.create_drum()
        
    def create_drum(self):
        self.body = pymunk.Body(1,100,body_type=pymunk.Body.STATIC)
        self.body.position = self.pos
        self.shape = pymunk.Poly.create_box(self.body, self.shape_size)
        self.shape.elasticity = 1
        self.shape.collision_type = self.space.collision_type
        self.space.add(self.body, self.shape)

    def mouse_input(self):
        mouse_pos = pygame.mouse.get_pos()
        if self.rect.collidepoint(mouse_pos) and pygame.mouse.get_pressed()[0]:
            self.clicked = True
        
        if self.clicked:
            self.mouse_move(mouse_pos)

    def mouse_move(self, mouse_pos):
        if self.clicked:
            if not self.rect.collidepoint(mouse_pos) and pygame.mouse.get_pressed()[0]:
                self.body.position = mouse_pos
                self.space.reindex_shapes_for_body(self.body)
                self.clicked = False

    def update(self):
        # Update the drumkit's position based on physics simulation
        self.rect.center = round(self.body.position.x), round(self.body.position.y)
        self.mouse_input()

class Cymbal(Drumkit):
    def __init__(self, space, pos, shape_size=(223, 33), collision_type=2):
        super().__init__(space, pos, shape_size, collision_type)
        self.image = pygame.image.load("graphics/cymbal.png").convert_alpha()
        self.rect = self.image.get_rect(center=(pos))

class Snare(Drumkit):
    def __init__(self, space, pos, shape_size=(204, 70), collision_type=3):
        super().__init__(space, pos, shape_size, collision_type)
        self.image = pygame.image.load("graphics/snare.png").convert_alpha()
        self.rect = self.image.get_rect(center=(pos))

class Bass(Drumkit):
    def __init__(self, space, pos, shape_size=(202, 112), collision_type=4):
        super().__init__(space, pos, shape_size, collision_type)
        self.image = pygame.image.load("graphics/bass.png").convert_alpha()
        self.rect = self.image.get_rect(center=(pos))

class Kick(Drumkit):
    def __init__(self, space, pos, shape_size=(204, 70), collision_type=5):
        super().__init__(space, pos, shape_size, collision_type)
        self.image = pygame.image.load("graphics/kick.png").convert_alpha()
        self.rect = self.image.get_rect(center=(pos))

def create_drums(space: pymunk.Space) -> pygame.sprite.Group:
    return pygame.sprite.Group(
        Cymbal(space, (200, 600)),
        Snare(space, (500, 600)),
        Bass(space, (800, 600)),
        Kick(space, (1100, 600))
    )