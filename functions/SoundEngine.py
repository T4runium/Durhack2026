import pygame
from enum import Enum

class Strength(Enum):
    SOFT = 0.0
    MEDIUM = 0.5
    HARD = 1.0


sound_effects: dict[str, dict[int, dict[Strength, pygame.mixer.Sound] | None]] = {
    "drums1": {
        1: { #Cymbal 
            Strength.SOFT: pygame.mixer.Sound("./sounds/drums1/VHHCymbalTap.wav"),
            Strength.MEDIUM: pygame.mixer.Sound("./sounds/drums1/VHHCymbal.wav")
        },
        2: { #CymbalClosed
            Strength.MEDIUM: pygame.mixer.Sound("./sounds/drums1/VHHCymbalClosed.wav")
        },
        3: { #DrumSmall
            Strength.MEDIUM: pygame.mixer.Sound("./sounds/drums1/VHHDrumSmall.wav")
        },
        4: { #DrumMedium
            Strength.MEDIUM: pygame.mixer.Sound("./sounds/drums1/VHHDrumMedium.wav") 
        },
        5: { #DrumLarge
            Strength.MEDIUM: pygame.mixer.Sound("./sounds/drums1/VHHDrumLarge.wav")
        },
        7: { #Snare
            Strength.MEDIUM: pygame.mixer.Sound("./sounds/drums1/VHHSnareDrumTap.wav"),
            Strength.HARD: pygame.mixer.Sound("./sounds/drums1/VHHSnare.wav")
        },
    }
}

def get_strength_from_velocity(velocity: float) -> Strength:
    """Get the strength category based on the velocity value."""
    return min(Strength, key=lambda strength: abs(strength.value - velocity))

def play_sound_from_params(type: str, instrument: int,
    velocity: float = 0.0) -> None:
    velocity = max(0.0, min(1.0, velocity / 20))  # Clamp velocity to [0.0, 1.0]
    if type not in sound_effects:
        return
    else:
        instrument_sound_array: dict[Strength, pygame.mixer.Sound] | None = sound_effects[type][instrument]
        if instrument_sound_array is None:
            return
        closest_strength: Strength = min(
            instrument_sound_array,
            key=lambda available_strength: abs(available_strength.value - velocity),
        )
        sound: pygame.mixer.Sound = instrument_sound_array[closest_strength]
        sound.set_volume(0.5 + (velocity * 0.5))
        sound.play()
        
