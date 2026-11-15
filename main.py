import pygame, pymunk
from functions.drums import (
    Drumkit,
    create_all,
    create_bass,
    create_cymbal,
    create_kick,
    create_snare,
)
from functions.CollisionHandler import register_collision_handlers
from functions.DrumStick import CreateDrumStick , Create_TransparentSource , DrumStick
from functions import SoundEngine
from classes.button import Button
import classes.AccuracyTracker as AccuracyTracker
 
import pymunk.pygame_util

from levels import Chp1

SCREEN_SIZE = (1280, 720)
from dhtypes import gameStates, soundTypes

def IsValidPosition():
    return pygame.mouse.get_pos()[1] < 300

FPS = 60

space = pymunk.Space()
space.gravity = (0, 750) # 500 pixels per second squared downward
space.damping = 1

gameState: gameStates.GameState = gameStates.GameState.STICKMOVE

def nextState(next_state: gameStates.GameState) -> None:
    global gameState
    gameState = next_state

def resetToDrumMove(drums: pygame.sprite.Group, drumstick: pygame.sprite.Group) -> None:
    global gameState

    for drum in drums:
        space.remove(drum.body, drum.shape)
    drums.empty()
    drums.add(create_all(space))

    drumstick.empty()

    drumstick = Create_TransparentSource()

    gameState = gameStates.GameState.DRUMMOVE

def start_stick_move() -> None:
    global track_start_time

    if gameState != gameStates.GameState.DRUMMOVE:
        return

    stick_move_start_time = pygame.time.get_ticks() / 1000.0
    track_start_time = stick_move_start_time + 4 * 60.0 / ongoing_track.bpm
    nextState(gameStates.GameState.STICKMOVE)


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

    current_time = pygame.time.get_ticks() / 1000.0
    if current_time < track_start_time:
        return

    beat = (current_time - track_start_time) * ongoing_track.bpm / 60.0

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
    global gameState, track_start_time

    pygame.init()
    screen: pygame.Surface = pygame.display.set_mode(SCREEN_SIZE, pygame.RESIZABLE)
    pygame.display.set_caption("Durhack2026")
    clock: pygame.time.Clock = pygame.time.Clock()



    # Create instances here
    drums = create_all(space)
    drum_buttons = [
        Button(
            "graphics/icons/drums1/CymbalIcon.png",
            "graphics/icons/drums1/CymbalIconInverted.png",
            100,
            100,
            "+",
            lambda: create_cymbal(space, drums),
            2,
        ),
        Button(
            "graphics/icons/drums1/SnareIcon.png",
            "graphics/icons/drums1/SnareInvertedIcon.png",
            100,
            200,
            "+",
            lambda: create_snare(space, drums),
            3,
        ),
        Button(
            "graphics/icons/drums1/DrumLargeIcon.png",
            "graphics/icons/drums1/DrumLargeInvertedIcon.png",
            100,
            300,
            "+",
            lambda: create_bass(space, drums),
            4,
        ),
        Button(
            "graphics/icons/drums1/DrumKickIcon.png",
            "graphics/icons/drums1/DrumKickInvertedIcon.png",
            100,
            400,
            "+",
            lambda: create_kick(space, drums),
            5,
        ),
        Button(
            "graphics/icons/ui/PlayIcon.png",
            "graphics/icons/ui/PlayIconInverted.png",
            1210,
            650,
            "",
            lambda: start_stick_move(),
        ),
        Button(
            "graphics/icons/ui/Restart.png",
            "graphics/icons/ui/RestartInverted.png",
            1200,
            100,
            "",
            lambda: resetToDrumMove(drums, drumstick),
        )
    ]
    drumstick : pygame.sprite.Group = Create_TransparentSource()

    register_collision_handlers(space, record_hit)

    # DRUMMOVE (drag drums, Enter/Space when done) -> STICKMOVE (click above y=300 to drop) -> STICKDROP
    gameState = gameStates.GameState.STICKMOVE

    active_drum: Drumkit | None = None
    running = True
    while running:

        for event in pygame.event.get():

            for button in drum_buttons:
                button.handle_event(event)

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

            elif gameState == gameStates.GameState.STICKMOVE:

                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and IsValidPosition():
                    drumstick.empty()

                    drumstick = CreateDrumStick(space)
                    gameState = gameStates.GameState.STICKDROP
            elif gameState == gameStates.GameState.STICKDROP:
                
                if event.type == pygame.MOUSEBUTTONDOWN:
                    for j in drumstick:
                        if (isinstance(j,DrumStick)):
                            if (j.rect.collidepoint(event.pos)):
                                SoundEngine.play_sound_from_params("drums1", 8)


        screen.blit(background , (0,0)) # replace with ui image when ready

        # drawing goes here

        drums.update()
        drums.draw(screen)

        for button in drum_buttons:
            button.draw(screen)

        if gameState != gameStates.GameState.DRUMMOVE: # no stick while arranging drums

            drumstick.update()
            drumstick.draw(screen)

        draw_options = pymunk.pygame_util.DrawOptions(screen)

        pygame.display.flip()

        clock.tick(FPS)
        
        #MENU -> PLAYTRACK -> DRUMMOVE -> STICKMOVE -> STICKDROP -> POSTGAME

        if (gameState == gameStates.GameState.STICKDROP):
                for j in drumstick:
                    if (isinstance(j , DrumStick)):
                        if (not j.IsOutOfBounds(SCREEN_SIZE)):
                            j.GetRidOf()
            
                            gameState = gameStates.GameState.DRUMMOVE
                            drumstick.empty()
                            gameState = gameStates.GameState.DRUMMOVE

                            drumstick.empty()

                            drumstick = Create_TransparentSource()

        sub_steps = 10

        for _ in range(sub_steps):
            space.step(1 / FPS / sub_steps) 


    pygame.quit()


if __name__ == "__main__":
    main()
