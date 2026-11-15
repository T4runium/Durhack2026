from collections.abc import Callable
from functions.soundDictionary import _SOUND_BY_DRUM_TYPE

import pygame


class Button:
    def __init__(self, image, hover_image, x_pos, y_pos, text, on_click: Callable[[], None], drum_type=None):
        self.default_image = pygame.transform.scale_by(
            pygame.image.load(image).convert_alpha(), 0.5
        )
        self.hover_image = pygame.transform.scale_by(
            pygame.image.load(hover_image).convert_alpha(), 0.5
        )
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

            from functions.SoundEngine import play_sound_from_params

            if self.drum_type is not None:
                instrument, _ = _SOUND_BY_DRUM_TYPE[self.drum_type]
                play_sound_from_params("drums1", instrument, 1000)

            else:
                play_sound_from_params("ui", 1, 1000)
    
        return clicked

    def draw(
        self,
        surface: pygame.Surface,
        alpha: float = 1.0,
        offset: tuple[int, int] = (0, 0),
    ) -> None:
        color = "green" if self.rect.collidepoint(pygame.mouse.get_pos()) else "white"
        self.image = self.hover_image if self.rect.collidepoint(pygame.mouse.get_pos()) else self.default_image
        image = self.image.copy()
        image.set_alpha(round((image.get_alpha() or 255) * alpha))
        draw_rect = self.rect.move(offset)
        surface.blit(image, draw_rect)
        rendered_text = self.font.render(self.text, True, color)
        rendered_text.set_alpha(round(255 * alpha))
        text_rect = rendered_text.get_rect(center=draw_rect.center)
        surface.blit(rendered_text, text_rect)