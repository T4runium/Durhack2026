import pygame, pymunk
from functions.drums import create_drums
from functions.CollisionHandler import on_hit as game_on_hit
from functions.DrumStick import CreateDrumStick
from functions.neural import neural
import pymunk.pygame_util

SCREEN_SIZE = (1280, 720)
from dhtypes import gameStates

FPS = 60

space = pymunk.Space()
space.gravity = (0, 750) # 500 pixels per second squared downward

# ---------- AI bandmate (call and response) ----------
SoundEngine = neural.SoundEngine
BPM = 120
SPB = 60 / BPM                     # seconds per beat
ROUND_BEATS = 8                    # player plays 2 bars, then the bandmate answers 2 bars
DRUM_INSTRUMENT = {2: 1, 3: 7, 4: 5, 5: 6}   # drum collision type -> drums1 instrument (as CollisionHandler)


def seconds() -> float:
    return pygame.time.get_ticks() / 1000


class Bandmate:
    """Records the player's hits for a round, then plays the network's answer without blocking the loop."""

    def __init__(self):
        self.net = neural.load()
        self.player_hits = []      # (beat, drum type, impulse)
        self.queue = []            # answer notes still to play: (beat, SoundEvent)
        self.round_start = seconds()
        self.answer_start = None   # None while the player is playing

    def on_hit(self, arbiter, space, data):
        game_on_hit(arbiter, space, data)            # the game's own sound + print
        if arbiter.is_first_contact and self.answer_start is None:
            drum = next(s.collision_type for s in arbiter.shapes if s.collision_type != 1)
            beat = (seconds() - self.round_start) / SPB
            self.player_hits.append((beat, drum, arbiter.total_impulse.length))

    def player_track(self):
        events = [(beat, SoundEngine.SoundEvent("drums1", DRUM_INSTRUMENT[d], imp))
                  for beat, d, imp in self.player_hits]
        return SoundEngine.Track(name="Player", bpm=BPM, sound_events=events)

    def update(self):
        now = seconds()
        if self.answer_start is None and now - self.round_start >= ROUND_BEATS * SPB:
            player = self.player_track()
            answer = neural.respond(self.net, player, n_bars=ROUND_BEATS // 4)
            neural.show(player, ROUND_BEATS * neural.SUBDIV, "you played:")
            neural.show(answer, ROUND_BEATS * neural.SUBDIV, "bandmate answers:")
            if player.sound_events:
                print(f"difficulty of your part (mean surprise): {neural.surprise(self.net, player).mean():.2f}")
            self.queue = sorted(answer.sound_events, key=lambda e: e[0])
            self.answer_start = now
        if self.answer_start is not None:
            while self.queue and self.queue[0][0] * SPB <= now - self.answer_start:
                _, ev = self.queue.pop(0)
                SoundEngine.play_sound_from_params(ev.type, ev.instrument, ev.velocity)
            if now - self.answer_start >= ROUND_BEATS * SPB:   # answer finished: next round
                self.player_hits.clear()
                self.queue.clear()
                self.round_start, self.answer_start = now, None

gameState: gameStates.GameState = gameStates.GameState.LOADING

def main() -> None:
    """Run the main Pygame application loop."""
    pygame.init()
    screen: pygame.Surface = pygame.display.set_mode(SCREEN_SIZE, pygame.RESIZABLE)
    pygame.display.set_caption("Durhack2026")
    clock: pygame.time.Clock = pygame.time.Clock()

    # Create instances here
    drums = create_drums(space)
    drumstick = CreateDrumStick(space)
    bandmate = Bandmate()

    for collision_type in range(2, 6):
        space.on_collision(1, collision_type, post_solve=bandmate.on_hit)

    running = True
    gameState: gameStates.GameState = gameStates.GameState.DRUMMOVE # Start in DRUMMOVE state for testing
    while running:

        for event in pygame.event.get():

            if event.type == pygame.QUIT:

                running = False

            elif event.type == pygame.VIDEORESIZE:
                # pygame 2 resizes the window surface itself; calling set_mode here
                # fights tiling compositors like niri and loops forever
                screen = pygame.display.get_surface()

        bandmate.update()

        screen.fill((0, 0, 0)) # replace with ui image when ready

        # drawing goes here

        drums.update()
        drums.draw(screen)

        drumstick.update()
        drumstick.draw(screen)

        draw_options = pymunk.pygame_util.DrawOptions(screen)
        space.debug_draw(draw_options)

        pygame.display.flip()

        clock.tick(FPS)

        sub_steps = 10

        for i in range(sub_steps):
            space.step(1 / FPS / sub_steps) # update physics simulation
            
        match gameState:
            case gameStates.GameState.DRUMMOVE:
                pass
            case gameStates.GameState.STICKDROP:
                pass
            case _:
                pass

    pygame.quit()


if __name__ == "__main__":
    main()
