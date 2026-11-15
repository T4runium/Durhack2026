import os
import sys
from pathlib import Path
import numpy as np

PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT.parent))
os.chdir(PROJECT_ROOT)

import SoundEngine

SUBDIV = 4                      
BAR = 4 * SUBDIV                
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

HINT_DRUM_SIZES = {2: (223, 33), 3: (204, 70), 4: (202, 112), 5: (204, 70)}


def _boxes_overlap(pos_a, size_a, pos_b, size_b):
    """True if two axis-aligned boxes (centre, (width, height)) overlap."""
    return (abs(pos_a[0] - pos_b[0]) * 2 < size_a[0] + size_b[0]
            and abs(pos_a[1] - pos_b[1]) * 2 < size_a[1] + size_b[1])


def hint_move(current, solution, amount=0.25, sizes=None, snap=2.0):
    """Move each drum `amount` (0-1) of the way towards its solution position, without overlapping.

    current, solution: {collision type: (x, y)}. Returns new positions in the same form.
    Furthest drums move first; a blocked step is halved until it fits (or skipped).
    Drums within `snap` pixels of their target go exactly onto it.
    """
    if not 0 <= amount <= 1:
        raise ValueError("amount must be between 0 and 1")
    sizes = HINT_DRUM_SIZES if sizes is None else sizes
    new = {k: (float(p[0]), float(p[1])) for k, p in current.items()}
    if amount == 0:
        return new

    def distance(k):
        return float(np.hypot(solution[k][0] - new[k][0], solution[k][1] - new[k][1]))

    for k in sorted(set(current) & set(solution), key=distance, reverse=True):
        start, goal = np.array(new[k]), np.array(solution[k], dtype=float)
        step = amount if np.linalg.norm(goal - start) * (1 - amount) > snap else 1.0
        for _ in range(8):                      # halve the step until it doesn't overlap anything
            pos = start + step * (goal - start)
            blocked = k in sizes and any(
                _boxes_overlap(pos, sizes[k], new[o], sizes[o])
                for o in new if o != k and o in sizes)
            if not blocked:
                new[k] = (float(pos[0]), float(pos[1]))
                break
            step /= 2
    return new


def hint_progress(current, solution):
    """Average distance in pixels between the drums and their solution positions (0 = solved)."""
    keys = set(current) & set(solution)
    if not keys:
        return 0.0
    return float(np.mean([np.hypot(solution[k][0] - current[k][0], solution[k][1] - current[k][1])
                          for k in keys]))


# ---------- Similarity: how close the played track is to the solution ----------
def similarity(solution, played, window=0.15, align_start=True):
    """Similarity between the solution Track and the played Track, as a percentage (0-100).

    Hits on the same instrument are paired, closest first; a pair scores 1 when exact, falling to 0
    at `window` seconds apart. Missed notes and extra hits both lower the score.
    align_start: line up the first played hit with the solution's first note.
    """
    sol = sorted(solution.sound_events, key=lambda e: e[0])
    ply = sorted(played.sound_events, key=lambda e: e[0])
    if not sol and not ply:
        return 100.0
    elif not sol or not ply:
        return 0.0

    spb_sol, spb_ply = 60.0 / solution.bpm, 60.0 / played.bpm
    sol_t = [beat * spb_sol for beat, _ in sol]
    ply_t = [beat * spb_ply for beat, _ in ply]
    if align_start:
        shift = sol_t[0] - ply_t[0]
        ply_t = [t + shift for t in ply_t]

    pairs = sorted(
        (abs(st - pt), i, j)
        for i, (st, (_, se)) in enumerate(zip(sol_t, sol))
        for j, (pt, (_, pe)) in enumerate(zip(ply_t, ply))
        if se.instrument == pe.instrument and abs(st - pt) < window
    )
    used_sol, used_ply, total = set(), set(), 0.0
    for dt, i, j in pairs:
        if i not in used_sol and j not in used_ply:
            used_sol.add(i)
            used_ply.add(j)
            total += 1 - dt / window
    return 100.0 * 2 * total / (len(sol) + len(ply))
