import pygame

def play_sound_from_params(velocity: float, type: str, 
    sound_effects: dict[str, dict[float, pygame.mixer.Sound]], pitch: float = 1.0) -> None:
    if type not in sound_effects:
        return
    else:
        closest_velocity = min(sound_effects[type].keys(), key=lambda v: abs(v - velocity))
        sound_effects[type][closest_velocity].play()