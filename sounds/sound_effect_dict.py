import pygame

from ..types.soundTypes import Strength

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