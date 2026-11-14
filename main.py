import pygame


SCREEN_SIZE = (800, 600)
FPS = 60


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
        screen.fill((0, 0, 0))
        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()


if __name__ == "__main__":
    main()
