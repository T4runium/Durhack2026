from pathlib import Path

import pygame


PROJECT_ROOT = Path(__file__).parent
VELOCITIES_TO_TEST = (0.0, 0.5, 1.0)
PAUSE_BETWEEN_SOUNDS_MS = 750


def main() -> None:
    pygame.init()
    pygame.mixer.init()

    # SoundEngine uses paths relative to the project root.
    import os

    os.chdir(PROJECT_ROOT)
    from functions.SoundEngine import (
        Strength,
        get_strength_from_velocity,
        play_sound_from_params,
        sound_effects,
    )

    try:
        expected_strengths = {
            0.0: Strength.SOFT,
            0.5: Strength.MEDIUM,
            1.0: Strength.HARD,
        }
        for velocity, expected_strength in expected_strengths.items():
            actual_strength = get_strength_from_velocity(velocity)
            assert actual_strength is expected_strength, (
                f"Velocity {velocity} mapped to {actual_strength}, "
                f"expected {expected_strength}"
            )

        print("Velocity mapping passed.")
        print("Playing configured sounds...")
        print("Press Ctrl+C to stop.")

        for sound_type, instruments in sound_effects.items():
            for instrument, available_sounds in instruments.items():
                if available_sounds is None:
                    continue

                for velocity in VELOCITIES_TO_TEST:
                    strength = get_strength_from_velocity(velocity)
                    print(
                        f"{sound_type} instrument {instrument}: "
                        f"velocity {velocity} -> {strength.name}"
                    )
                    play_sound_from_params(sound_type, instrument, velocity)
                    pygame.time.delay(PAUSE_BETWEEN_SOUNDS_MS)
    finally:
        pygame.mixer.stop()
        pygame.quit()


if __name__ == "__main__":
    main()
