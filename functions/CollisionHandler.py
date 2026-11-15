from .soundDictionary import _SOUND_BY_DRUM_TYPE


def on_hit(arbiter, space, data):
    if not arbiter.is_first_contact:
        return

    drum_shape = next(
        shape for shape in arbiter.shapes if shape.collision_type != 1 # passes candidate and assigns the first non-drumstick shape to drum_shape
    )
    instrument, label = _SOUND_BY_DRUM_TYPE[drum_shape.collision_type]
    impulse = arbiter.total_impulse.length

    from .SoundEngine import play_sound_from_params

    play_sound_from_params("drums1", instrument, impulse)

    if data is not None:
        data(instrument, impulse)

    print(label)
    print(f"Impulse: {impulse:.2f}")
    return True


def register_collision_handlers(space, hit_callback=None):
    for collision_type in range(2, 6):
        space.on_collision(
            1,
            collision_type,
            post_solve=on_hit,
            data=hit_callback,
        )