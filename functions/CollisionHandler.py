def on_hit(arbiter, space, data):
    from .SoundEngine import play_sound_from_params

    print("Collision!")
    if arbiter.shapes[0].collision_type == 2:
        play_sound_from_params("drums1", 1, arbiter.total_impulse.length)
    elif arbiter.shapes[0].collision_type == 3:
        play_sound_from_params("drums1", 7, arbiter.total_impulse.length)
    elif arbiter.shapes[0].collision_type == 4:
        play_sound_from_params("drums1", 4, arbiter.total_impulse.length)
    elif arbiter.shapes[0].collision_type == 5:
        play_sound_from_params("drums1", 5, arbiter.total_impulse.length)
    elif arbiter.shapes[0].collision_type == 6:
        play_sound_from_params("drums1", 6, arbiter.total_impulse.length)
    return True

def register_collision_handlers(space):
    for collision_type in range(2, 7):
        space.on_collision(1, collision_type, begin=on_hit)