_SOUND_BY_DRUM_TYPE = {
    2: (1, "Cymbal hit!"),
    3: (7, "Snare hit!"),
    4: (5, "Bass hit!"),
    5: (6, "Kick hit!"),
}


def on_hit(arbiter, space, data):
    if not arbiter.is_first_contact:
        return

    drum_shape = next(
        shape for shape in arbiter.shapes if shape.collision_type != 1
    )
    instrument, label = _SOUND_BY_DRUM_TYPE[drum_shape.collision_type]

    from .SoundEngine import play_sound_from_params

    play_sound_from_params("drums1", instrument, arbiter.total_impulse.length)
    print(label)
    print(f"Impulse: {arbiter.total_impulse.length:.2f}")
    return True


def register_collision_handlers(space):
    for collision_type in range(2, 6):
        space.on_collision(1, collision_type, post_solve=on_hit)