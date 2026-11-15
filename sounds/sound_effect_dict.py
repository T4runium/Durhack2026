import pygame

from ..dhtypes.soundTypes import Strength

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
        6: { #Kick
            Strength.MEDIUM: pygame.mixer.Sound("./sounds/drums1/VHHKick.wav")
        },
        7: { #Snare
            Strength.MEDIUM: pygame.mixer.Sound("./sounds/drums1/VHHSnareDrumTap.wav"),
            Strength.HARD: pygame.mixer.Sound("./sounds/drums1/VHHSnare.wav")
        },
        8: { #Stick
            Strength.MEDIUM: pygame.mixer.Sound("./sounds/drums1/VRBell.wav"),
        }
    },
    "ui": {
        1: { # button
            Strength.MEDIUM: pygame.mixer.Sound("./sounds/SND01_sine/button.wav"),
        },
        2: { # caution
            Strength.MEDIUM: pygame.mixer.Sound("./sounds/SND01_sine/caution.wav"),
        },
        3: { # celebration
            Strength.MEDIUM: pygame.mixer.Sound("./sounds/SND01_sine/celebration.wav"),
        },
        4: { # disabled
            Strength.MEDIUM: pygame.mixer.Sound("./sounds/SND01_sine/disabled.wav"),
        },
        5: { # notification
            Strength.MEDIUM: pygame.mixer.Sound("./sounds/SND01_sine/notification.wav"),
        },
        6: { # progress_loop
            Strength.MEDIUM: pygame.mixer.Sound("./sounds/SND01_sine/progress_loop.wav"),
        },
        7: { # ringtone_loop
            Strength.MEDIUM: pygame.mixer.Sound("./sounds/SND01_sine/ringtone_loop.wav"),
        },
        8: { # select
            Strength.MEDIUM: pygame.mixer.Sound("./sounds/SND01_sine/select.wav"),
        },
        9: { # swipe
            Strength.MEDIUM: pygame.mixer.Sound("./sounds/SND01_sine/swipe.wav"),
        },
        10: { # swipe_01
            Strength.MEDIUM: pygame.mixer.Sound("./sounds/SND01_sine/swipe_01.wav"),
        },
        11: { # swipe_02
            Strength.MEDIUM: pygame.mixer.Sound("./sounds/SND01_sine/swipe_02.wav"),
        },
        12: { # swipe_03
            Strength.MEDIUM: pygame.mixer.Sound("./sounds/SND01_sine/swipe_03.wav"),
        },
        13: { # swipe_04
            Strength.MEDIUM: pygame.mixer.Sound("./sounds/SND01_sine/swipe_04.wav"),
        },
        14: { # swipe_05
            Strength.MEDIUM: pygame.mixer.Sound("./sounds/SND01_sine/swipe_05.wav"),
        },
        15: { # tap_01
            Strength.MEDIUM: pygame.mixer.Sound("./sounds/SND01_sine/tap_01.wav"),
        },
        16: { # tap_02
            Strength.MEDIUM: pygame.mixer.Sound("./sounds/SND01_sine/tap_02.wav"),
        },
        17: { # tap_03
            Strength.MEDIUM: pygame.mixer.Sound("./sounds/SND01_sine/tap_03.wav"),
        },
        18: { # tap_04
            Strength.MEDIUM: pygame.mixer.Sound("./sounds/SND01_sine/tap_04.wav"),
        },
        19: { # tap_05
            Strength.MEDIUM: pygame.mixer.Sound("./sounds/SND01_sine/tap_05.wav"),
        },
        20: { # toggle_off
            Strength.MEDIUM: pygame.mixer.Sound("./sounds/SND01_sine/toggle_off.wav"),
        },
        21: { # toggle_on
            Strength.MEDIUM: pygame.mixer.Sound("./sounds/SND01_sine/toggle_on.wav"),
        },
        22: { # transition_down
            Strength.MEDIUM: pygame.mixer.Sound("./sounds/SND01_sine/transition_down.wav"),
        },
        23: { # transition_up
            Strength.MEDIUM: pygame.mixer.Sound("./sounds/SND01_sine/transition_up.wav"),
        },
        24: { # type_01
            Strength.MEDIUM: pygame.mixer.Sound("./sounds/SND01_sine/type_01.wav"),
        },
        25: { # type_02
            Strength.MEDIUM: pygame.mixer.Sound("./sounds/SND01_sine/type_02.wav"),
        },
        26: { # type_03
            Strength.MEDIUM: pygame.mixer.Sound("./sounds/SND01_sine/type_03.wav"),
        },
        27: { # type_04
            Strength.MEDIUM: pygame.mixer.Sound("./sounds/SND01_sine/type_04.wav"),
        },
        28: { # type_05
            Strength.MEDIUM: pygame.mixer.Sound("./sounds/SND01_sine/type_05.wav"),
        },
    },
}