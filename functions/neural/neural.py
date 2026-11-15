import os
import sys
from pathlib import Path
import numpy as np

import pygame

PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT.parent))
os.chdir(PROJECT_ROOT)

import SoundEngine

# Imitator: an AI "hand" plays the actual game (pymunk drumstick) to copy a track.
# Each time the stick hits a drum (or a planned hit is overdue), the hand sets the stick's
# velocity with projectile maths so it lands on the next note's drum at the right moment.


# ---------- Beat grid ----------
SUBDIV = 4                      # slots per beat (quarter beats)
BAR = 4 * SUBDIV                # slots per 4/4 bar
INSTRUMENTS = [(stype, inst) for stype in SoundEngine.sound_effects
               for inst in SoundEngine.sound_effects[stype]]
N_INST = len(INSTRUMENTS)

# drums1 instrument numbers (see sounds/sound_effect_dict.py)
CYMBAL, HIHAT, TOM_HI, TOM_MID, TOM_LO, KICK, SNARE = 1, 2, 3, 4, 5, 6, 7


def col(inst, stype="drums1"):
    return INSTRUMENTS.index((stype, inst))


def encode_track(track, n_slots=None):
    """Track -> grid of shape (slots, instruments), 1 where a drum is hit. Off-grid hits snap to the nearest slot."""
    last = max((beat for beat, _ in track.sound_events), default=0)
    if n_slots is None:
        n_slots = int(round(last * SUBDIV)) + 1
    grid = np.zeros((n_slots, N_INST))
    for beat, event in track.sound_events:
        key = (event.type, event.instrument)
        slot = int(round(beat * SUBDIV))
        if key in INSTRUMENTS and 0 <= slot < n_slots:
            grid[slot, INSTRUMENTS.index(key)] = 1
    return grid


def decode_grid(grid, bpm=120, name="Groove"):
    """Grid -> Track."""
    events = []
    for slot, inst_col in zip(*np.nonzero(grid)):
        stype, inst = INSTRUMENTS[inst_col]
        events.append((slot / SUBDIV, SoundEngine.SoundEvent(stype, int(inst),
                                                             0.6 * SoundEngine.SCALE_FACTOR)))
    events.sort(key=lambda e: e[0])
    return SoundEngine.Track(name=name, bpm=bpm, sound_events=events)


def show(track, n_slots=None, title=None):
    """Print a track as a drum grid, one row per instrument."""
    grid = encode_track(track, n_slots)
    names = {CYMBAL: "crash", HIHAT: "hihat", TOM_HI: "tom hi", TOM_MID: "tom mid",
             TOM_LO: "tom lo", KICK: "kick", SNARE: "snare"}
    if title:
        print(title)
    for c, (stype, inst) in enumerate(INSTRUMENTS):
        row = "".join(("x" if grid[t, c] else ".") + (" " if t % BAR == BAR - 1 else "")
                      for t in range(len(grid)))
        print(f"  {names.get(inst, f'{stype} {inst}'):8s}{row}")


# ---------- Test grooves for the imitator ----------
KICK_PATTERNS = [[0, 8], [0, 10], [0, 6, 8], [0, 7, 10], [0, 8, 10], [0, 3, 8, 11], [0, 4, 8, 12]]


