import pygame,pymunk

class Drumkit(pygame.sprite.Sprite):
    def __init__(self, space, pos, shape_size=(100, 100), collision_type=0):
        super().__init__()
        self.image = pygame.image.load("graphics/bass.png").convert_alpha()
        self.rect = self.image.get_rect(center=(pos))
        self.space = space
        self.pos = pos
        self.shape_size = shape_size  # Default size for the drumkit shape
        self.space.collision_type = collision_type  # Default collision type, can be overridden in subclasses
        self.create_drum()
        
    def create_drum(self):
        self.body = pymunk.Body(1,100,body_type=pymunk.Body.STATIC)
        self.body.position = self.pos
        self.shape = pymunk.Poly.create_box(self.body, self.shape_size)
        self.shape.elasticity = 1
        self.shape.collision_type = self.space.collision_type
        self.space.add(self.body, self.shape)

    def update(self):
        # Update the drumkit's position based on physics simulation
        self.rect.center = round(self.body.position.x), round(self.body.position.y)

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

def create_cymbal(space: pymunk.Space, group: pygame.sprite.Group) -> None:
    group.add(
        Cymbal(space, (200, 600))
    )

def create_snare(space: pymunk.Space, group: pygame.sprite.Group) -> None:
    group.add(
        Snare(space, (500, 600)),
    )

def create_bass(space: pymunk.Space, group: pygame.sprite.Group) -> None:
    group.add(
        Bass(space, (800, 600)),
    )

def create_kick(space: pymunk.Space, group: pygame.sprite.Group) -> None:
    group.add(
        Kick(space, (1100, 600))
    )

def create_all(space: pymunk.Space) -> pygame.sprite.Group:
    drums = pygame.sprite.Group()
    create_cymbal(space, drums)
    create_snare(space, drums)
    create_bass(space, drums)
    create_kick(space, drums)
    return drums
