def on_hit(arbiter, space, data):
    from .SoundEngine import play_sound_from_params

    match arbiter.shapes[0].collision_type:
        case 2:
            play_sound_from_params("drums1", 1, arbiter.total_impulse.length)
            print("Cymbal hit!")
        case 3:
            play_sound_from_params("drums1", 7, arbiter.total_impulse.length)
            print("Hi-Hat hit!")
        case 4:
            play_sound_from_params("drums1", 4, arbiter.total_impulse.length)
            print("Snare hit!")
        case 5:
            play_sound_from_params("drums1", 5, arbiter.total_impulse.length)
            print("Bass hit!")
        case 6:
            play_sound_from_params("drums1", 6, arbiter.total_impulse.length)
            print("Tom hit!")


def register_collision_handlers(space):
    for collision_type in range(2, 6):
        space.on_collision(1, collision_type, begin=on_hit)