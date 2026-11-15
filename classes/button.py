from collections.abc import Callable

import pygame


class Button:
    def __init__(self, image, x_pos, y_pos, text, on_click: Callable[[], None]):
        self.image = pygame.image.load(image).convert_alpha()
        self.image.set_alpha(100)
        self.rect = self.image.get_rect(center=(x_pos, y_pos))
        self.text = text
        self.font = pygame.font.Font(None, 32)
        self.on_click = on_click

    def handle_event(self, event) -> bool:
        clicked = (
            event.type == pygame.MOUSEBUTTONDOWN
            and event.button == 1
            and self.rect.collidepoint(event.pos)
        )
        if clicked:
            self.on_click()
        return clicked

    def draw(self, surface):
        surface.blit(self.image, self.rect)
        color = "green" if self.rect.collidepoint(pygame.mouse.get_pos()) else "white"
        rendered_text = self.font.render(self.text, True, color)
        text_rect = rendered_text.get_rect(center=self.rect.center)
        surface.blit(rendered_text, text_rect)
