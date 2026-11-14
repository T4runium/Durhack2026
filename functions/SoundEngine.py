import os
import sys
from pathlib import Path

import pygame
import numpy as np

try:
    from ..types.soundTypes import SoundEvent, Strength, Track
    from ..sounds.sound_effect_dict import sound_effects
except ImportError:
    project_root = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(project_root.parent))
    os.chdir(project_root)
    pygame.init()
    pygame.mixer.init()
    from Durhack2026.types.soundTypes import SoundEvent, Strength, Track
    from Durhack2026.sounds.sound_effect_dict import sound_effects

metronome_sound: pygame.mixer.Sound = pygame.mixer.Sound(
    "./sounds/metronome/freesoundMetronome.mp3"
)

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
        strength = min(
            instrument_sound_array,
            key=lambda available_strength: abs(available_strength.value - velocity),
        )
        sound: pygame.mixer.Sound = instrument_sound_array[strength]
        sound.set_volume(0.5 + (velocity * 0.5))
        sound.play()
        
def play_sound_from_track(track: Track, metronome: bool = False) -> None:
    """Play a track in beat order, optionally playing a click on each beat."""
    if pygame.mixer.get_init() is None:
        raise RuntimeError("The Pygame mixer must be initialized before playing sounds.")
    if track.bpm <= 0:
        raise ValueError("Track BPM must be greater than zero.")

    seconds_per_beat = 60.0 / track.bpm
    events = sorted(track.sound_events, key=lambda event: event[0])
    if any(start_beat < 0 for start_beat, _ in events):
        raise ValueError("Sound event beat positions must not be negative.")

    start_time = pygame.time.get_ticks() / 1000.0
    next_event = 0
    next_metronome_beat = 0
    last_event_beat = events[-1][0] if events else -1
    clock = pygame.time.Clock()

    while next_event < len(events):
        elapsed = pygame.time.get_ticks() / 1000.0 - start_time

        if metronome:
            while (
                next_metronome_beat <= last_event_beat
                and next_metronome_beat * seconds_per_beat <= elapsed
            ):
                metronome_sound.play()
                next_metronome_beat += 1

        while (
            next_event < len(events)
            and events[next_event][0] * seconds_per_beat <= elapsed
        ):
            _, event = events[next_event]
            play_sound_from_params(event.type, event.instrument, event.velocity)
            next_event += 1

        clock.tick(120)

    while pygame.mixer.get_busy():
        clock.tick(60)

    
def get_nparray_from_track(
    track: Track
    ) -> np.ndarray:
    """Mix sound events into a NumPy array using the Pygame mixer format."""
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

        start_time = start_beat * seconds_per_beat

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
    
def clip_audio_arrays(arrays: list[np.ndarray], max_time: float):
    mixer_settings = pygame.mixer.get_init()
    if mixer_settings is None:
        raise RuntimeError("The Pygame mixer must be initialized before clipping audio arrays.")
    
    sample_rate, _, _ = mixer_settings
    max_samples = int(max_time * sample_rate)
    return [array[:max_samples] for array in arrays]

def check_audio_difference(array1: np.ndarray, array2: np.ndarray) -> float:
    """Return a difference score from 0.0 to 1.0."""
    if array1.shape != array2.shape:
        raise ValueError("Audio arrays must have the same shape.")

    flat1 = array1.astype(np.float64).ravel()
    flat2 = array2.astype(np.float64).ravel()

    norm1 = np.linalg.norm(flat1)
    norm2 = np.linalg.norm(flat2)

    if norm1 == 0 and norm2 == 0:
        return 0.0
    if norm1 == 0 or norm2 == 0:
        return 1.0

    similarity = np.dot(flat1, flat2) / (norm1 * norm2)
    similarity = np.clip(similarity, -1.0, 1.0)

    return float((1.0 - similarity) / 2.0)

def generate_random_track(bpm: int, track_length_beats: int):
    """Generate a random track with sound events."""
    if bpm <= 0:
        raise ValueError("BPM must be greater than zero.")
    if track_length_beats <= 0:
        raise ValueError("Track length in beats must be greater than zero.")

    sound_types = list(sound_effects.keys())
    instruments = {stype: list(sound_effects[stype].keys()) for stype in sound_types}
    sound_events: list[tuple[float, SoundEvent]] = []

    for beat in range(track_length_beats * 4): # generate quarter beats
        if np.random.rand() < 0.5:
            stype = np.random.choice(sound_types)
            instrument = np.random.choice(instruments[stype])
            velocity = np.random.uniform(0.0, SCALE_FACTOR)
            sound_events.append((float(beat), SoundEvent(stype, instrument, velocity)))
            
    #scale beat to quarter beats
    sound_events = [(beat / 4.0, event) for beat, event in sound_events]

    return Track(name="Random Track", bpm=bpm, sound_events=sound_events)