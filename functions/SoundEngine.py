import os
from random import random
import sys
from pathlib import Path

import pygame
import numpy as np

try:
    from ..dhtypes.soundTypes import SoundEvent, Strength, Track
    from ..sounds.sound_effect_dict import sound_effects
except ImportError:
    project_root = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(project_root.parent))
    os.chdir(project_root)
    pygame.init()
    pygame.mixer.init()
    from Durhack2026.dhtypes.soundTypes import SoundEvent, Strength, Track
    from Durhack2026.sounds.sound_effect_dict import sound_effects

metronome_sound: pygame.mixer.Sound = pygame.mixer.Sound(
    "./sounds/metronome/freesoundMetronome.mp3"
)

SCALE_FACTOR: int = 1000 # Adjust this factor to scale the impulse to [0.0, 1.0]
VOLUME_FLOOR: float = 0.15 # Minimum volume level
IMPULSE_REJECTION_THRESHOLD: float = 40 # Impulses below this value are ignored

def get_scale_factor() -> int:
    return SCALE_FACTOR

def get_strength_from_impulse(impulse: float) -> Strength:
    """Get the strength category based on the impulse value."""
    return min(Strength, key=lambda strength: abs(strength.value - impulse))

def play_sound_from_params(type: str, instrument: int,
    impulse: float = 0.0) -> None:
    if impulse < IMPULSE_REJECTION_THRESHOLD:
        print(f"Ignored impulse {impulse} for {type} instrument {instrument} (below threshold).")
        return
    impulse = max(0.0, min(1.0, impulse / SCALE_FACTOR))  # Clamp impulse to [0.0, 1.0]
    if type not in sound_effects:
        return
    else:
        instrument_sound_array: dict[Strength, pygame.mixer.Sound] | None = sound_effects[type][instrument]
        if instrument_sound_array is None:
            return
        strength = min(
            instrument_sound_array,
            key=lambda available_strength: abs(available_strength.value - impulse),
        )
        sound: pygame.mixer.Sound = instrument_sound_array[strength]
        sound.set_volume(VOLUME_FLOOR + (impulse * (1.0 - VOLUME_FLOOR)))
        sound.play()
        print(f"Playing sound: {type}, instrument: {instrument}, strength: {strength.name}, normalised impulse: {impulse:.2f}, volume: {sound.get_volume():.2f}")
        
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

