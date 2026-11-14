import pygame, pymunk
from functions.drums import create_drums

SCREEN_SIZE = (800, 600)
FPS = 60

space = pymunk.Space()
space.gravity = (0, 900) # 900 pixels per second squared downward


def main() -> None:
    """Run the main Pygame application loop."""
    pygame.init()
    screen: pygame.Surface = pygame.display.set_mode(SCREEN_SIZE, pygame.RESIZABLE)
    pygame.display.set_caption("Durhack2026")
    clock: pygame.time.Clock = pygame.time.Clock()

    drums = create_drums(space)

    running = True
    while running:

        for event in pygame.event.get():

            if event.type == pygame.QUIT:

                running = False
            elif event.type == pygame.VIDEORESIZE:

                scrsize = event.size
                screen = pygame.display.set_mode(scrsize, pygame.RESIZABLE)

        screen.fill((0, 0, 0)) # replace with ui image when ready

        # drawing goes here

        drums.update()
        drums.draw(screen)



        pygame.display.flip()

        clock.tick(FPS)
        space.step(1 / FPS) # update physics simulation

    pygame.quit()


if __name__ == "__main__":
    main()
