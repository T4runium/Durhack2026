import pygame
import numpy as np
from ..types.soundTypes import Strength, Track

SCALE_FACTOR = 20.0  # Adjust this factor to scale the velocity to [0.0, 1.0]

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
    velocity = max(0.0, min(1.0, velocity / SCALE_FACTOR))  # Clamp velocity to [0.0, 1.0]
    if type not in sound_effects:
        return
    else:
        instrument_sound_array: dict[Strength, pygame.mixer.Sound] | None = sound_effects[type][instrument]
        if instrument_sound_array is None:
            return
        sound: pygame.mixer.Sound = instrument_sound_array[get_strength_from_velocity(velocity)]
        sound.set_volume(0.5 + (velocity * 0.5))
        sound.play()
        
def get_nparray_from_track(
    track: Track
    ) -> np.ndarray:
    """Mix beat-timestamped track events into a NumPy audio array."""
    mixer_settings = pygame.mixer.get_init()
    if mixer_settings is None:
        raise RuntimeError("The Pygame mixer must be initialized before mixing sounds.")
    if track.bpm <= 0:
        raise ValueError("Track BPM must be greater than zero.")

    sample_rate, _, channels = mixer_settings
    decoded_events: list[tuple[np.ndarray, int, float]] = []
    total_samples = 0

    seconds_per_beat = 60.0 / track.bpm

    for start_beat, event in track.sound_events:
        if start_beat < 0:
            raise ValueError("Sound event beat positions must not be negative.")

        instrument_sounds = sound_effects.get(event.type)
        if instrument_sounds is None:
            raise ValueError(f"Unknown sound type: {event.type}")

        sounds_by_strength = instrument_sounds.get(event.instrument)
        if sounds_by_strength is None:
            raise ValueError(
                f"Unknown instrument {event.instrument} for sound type {event.type}"
            )

        velocity = max(0.0, min(1.0, event.velocity / SCALE_FACTOR))
        strength = min(
            sounds_by_strength,
            key=lambda available_strength: abs(available_strength.value - velocity),
        )
        sound = sounds_by_strength[strength]
        samples = np.frombuffer(sound.get_raw(), dtype=np.int16)

        if channels > 1:
            if len(samples) % channels != 0:
                raise ValueError("Sound data does not match the mixer channel count.")
            samples = samples.reshape(-1, channels)
        else:
            samples = samples.reshape(-1, 1)

        start_time = start_beat * seconds_per_beat
        start_sample = int(start_time * sample_rate)
        end_sample = start_sample + len(samples)
        volume = 0.5 + (velocity * 0.5)

        decoded_events.append((samples, start_sample, volume))
        total_samples = max(total_samples, end_sample)

    mixed = np.zeros((total_samples, channels), dtype=np.float64)

    for samples, start_sample, volume in decoded_events:
        end_sample = start_sample + len(samples)
        mixed[start_sample:end_sample] += samples * volume

    return np.clip(mixed, -32768, 32767).astype(np.int16)