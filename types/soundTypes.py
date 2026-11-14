from enum import Enum
from typing import NamedTuple

class SoundEvent(NamedTuple):
    type: str
    instrument: int
    velocity: float

class Strength(Enum):
    SOFT = 0.0
    MEDIUM = 0.5
    HARD = 1.0
    
class Track(NamedTuple):
    name: str
    bpm: int 
    sound_events: list[tuple[float, SoundEvent]]