def make_groove(n_bars=8):
    """A random but musical drum groove: hats, kick pattern, backbeat snare, fills and crashes."""
    grid = np.zeros((n_bars * BAR, N_INST))
    hat = HIHAT if np.random.rand() < 0.8 else CYMBAL
    hat_step = np.random.choice([4, 2, 1], p=[0.2, 0.6, 0.2])
    kick = KICK_PATTERNS[np.random.randint(len(KICK_PATTERNS))]
    snare = [4, 12] if np.random.rand() < 0.8 else [8]
    fill_every = np.random.choice([4, 8])
    for b in range(n_bars):
        s = b * BAR
        fill = (b % fill_every == fill_every - 1) and np.random.rand() < 0.7
        groove_end = BAR - (np.random.choice([4, 8]) if fill else 0)
        for i in range(0, groove_end, hat_step):
            grid[s + i, col(hat)] = 1
        for i in kick:
            if i < groove_end:
                grid[s + i, col(KICK)] = 1
        for i in snare:
            if i < groove_end:
                grid[s + i, col(SNARE)] = 1
        if np.random.rand() < 0.25 and groove_end == BAR:  # occasional extra kick
            grid[s + np.random.choice([2, 6, 14]), col(KICK)] = 1
        if np.random.rand() < 0.15:                        # occasional ghost snare
            grid[s + np.random.choice([7, 9, 15]), col(SNARE)] = 1
        if fill:  # tom run down, or a snare roll
            toms = [SNARE] * 4 if np.random.rand() < 0.3 else [TOM_HI, TOM_HI, TOM_MID, TOM_MID, TOM_LO, TOM_LO, TOM_LO, TOM_LO]
            length = BAR - groove_end
            for k, i in enumerate(range(groove_end, BAR)):
                grid[s + i, col(toms[int(k * len(toms) / length)])] = 1
            if b + 1 < n_bars:                              # crash on the next downbeat
                grid[s + BAR, col(CYMBAL)] = 1
    return grid


import pymunk
from DrumStick import Create_DrumStick

FPS = 60                     # main.py: clock.tick(FPS), space.step(1 / FPS)
GRAVITY = 750     # main.py: space.gravity = (0, 750)
# Copy of drums.create_drums: collision type -> centre. Update if the drums move.
DRUM_LAYOUT = {2: (600, 600), 3: (400, 600), 4: (200, 600)}
DRUM_SIZE = 100
DRUM_TYPES = sorted(DRUM_LAYOUT)
DRUM_NAMES = {2: "cymbal", 3: "snare", 4: "bass"}
# CollisionHandler._SOUND_BY_DRUM_TYPE: drum -> drums1 instrument it plays
DRUM_INSTRUMENT = {2: 1, 3: 7, 4: 5}
# Track instrument -> which of the 3 game drums plays it
INSTRUMENT_TO_DRUM = {CYMBAL: 2, HIHAT: 2, SNARE: 3, TOM_HI: 3, TOM_MID: 4, TOM_LO: 4, KICK: 4}
STICK_HALF = (62.5, 25)      # DrumStick_size / 2
START_POS = (400, 300)       # where the hand picks the stick up
LEAD_IN = 1.0                # seconds before the track's first beat
MIN_GAP = 0.1                # notes closer than this (one stick!) are merged


def build_space():
    """Headless copy of the game's physics: the real drumstick + the drums."""
    space = pymunk.Space()
    space.gravity = (0, GRAVITY)
    stick = Create_DrumStick(space)
    stick.collision_type = 1
    for ct, pos in DRUM_LAYOUT.items():
        body = pymunk.Body(1, 100, body_type=pymunk.Body.STATIC)
        body.position = pos
        shape = pymunk.Poly.create_box(body, (DRUM_SIZE, DRUM_SIZE))
        shape.elasticity = 1
        shape.collision_type = ct
        space.add(body, shape)
    return space, stick.body


def reset_stick(body):
    body.position = START_POS
    body.velocity = (0, 0)
    body.angle = 0
    body.angular_velocity = 0


def physics_aim(body, drum, dt):
    """Velocity that makes the stick land on top of `drum` in `dt` seconds (projectile motion)."""
    x, y = body.position
    a = body.angle
    half_height = STICK_HALF[0] * abs(np.sin(a)) + STICK_HALF[1] * abs(np.cos(a))
    tx, ty = DRUM_LAYOUT[drum][0], DRUM_LAYOUT[drum][1] - DRUM_SIZE / 2 - half_height
    return np.array([(tx - x) / dt, (ty - y - 0.5 * GRAVITY * dt ** 2) / dt])


