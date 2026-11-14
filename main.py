import pygame, pymunk
from drums import create_ball, draw_ball

SCREEN_SIZE = (800, 600)
FPS = 60

space = pymunk.Space()
space.gravity = (0, 900) # 900 pixels per second squared downward

ball = create_ball(space) # create a static ball in the physics space


def main() -> None:
    """Run the main Pygame application loop."""
    pygame.init()
    screen: pygame.Surface = pygame.display.set_mode(SCREEN_SIZE, pygame.RESIZABLE)
    pygame.display.set_caption("Durhack2026")
    clock: pygame.time.Clock = pygame.time.Clock()

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

        draw_ball(screen, ball)

        
        pygame.display.flip()

        clock.tick(FPS)
        space.step(1 / FPS) # update physics simulation

    pygame.quit()


if __name__ == "__main__":
    main()
