import os
import sys
from pathlib import Path

import numpy as np
import pygame

PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT.parent))
os.chdir(PROJECT_ROOT)

pygame.init()
pygame.mixer.init()

from Durhack2026.functions import SoundEngine
from Durhack2026.levels import Chp1
from Durhack2026.types.soundTypes import Track

def main() -> None:
    try:
        chp1_level1: Track = Chp1.levels[0]
        sim_array: np.ndarray = SoundEngine.get_nparray_from_track(chp1_level1)
        print(f"Generated audio array with shape {sim_array.shape}.")
        print(sim_array)
        SoundEngine.play_sound_from_npdarray(sim_array)

        clock = pygame.time.Clock()
        while pygame.mixer.get_busy():
            clock.tick(60)
            
        sim_array2: np.ndarray = SoundEngine.get_nparray_from_track(Chp1.levels[1])
        print(f"Generated audio array with shape {sim_array2.shape}.")
        print(sim_array2)
        print(SoundEngine.check_audio_difference(sim_array, sim_array2))
    finally:
        pygame.mixer.stop()
        pygame.quit()


if __name__ == "__main__":
    main()