def is_lost(body):
    x, y = body.position
    return not (-200 < x < 1000 and y < 900)


def track_to_notes(track):
    """Track -> list of (seconds after start, game drum). One stick, so near-simultaneous notes merge."""
    spb = 60.0 / track.bpm
    priority = {3: 0, 4: 1, 2: 2}   # when notes clash keep snare, then bass, then cymbal
    notes = []
    for beat, event in sorted(track.sound_events, key=lambda e: e[0]):
        drum = INSTRUMENT_TO_DRUM.get(event.instrument)
        if drum is None:
            continue
        t = LEAD_IN + beat * spb
        if notes and t - notes[-1][0] < MIN_GAP:
            if priority[drum] < priority[notes[-1][1]]:
                notes[-1] = (notes[-1][0], drum)
            continue
        notes.append((t, drum))
    return notes


class Imitator:
    """Controller shared by the headless sim and the real game window.
    Call before_step(now, body) every frame and on_hit(now, drum, impulse) on every first contact."""

    def __init__(self, notes, aim):
        self.notes = notes
        self.aim = aim                  # function (body, drum, dt) -> velocity
        self.next = 0                   # index of the note we are currently throwing for
        self.need_action = True
        self.hits = []                  # what was actually played: (time, drum, impulse)

    def on_hit(self, now, drum, impulse):
        self.hits.append((now, drum, impulse))
        if (self.next < len(self.notes) and self.notes[self.next][1] == drum
                and abs(self.notes[self.next][0] - now) < 0.15):
            self.next += 1              # that was (roughly) the planned hit: aim for the next one
            self.need_action = True

    def before_step(self, now, body):
        if self.next < len(self.notes) and now > self.notes[self.next][0] + 0.1:
            self.next += 1              # missed it: give up on that note and aim for the next one
            self.need_action = True
        if is_lost(body):
            reset_stick(body)
            self.need_action = True
        if self.need_action:            # skip notes that are too close to reach in time
            while self.next < len(self.notes) and self.notes[self.next][0] - now < 1.0 / FPS:
                self.next += 1
        if self.need_action and self.next < len(self.notes):
            t, drum = self.notes[self.next]
            dt = t - now
            body.velocity = tuple(float(v) for v in self.aim(body, drum, dt))
            self.need_action = False

    @property
    def done(self):
        return self.next >= len(self.notes)


def _watch_hits(space, callback):
    def post_solve(arbiter, space, data):
        if arbiter.is_first_contact:
            drum = next(s.collision_type for s in arbiter.shapes if s.collision_type != 1)
            callback(drum, arbiter.total_impulse.length)
    for ct in DRUM_TYPES:
        space.on_collision(1, ct, post_solve=post_solve)


def simulate(track, aim, extra_time=1.0):
    """Play a track headlessly. Returns the Imitator (with .hits) and the notes it aimed for."""
    space, body = build_space()
    reset_stick(body)
    notes = track_to_notes(track)
    ctrl = Imitator(notes, aim)
    frame = [0]
    _watch_hits(space, lambda drum, imp: ctrl.on_hit(frame[0] / FPS, drum, imp))
    end = (notes[-1][0] if notes else 0) + extra_time
    while frame[0] / FPS < end:
        ctrl.before_step(frame[0] / FPS, body)
        space.step(1 / FPS)
        frame[0] += 1
    return ctrl, notes


def score(notes, hits, window=0.07):
    """Match played hits to notes (same drum, within `window` seconds)."""
    used, matched, errors = set(), 0, []
    for t, drum in notes:
        best = None
        for i, (ht, hd, _) in enumerate(hits):
            if i not in used and hd == drum and abs(ht - t) <= window and (best is None or abs(ht - t) < abs(hits[best][0] - t)):
                best = i
        if best is not None:
            used.add(best)
            matched += 1
            errors.append(abs(hits[best][0] - t))
    return {"hit_rate": matched / max(1, len(notes)),
            "timing_ms": 1000 * float(np.mean(errors)) if errors else float("nan"),
            "extra_hits": len(hits) - len(used)}


