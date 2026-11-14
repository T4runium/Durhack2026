from ..dhtypes.soundTypes import Strength, SoundEvent, Track

#Each track consists of a name, bpm, and a list of sound events timestamped with the beat they occur on. 
levels: list[Track] = [
    Track(
        name="Level 1 - Basic Drum Beat",
        bpm=120,
        sound_events=[
            (0.0, SoundEvent(type="drums1", instrument=4, velocity=Strength.MEDIUM.value)),
            (1.0 , SoundEvent(type="drums1", instrument=4, velocity=Strength.MEDIUM.value)),
            (2.0 , SoundEvent(type="drums1", instrument=4, velocity=Strength.MEDIUM.value)),
            (3.0 , SoundEvent(type="drums1", instrument=4, velocity=Strength.MEDIUM.value)),
            (4.0 , SoundEvent(type="drums1", instrument=4, velocity=Strength.MEDIUM.value)),
            (5.0 , SoundEvent(type="drums1", instrument=4, velocity=Strength.MEDIUM.value)),
            (6.0 , SoundEvent(type="drums1", instrument=4, velocity=Strength.MEDIUM.value)),
            (7.0 , SoundEvent(type="drums1", instrument=4, velocity=Strength.MEDIUM.value)),
        ]
    ),
    Track (
        name="Level 2 - Drum and Cymbal",
        bpm=120,
        sound_events=[
            (0.0, SoundEvent(type="drums1", instrument=4, velocity=Strength.MEDIUM.value)),
            (1.0 , SoundEvent(type="drums1", instrument=1, velocity=Strength.HARD.value)),
            (2.0 , SoundEvent(type="drums1", instrument=4, velocity=Strength.MEDIUM.value)),
            (3.0 , SoundEvent(type="drums1", instrument=1, velocity=Strength.HARD.value)),
            (4.0 , SoundEvent(type="drums1", instrument=4, velocity=Strength.MEDIUM.value)),
            (5.0 , SoundEvent(type="drums1", instrument=1, velocity=Strength.HARD.value)),
            (6.0 , SoundEvent(type="drums1", instrument=4, velocity=Strength.MEDIUM.value)),
            (7.0 , SoundEvent(type="drums1", instrument=1, velocity=Strength.HARD.value)),
        ]
    )
]