def check_audio_difference(
    target: np.ndarray,
    recorded: np.ndarray,
    sample_rate: int | None = None,
    bpm: float = 120.0,
    subdivisions_per_beat: int = 4,
    activity_threshold: float = 0.2,
    timing_tolerance: float | None = None,
) -> float:
    """Return a beat-pattern difference score from 0.0 to 1.0.

    The score combines timing, volume, and spectral timbre. Missing and
    additional detected hits receive a score of zero.
    """
    if bpm <= 0:
        raise ValueError("BPM must be greater than zero.")
    if subdivisions_per_beat <= 0:
        raise ValueError("Subdivisions per beat must be greater than zero.")
    if not 0.0 <= activity_threshold <= 1.0:
        raise ValueError("Activity threshold must be between zero and one.")

    if sample_rate is None:
        mixer_settings = pygame.mixer.get_init()
        if mixer_settings is None:
            raise RuntimeError(
                "The Pygame mixer must be initialized when sample_rate is omitted."
            )
        sample_rate = mixer_settings[0]

    if target.ndim not in (1, 2) or recorded.ndim not in (1, 2):
        raise ValueError("Audio arrays must be one- or two-dimensional.")

    def to_mono(audio: np.ndarray) -> np.ndarray:
        if audio.ndim == 1:
            return audio.astype(np.float64)
        return audio.astype(np.float64).mean(axis=1)

    target_mono = to_mono(target)
    recorded_mono = to_mono(recorded)
    subdivision_samples = max(
        1,
        round(sample_rate * 60.0 / bpm / subdivisions_per_beat),
    )
    subdivision_duration = subdivision_samples / sample_rate
    timing_limit = timing_tolerance or subdivision_duration
    slot_count = max(
        1,
        int(
            np.ceil(
                max(len(target_mono), len(recorded_mono))
                / subdivision_samples
            )
        ),
    )

    def get_features(
        audio: np.ndarray,
    ) -> tuple[np.ndarray, np.ndarray, np.ndarray, float]:
        energies = np.zeros(slot_count) 
        timing_offsets = np.zeros(slot_count)
        spectra = np.zeros((slot_count, subdivision_samples // 2 + 1))

        for slot in range(slot_count):
            start = slot * subdivision_samples
            section = audio[start:start + subdivision_samples]
            if len(section) == 0:
                continue

            padded = np.zeros(subdivision_samples)
            padded[:len(section)] = section
            absolute = np.abs(padded)
            energy = np.sqrt(np.mean(padded**2))
            energies[slot] = energy

            if energy > 0:
                timing_offsets[slot] = (
                    np.average(
                        np.arange(subdivision_samples),
                        weights=absolute,
                    )
                    / sample_rate
                )

            windowed = padded * np.hanning(subdivision_samples)
            spectrum = np.abs(np.fft.rfft(windowed))
            spectrum_norm = np.linalg.norm(spectrum)
            if spectrum_norm > 0:
                spectra[slot] = spectrum / spectrum_norm

        return energies, timing_offsets, spectra, np.max(energies)

    target_energy, target_timing, target_spectra, target_max = get_features(
        target_mono
    )
    recorded_energy, recorded_timing, recorded_spectra, recorded_max = get_features(
        recorded_mono
    )

    target_hits = np.flatnonzero(
        target_energy >= target_max * activity_threshold
    ) if target_max > 0 else np.array([], dtype=int)
    recorded_hits = np.flatnonzero(
        recorded_energy >= recorded_max * activity_threshold
    ) if recorded_max > 0 else np.array([], dtype=int)

    unmatched_recorded = set(recorded_hits.tolist())
    matched_scores: list[float] = []
    volume_tolerance_db = 12.0

    for target_slot in target_hits:
        if not unmatched_recorded:
            break

        recorded_slot = min(
            unmatched_recorded,
            key=lambda slot: abs(slot - target_slot),
        )
        timing_difference = abs(
            (recorded_slot - target_slot) * subdivision_duration
            + recorded_timing[recorded_slot]
            - target_timing[target_slot]
        )

        if timing_difference > timing_limit:
            continue

        unmatched_recorded.remove(recorded_slot)
        timing_score = np.exp(-timing_difference / timing_limit)

        target_db = 20.0 * np.log10(max(target_energy[target_slot], 1e-12))
        recorded_db = 20.0 * np.log10(max(recorded_energy[recorded_slot], 1e-12))
        volume_score = np.exp(
            -abs(target_db - recorded_db) / volume_tolerance_db
        )

        timbre_similarity = float(
            np.dot(
                target_spectra[target_slot],
                recorded_spectra[recorded_slot],
            )
        )
        timbre_score = np.clip((timbre_similarity + 1.0) / 2.0, 0.0, 1.0)

        matched_scores.append(
            0.40 * timing_score
            + 0.25 * volume_score
            + 0.35 * timbre_score
        )

    total_hits = max(len(target_hits), len(recorded_hits))
    if total_hits == 0:
        return 0.0

    difference = 1.0 - (sum(matched_scores) / total_hits)
    if np.isclose(difference, 0.0):
        return 0.0
    return float(np.clip(difference, 0.0, 1.0))

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
    sound_events = [(beat / 4.0 + random() * 0.5 - 0.25, event) for beat, event in sound_events]

    return Track(name="Random Track", bpm=bpm, sound_events=sound_events)

def get_two_random_tracks_as_arrays(bpm: int, track_length_beats: int) -> tuple[np.ndarray, np.ndarray]:
    """Generate two random tracks and return their audio arrays."""
    track1 = generate_random_track(bpm, track_length_beats)
    track2 = generate_random_track(bpm, track_length_beats)

    array1 = get_nparray_from_track(track1)
    array2 = get_nparray_from_track(track2)
    
    if array1.shape[0] < array2.shape[0]:
        array2 = array2[:array1.shape[0]]
    elif array1.shape[0] > array2.shape[0]:
        array1 = array1[:array2.shape[0]]

    return array1, array2