def hits_to_track(hits, bpm=120, name="Imitation"):
    """What the AI actually played, as a Track you can show / play / compare."""
    spb = 60.0 / bpm
    events = [((t - LEAD_IN) / spb, SoundEngine.SoundEvent("drums1", DRUM_INSTRUMENT[d], imp))
              for t, d, imp in hits if t >= LEAD_IN - 0.1]
    return SoundEngine.Track(name=name, bpm=bpm, sound_events=events)


def imitate(track):
    """Headless: the AI plays `track` in the game physics. Returns (what it played as a Track, score)."""
    ctrl, notes = simulate(track, physics_aim)
    return hits_to_track(ctrl.hits, track.bpm), score(notes, ctrl.hits)


def play_in_game(track):
    """Open the game window and let the AI play `track` with the real drums, stick and sounds."""
    from Durhack2026.functions.drums import create_drums
    from Durhack2026.functions.DrumStick import CreateDrumStick
    from Durhack2026.functions.CollisionHandler import on_hit as game_on_hit

    pygame.init()
    screen = pygame.display.set_mode((800, 600), pygame.RESIZABLE)
    pygame.display.set_caption(f"AI imitating: {track.name}")
    clock = pygame.time.Clock()
    space = pymunk.Space()
    space.gravity = (0, GRAVITY)
    drums = create_drums(space)
    stick_group = CreateDrumStick(space)
    body = next(iter(stick_group)).shape.body
    reset_stick(body)

    notes = track_to_notes(track)
    ctrl = Imitator(notes, physics_aim)
    frame = 0

    def post_solve(arbiter, space, data):
        game_on_hit(arbiter, space, data)          # the game's own sound + print
        if arbiter.is_first_contact:
            drum = next(s.collision_type for s in arbiter.shapes if s.collision_type != 1)
            ctrl.on_hit(frame / FPS, drum, arbiter.total_impulse.length)
    for ct in DRUM_TYPES:
        space.on_collision(1, ct, post_solve=post_solve)

    end = (notes[-1][0] if notes else 0) + 1.5
    running = True
    while running and frame / FPS < end:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        ctrl.before_step(frame / FPS, body)
        screen.fill((0, 0, 0))
        drums.update()
        drums.draw(screen)
        stick_group.update()
        stick_group.draw(screen)
        pygame.display.flip()
        clock.tick(FPS)
        space.step(10 / FPS)
        frame += 1
    pygame.quit()
    result = score(notes, ctrl.hits)
    print(f"hit {result['hit_rate']:.0%} of notes, average {result['timing_ms']:.0f} ms off, "
          f"{result['extra_hits']} extra hits")
    return hits_to_track(ctrl.hits, track.bpm), result


def test_imitator(tracks=None):
    """Play each level + some generated grooves headlessly and report how well the AI copied them."""
    if tracks is None:
        tracks = []
        try:
            from Durhack2026.levels import Chp1
            tracks += list(Chp1.levels)
        except ImportError:
            pass
        np.random.seed(5)
        tracks += [decode_grid(make_groove(2), name=f"random groove {i}") for i in range(5)]
    for track in tracks:
        _, r = imitate(track)
        print(f"{track.name:32s} hit {r['hit_rate']:4.0%}  {r['timing_ms']:3.0f} ms off  "
              f"{r['extra_hits']} extra hits")


if __name__ == "__main__":
    if "imitate" in sys.argv:
        from Durhack2026.levels import Chp1
        level = Chp1.levels[int(sys.argv[-1]) if sys.argv[-1].isdigit() else 0]
        show(level, title=f"{level.name}:")
        played, _ = play_in_game(level)
        show(played, title="AI played:")
    elif "test_imitator" in sys.argv:
        test_imitator()
