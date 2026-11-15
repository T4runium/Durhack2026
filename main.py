import pygame, pymunk
from functions.drums import Drumkit, create_drums
from functions.CollisionHandler import register_collision_handlers
from functions.DrumStick import CreateDrumStick , Create_TransparentSource , DrumStick

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


def main() -> None:
    """Run the main Pygame application loop."""
    pygame.init()
    screen: pygame.Surface = pygame.display.set_mode(SCREEN_SIZE, pygame.RESIZABLE)
    pygame.display.set_caption("Durhack2026")
    clock: pygame.time.Clock = pygame.time.Clock()



    # Create instances here
    drums = create_drums(space)
    drumstick : pygame.sprite.Group = Create_TransparentSource()
    
    current_track: soundTypes.Track | None = None
    ongoing_track: soundTypes.Track | None = None

    register_collision_handlers(space)

    # DRUMMOVE (drag drums, Enter/Space when done) -> STICKMOVE (click above y=300 to drop) -> STICKDROP
    gameState = gameStates.GameState.DRUMMOVE

    active_drum: Drumkit | None = None
    running = True
    time_run = 0

    while running:

        for event in pygame.event.get():

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
            elif gameState == gameStates.GameState.STICKDROP:
                
                if event.type == pygame.MOUSEBUTTONDOWN:
                    for j in drumstick:
                        if (isinstance(j,DrumStick)):
                            if (j.rect.collidepoint(event.pos)):
                                pass # add the sound effect
                


        screen.blit(background , (0,0)) # replace with ui image when ready

        # drawing goes here

        drums.update()
        drums.draw(screen)

        if not gameState in (gameStates.GameState.DRUMMOVE , gameStates.GameState.MENU): # no stick while arranging drums
            drumstick.update()
            drumstick.draw(screen)



        draw_options = pymunk.pygame_util.DrawOptions(screen)

        pygame.display.flip()

        clock.tick(FPS)
        
        #MENU -> PLAYTRACK -> DRUMMOVE -> STICKMOVE -> STICKDROP -> POSTGAME

        if (gameState == gameStates.GameState.STICKDROP):
                for j in drumstick:
                    if (isinstance(j , DrumStick)):
                        if (j.IsOutOfBounds(SCREEN_SIZE)):
                            j.GetRidOf()
            
                gameState = gameStates.GameState.DRUMMOVE
                drumstick.empty()
                       
        sub_steps = 10

        for i in range(sub_steps):
            space.step(1 / FPS / sub_steps) 


    pygame.quit()


if __name__ == "__main__":
    main()
