import pygame, pymunk
from functions.drums import Drumkit, create_drums
from functions.CollisionHandler import register_collision_handlers
from functions.DrumStick import CreateDrumStick , Create_TransparentSource
import pymunk.pygame_util

SCREEN_SIZE = (1280, 720)
from dhtypes import gameStates

def IsValidPosition():
    return pygame.mouse.get_pos()[1] < 300

FPS = 60

space = pymunk.Space()
space.gravity = (0, 750) # 500 pixels per second squared downward

gameState: gameStates.GameState = gameStates.GameState.STICKMOVE


background = pygame.image.load('graphics/backgrounds/BG1.png')
background = pygame.transform.scale(background , SCREEN_SIZE)



def main() -> None:
    """Run the main Pygame application loop."""
    pygame.init()
    screen: pygame.Surface = pygame.display.set_mode(SCREEN_SIZE, pygame.RESIZABLE)
    pygame.display.set_caption("Durhack2026")
    clock: pygame.time.Clock = pygame.time.Clock()



    # Create instances here
    drums = create_drums(space)
    drumstick : pygame.sprite.Group = Create_TransparentSource()

    register_collision_handlers(space)

    gameState = gameStates.GameState.STICKMOVE

    active_drum: Drumkit | None = None
    running = True
    while running:

        has_pressed = False

        for event in pygame.event.get():

            if event.type == pygame.QUIT:

                running = False

            elif event.type == pygame.VIDEORESIZE:
                # pygame 2 resizes the window surface itself; calling set_mode here
                # fights tiling compositors like niri and loops forever
                screen = pygame.display.get_surface()

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
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
                previous_position = active_drum.body.position
                active_drum.body.position += event.rel
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


        screen.blit(background , (0,0)) # replace with ui image when ready

        # drawing goes here

        drums.update()
        drums.draw(screen)

        drumstick.update()
        drumstick.draw(screen)

        draw_options = pymunk.pygame_util.DrawOptions(screen)
        # space.debug_draw(draw_options)

        pygame.display.flip()

        clock.tick(FPS)

        sub_steps = 10

        for i in range(sub_steps):
            space.step(1 / FPS / sub_steps) # update physics simulation
            
        match gameState:
            case gameStates.GameState.DRUMMOVE:
                pass
            case gameStates.GameState.MENU:
                pass
            case gameStates.GameState.STICKDROP:
                # end case, either time limit or jump limit
                pass
            case gameStates.GameState.STICKMOVE:

                if (pygame.mouse.get_pressed()[0] and IsValidPosition() ):
                    drumstick.empty()

                    drumstick = CreateDrumStick(space)
                    gameState = gameStates.GameState.STICKDROP
                
            

    pygame.quit()


if __name__ == "__main__":
    main()


