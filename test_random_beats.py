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

import Durhack2026.functions.SoundEngine as SoundEngine

from Durhack2026.dhtypes.soundTypes import Track

def main() -> None:
    
    random_track: Track = SoundEngine.generate_random_track(120, 1024)
    random_track2: Track = SoundEngine.generate_random_track(120, 1024)
    
    random_array: np.ndarray = SoundEngine.get_nparray_from_track(random_track)
    random_array2: np.ndarray = SoundEngine.get_nparray_from_track(random_track2)
    
    if random_array.shape[0] < random_array2.shape[0]:
        random_array2 = random_array2[:random_array.shape[0]]
    elif random_array.shape[0] > random_array2.shape[0]:
        random_array = random_array[:random_array2.shape[0]]
    
    print(SoundEngine.check_audio_difference(
        random_array, random_array2
    ))
    
    pygame.mixer.stop()
    pygame.quit()
    
if __name__ == "__main__":
    main()