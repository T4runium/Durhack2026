import pygame, pymunk
from functions.drums import Drumkit, create_all, create_cymbal
from functions.CollisionHandler import register_collision_handlers
from functions.DrumStick import CreateDrumStick , Create_TransparentSource
from classes.button import Button

import pymunk.pygame_util

SCREEN_SIZE = (1280, 720)
from dhtypes import gameStates, soundTypes

def IsValidPosition():
    return pygame.mouse.get_pos()[1] < 300

FPS = 60

space = pymunk.Space()
space.gravity = (0, 750) # 500 pixels per second squared downward
space.damping = 1

gameState: gameStates.GameState = gameStates.GameState.DRUMMOVE


background = pygame.image.load('graphics/backgrounds/BG1.png')
background = pygame.transform.scale(background , SCREEN_SIZE)

current_track: soundTypes.Track | None = None
ongoing_track: soundTypes.Track = soundTypes.Track(
    name="Ongoing Track",
    bpm=120,
    sound_events=[],
)

track_start_time: float = 0
accuracy_score: float = 0.0
accuracy_tracker: AccuracyTracker.AccuracyTracker | None = None

def drag_drum(drums, active_drum: Drumkit, rel) -> None:
    """Move the held drum by the mouse movement, unless that would overlap another drum."""
    previous_position = active_drum.body.position
    active_drum.body.position += rel
    space.reindex_shapes_for_body(active_drum.body)

    overlapping_drum = any(
        info.shape is drum.shape
        for info in space.shape_query(active_drum.shape)
        for drum in drums
        if drum is not active_drum
    )
    if overlapping_drum:
        active_drum.body.position = previous_position
        space.reindex_shapes_for_body(active_drum.body)
    else:
        active_drum.rect.center = active_drum.body.position


def record_hit(instrument: int, impulse: float) -> None:
    global accuracy_score

    beat = (
        (pygame.time.get_ticks() / 1000.0 - track_start_time)
        * ongoing_track.bpm
        / 60.0
    )

    ongoing_track.sound_events.append(
        (
            beat,
            soundTypes.SoundEvent(
                type="drums1",
                instrument=instrument,
                velocity=impulse,
            ),
        )
    )

    if accuracy_tracker is not None:
        accuracy_tracker.register_hit(beat, instrument, impulse)
        accuracy_score = accuracy_tracker.accuracy_percent
    
def set_current_track_from_index(chapter: int, index: int) -> None:
    global current_track, ongoing_track, accuracy_tracker
    
    current_track = Chp1.levels[index]
    ongoing_track = soundTypes.Track(
        name="Ongoing Track",
        bpm=current_track.bpm,
        sound_events=[],
    )
    accuracy_tracker = AccuracyTracker.AccuracyTracker(
        current_track,
        current_track.bpm,
    )

def main() -> None:
    """Run the main Pygame application loop."""
    global track_start_time

    pygame.init()
    screen: pygame.Surface = pygame.display.set_mode(SCREEN_SIZE, pygame.RESIZABLE)
    pygame.display.set_caption("Durhack2026")
    clock: pygame.time.Clock = pygame.time.Clock()



    # Create instances here
    drums = create_all(space)
    cymbal_button = Button(
        "graphics/icons/drums1/CymbalIcon.png",
        "graphics/icons/drums1/CymbalIconInverted.png",
        100,
        100,
        "+",
        lambda: create_cymbal(space, drums),
    )
    drumstick : pygame.sprite.Group = Create_TransparentSource()

    register_collision_handlers(space, record_hit)

    # DRUMMOVE (drag drums, Enter/Space when done) -> STICKMOVE (click above y=300 to drop) -> STICKDROP
    gameState = gameStates.GameState.DRUMMOVE

    active_drum: Drumkit | None = None
    running = True
    while running:

        for event in pygame.event.get():

            cymbal_button.handle_event(event)

            if event.type == pygame.QUIT:

                running = False

            elif event.type == pygame.VIDEORESIZE:
                # pygame 2 resizes the window surface itself; calling set_mode here
                # fights tiling compositors like niri and loops forever
                screen = pygame.display.get_surface()

            elif gameState == gameStates.GameState.DRUMMOVE:

                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    active_drum = next( # sets active drum to most recent colliding drum
                        (
                            drum
                            for drum in reversed(drums.sprites())
                            if drum.rect.collidepoint(event.pos)
                        ),
                        None,
                    )

                elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                    active_drum = None

                elif event.type == pygame.MOUSEMOTION and active_drum is not None:
                    drag_drum(drums, active_drum, event.rel)

                elif event.type == pygame.KEYDOWN and event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    active_drum = None
                    gameState = gameStates.GameState.STICKMOVE

            elif gameState == gameStates.GameState.STICKMOVE:

                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and IsValidPosition():
                    drumstick.empty()

                    drumstick = CreateDrumStick(space)
                    gameState = gameStates.GameState.STICKDROP
                    track_start_time = pygame.time.get_ticks() / 1000.0  # Record the start time of the track


        screen.blit(background , (0,0)) # replace with ui image when ready

        # drawing goes here

        drums.update()
        drums.draw(screen)

        cymbal_button.draw(screen)

        if gameState != gameStates.GameState.DRUMMOVE: # no stick while arranging drums
            drumstick.update()
            drumstick.draw(screen)

        draw_options = pymunk.pygame_util.DrawOptions(screen)

        pygame.display.flip()

        clock.tick(FPS)
        
        #MENU -> PLAYTRACK -> DRUMMOVE -> STICKMOVE -> STICKDROP -> POSTGAME

        match gameState:
            case gameStates.GameState.MENU:
                pass
            case gameStates.GameState.DRUMMOVE:
                pass 
            case gameStates.GameState.STICKMOVE:
                pass 
            case gameStates.GameState.STICKDROP:
                
                sub_steps = 10

                for i in range(sub_steps):
                    space.step(1 / FPS / sub_steps)


    pygame.quit()


if __name__ == "__main__":
    main()
