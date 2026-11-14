import pygame
import numpy as np
from ..types.soundTypes import Strength, Track
from ..sounds.sound_effect_dict import sound_effects

SCALE_FACTOR = 20.0  # Adjust this factor to scale the velocity to [0.0, 1.0]


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
    """Mix sound events into a NumPy array using the Pygame mixer format."""
    mixer_settings = pygame.mixer.get_init()
    if mixer_settings is None:
        raise RuntimeError("The Pygame mixer must be initialized before mixing sounds.")

    sample_rate, _, channels = mixer_settings
    decoded_events: list[tuple[np.ndarray, int, float]] = []
    total_samples = 0

    for start_time, event in track.sound_events:
        if start_time < 0:
            raise ValueError("Sound event start times must not be negative.")

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

def play_sound_from_npdarray(audio_array: np.ndarray) -> None:
    """Play a NumPy array as sound using the Pygame mixer."""
    if audio_array.ndim == 1:
        audio_array = audio_array.reshape(-1, 1)

    channels = audio_array.shape[1]
    mixer_settings = pygame.mixer.get_init()
    if mixer_settings is None:
        raise RuntimeError("The Pygame mixer must be initialized before playing sounds.")

    _, _, mixer_channels = mixer_settings
    if channels != mixer_channels:
        raise ValueError(
            f"Audio array has {channels} channels, but the mixer is set to {mixer_channels} channels."
        )

    sound = pygame.sndarray.make_sound(audio_array)
    sound.play()