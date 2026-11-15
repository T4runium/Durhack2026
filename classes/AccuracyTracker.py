import math
import numpy as np
from ..functions import SoundEngine
from ..dhtypes.soundTypes import SoundEvent, Track


class AccuracyTracker:
    """Track timing, volume, and instrument accuracy for a performance."""

    def __init__(self, target_track: Track, bpm: float) -> None:
        if bpm <= 0:
            raise ValueError("BPM must be greater than zero.")

        self.target_track: Track = target_track
        self.target_events: list[tuple[float, SoundEvent]] = list(
            target_track.sound_events
        )
        self.bpm: float = bpm
        self.matched_targets: set[int] = set()
        self.scores: list[float] = []
        self.extra_hits: int = 0

    def register_hit(
        self,
        beat: float,
        instrument: int,
        impulse: float,
    ) -> None:
        """Register one player hit and update the running accuracy."""
        candidates = [
            (index, target_beat, event)
            for index, (target_beat, event) in enumerate(self.target_events)
            if index not in self.matched_targets
            and event.instrument == instrument
        ]

        if not candidates:
            self.extra_hits += 1
            return

        target_index, target_beat, target_event = min(
            candidates,
            key=lambda item: abs(item[1] - beat),
        )

        timing_difference_seconds = (
            abs(beat - target_beat) * 60.0 / self.bpm
        )
        timing_score = math.exp(-timing_difference_seconds / 0.1)

        volume_difference = abs(impulse / SoundEngine.get_scale_factor() - target_event.velocity)
        volume_score = math.exp(-volume_difference / 10.0)

        instrument_score = float(instrument == target_event.instrument)
        hit_score = (
            0.50 * timing_score
            + 0.30 * volume_score
            + 0.20 * instrument_score
        )

        self.matched_targets.add(target_index)
        self.scores.append(hit_score)

    @property
    def accuracy(self) -> float:
        """Return the current accuracy as a value between 0.0 and 1.0."""
        total_attempts = len(self.target_events) + self.extra_hits
        if total_attempts == 0:
            return 1.0

        return sum(self.scores) / total_attempts

    @property
    def accuracy_percent(self) -> float:
        """Return the current accuracy as a percentage."""
        return self.accuracy * 100.0

    def final_audio_accuracy(
        self,
        recorded_audio: np.ndarray,
        sample_rate: int | None = None,
        subdivisions_per_beat: int = 4,
        activity_threshold: float = 0.2,
        timing_tolerance: float | None = None,
    ) -> float:
        """Compare the final recording against the target audio.

        Returns an accuracy value from 0.0 to 1.0 using the per-sample
        timing, volume, and timbre comparison in SoundEngine.
        """
        target_audio = SoundEngine.get_nparray_from_track(self.target_track)
        difference = SoundEngine.check_audio_difference(
            target_audio,
            recorded_audio,
            sample_rate=sample_rate,
            bpm=self.bpm,
            subdivisions_per_beat=subdivisions_per_beat,
            activity_threshold=activity_threshold,
            timing_tolerance=timing_tolerance,
        )
        return 1.0 - difference

    def final_audio_accuracy_percent(
        self,
        recorded_audio: np.ndarray,
        sample_rate: int | None = None,
        subdivisions_per_beat: int = 4,
        activity_threshold: float = 0.2,
        timing_tolerance: float | None = None,
    ) -> float:
        """Return final audio accuracy as a percentage."""
        return self.final_audio_accuracy(
            recorded_audio,
            sample_rate=sample_rate,
            subdivisions_per_beat=subdivisions_per_beat,
            activity_threshold=activity_threshold,
            timing_tolerance=timing_tolerance,
        ) * 100.0
