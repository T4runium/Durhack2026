from collections.abc import Callable
from functions.soundDictionary import _SOUND_BY_DRUM_TYPE

import pygame


class Button:
    def __init__(self, image, hover_image, x_pos, y_pos, text, on_click: Callable[[], None], drum_type=None):
        self.default_image = pygame.image.load(image).convert_alpha()
        self.hover_image = pygame.image.load(hover_image).convert_alpha()
        self.image = self.default_image
        self.image.set_alpha(100)
        self.rect = self.image.get_rect(center=(x_pos, y_pos))
        self.text = text
        self.font = pygame.font.Font(None, 32)
        self.on_click = on_click
        self.drum_type = drum_type

    def handle_event(self, event) -> bool:
        clicked = (
            event.type == pygame.MOUSEBUTTONDOWN
            and event.button == 1
            and self.rect.collidepoint(event.pos)
        )
        if clicked:
            self.on_click()
    
            instrument, label = _SOUND_BY_DRUM_TYPE[self.drum_type]
            impulse = 1000
            from functions.SoundEngine import play_sound_from_params
            play_sound_from_params("drums1", instrument, impulse)

        return clicked

    def draw(self, surface):
        surface.blit(self.image, self.rect)
        color = "green" if self.rect.collidepoint(pygame.mouse.get_pos()) else "white"
        self.image = self.hover_image if self.rect.collidepoint(pygame.mouse.get_pos()) else self.default_image
        rendered_text = self.font.render(self.text, True, color)
        text_rect = rendered_text.get_rect(center=self.rect.center)
        surface.blit(rendered_text, text_rect)