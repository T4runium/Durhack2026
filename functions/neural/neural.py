import os
import sys
from pathlib import Path
import numpy as np

import pygame

PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT.parent))
os.chdir(PROJECT_ROOT)

import SoundEngine

# AI bandmate: given the last two bars of drumming, predict which drums are hit in the next
# quarter-beat slot. Sampling that repeatedly lets the network play: call-and-response,
# endless level generation, or "what comes next?" challenges.


class Layer:
    def __init__(self, num, next_num):
        scale = 0.1
        self.nodes = [0 for i in range(num)]
        self.weights = np.random.randn(num, next_num) * scale
        self.biases = np.zeros(next_num)


class Network:
    def __init__(self, shape):
        self.z = []
        self.learningRate = 1
        self.shape = shape
        self.length = len(shape)
        self.network = []
        for i in range(self.length - 1):
            self.network.append(Layer(self.shape[i], self.shape[i + 1]))
        self.network.append([0 for i in range(shape[-1])])

    def relu(self, x):
        return np.maximum(0, x)

    def d_relu(self, x):
        return (x > 0).astype(float)

    def sigmoid(self, x):
        return 1 / (1 + np.exp(-np.clip(x, -50, 50)))

    def bce(self, p, y):
        # Binary cross-entropy: each drum is its own yes/no question (several can hit at once)
        p = np.clip(p, 1e-9, 1 - 1e-9)
        return -(y * np.log(p) + (1 - y) * np.log(1 - p)).sum(axis=1).mean()

    def forward(self, inputs):
        # Returns (output, acts, zs). acts[i] is the input to weight layer i; zs[i] is the pre-ReLU of acts[i + 1]
        self.z = []
        acts = [np.array(inputs, dtype=float)]
        self.network[0].nodes = acts[0]
        for i in range(self.length - 2):
            z = np.dot(acts[i], self.network[i].weights) + self.network[i].biases
            self.z.append(z)
            acts.append(self.relu(z))
            self.network[i + 1].nodes = acts[-1]
        out = np.dot(acts[-1], self.network[-2].weights) + self.network[-2].biases
        self.network[-1] = out
        return out, acts, self.z

    def chainRule(self, delta, a_prev, W, z_prev = None):
        delta, a_prev = np.atleast_2d(delta), np.atleast_2d(a_prev)
        dW = np.dot(a_prev.T, delta)
        db = delta.sum(axis=0)
        d_prev = np.dot(delta, W.T)
        if z_prev is not None:
            d_prev *= self.d_relu(z_prev)
        return dW, db, d_prev

    def backward(self, grad_out, acts, zs):
        delta = grad_out
        dW = [None] * (self.length - 1)
        db = [None] * (self.length - 1)
        for i in reversed(range(self.length - 1)):
            z_prev = zs[i - 1] if i > 0 else None
            dW[i], db[i], delta = self.chainRule(delta, acts[i], self.network[i].weights, z_prev)
        return dW, db

    def update(self, dW, db):
        for i in range(self.length - 1):
            self.network[i].weights -= self.learningRate * dW[i]
            self.network[i].biases -= self.learningRate * db[i]

    def train_step(self, x, y):
        out, acts, zs = self.forward(x)
        p = self.sigmoid(np.atleast_2d(out))
        y = np.atleast_2d(y)
        loss = self.bce(p, y)
        # Gradient of sigmoid + BCE with respect to the output layer is simply p - y
        dW, db = self.backward((p - y) / len(y), acts, zs)
        self.update(dW, db)
        return loss

    def predict(self, x, temperature=1.0):
        """Probability of each drum being hit in the next slot. Higher temperature = wilder."""
        out = np.atleast_2d(self.forward(x)[0])
        return self.sigmoid(out / max(temperature, 1e-6))

    def save(self, path):
        arrays = {}
        for i in range(self.length - 1):
            arrays[f"W{i}"] = self.network[i].weights
            arrays[f"b{i}"] = self.network[i].biases
        np.savez(path, shape=np.array(self.shape), **arrays)

    @classmethod
    def load(cls, path):
        data = np.load(path)
        net = cls([int(n) for n in data["shape"]])
        for i in range(net.length - 1):
            net.network[i].weights = data[f"W{i}"]
            net.network[i].biases = data[f"b{i}"]
        return net


# ---------- Beat grid ----------
SUBDIV = 4                      # slots per beat (quarter beats)
BAR = 4 * SUBDIV                # slots per 4/4 bar
CONTEXT = 2 * BAR               # the network sees the last two bars
INSTRUMENTS = [(stype, inst) for stype in SoundEngine.sound_effects
               for inst in SoundEngine.sound_effects[stype]]
N_INST = len(INSTRUMENTS)
INPUT_SIZE = CONTEXT * N_INST + BAR   # grid window + one-hot position in the bar
WEIGHTS_PATH = PROJECT_ROOT / "bandmate_weights.npz"

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


def decode_grid(grid, bpm=120, name="Bandmate", probs=None):
    """Grid -> Track. If probs is given, more confident hits are played louder."""
    events = []
    for slot, inst_col in zip(*np.nonzero(grid)):
        strength = 0.6 if probs is None else 0.4 + 0.6 * probs[slot, inst_col]
        stype, inst = INSTRUMENTS[inst_col]
        events.append((slot / SUBDIV, SoundEngine.SoundEvent(stype, int(inst),
                                                             strength * SoundEngine.SCALE_FACTOR)))
    events.sort(key=lambda e: e[0])
    return SoundEngine.Track(name=name, bpm=bpm, sound_events=events)


def make_input(grid, t):
    """Network input for predicting slot t: the CONTEXT slots before t (zero-padded) + position in bar."""
    window = np.zeros((CONTEXT, N_INST))
    start = max(0, t - CONTEXT)
    window[CONTEXT - (t - start):] = grid[start:t]
    pos = np.zeros(BAR)
    pos[t % BAR] = 1
    return np.concatenate([window.ravel(), pos])


# ---------- Training data: a groove generator ----------
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


def make_dataset(n_grooves, n_bars=8):
    xs, ys = [], []
    for _ in range(n_grooves):
        grid = make_groove(n_bars)
        for t in range(len(grid)):
            xs.append(make_input(grid, t))
            ys.append(grid[t])
    return np.array(xs, dtype=np.float32), np.array(ys, dtype=np.float32)


# ---------- Using the network ----------
def generate(net, seed_track=None, n_beats=8, temperature=1.0, bpm=None):
    """Continue seed_track (or start from silence) for n_beats. Returns only the new part as a Track."""
    bpm = bpm or (seed_track.bpm if seed_track is not None else 120)
    seed = encode_track(seed_track) if seed_track is not None and seed_track.sound_events else np.zeros((0, N_INST))
    # pad the seed to a whole number of bars so the position-in-bar input stays aligned
    pad = (-len(seed)) % BAR
    grid = np.vstack([seed, np.zeros((pad, N_INST))])
    start = len(grid)
    new = np.zeros((n_beats * SUBDIV, N_INST))
    probs = np.zeros_like(new)
    grid = np.vstack([grid, new])
    for k in range(len(new)):
        t = start + k
        p = net.predict(make_input(grid, t), temperature)[0]
        hits = (np.random.rand(N_INST) < p) if temperature > 0 else (p > 0.5)
        grid[t] = hits
        probs[k] = p
    return decode_grid(grid[start:], bpm, "Bandmate", probs)


def respond(net, player_track, n_bars=1, temperature=1.5):
    """Call and response: the player plays, the bandmate answers with n_bars that fit."""
    return generate(net, player_track, n_bars * 4, temperature)


def surprise(net, track):
    """Per-slot surprise of a track to the network (0 = fully expected). Mean works as a rough difficulty score."""
    grid = encode_track(track)
    x = np.array([make_input(grid, t) for t in range(len(grid))])
    p = np.clip(net.predict(x), 1e-9, 1 - 1e-9)
    return -(grid * np.log(p) + (1 - grid) * np.log(1 - p)).sum(axis=1)


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


def train(epochs=8, n_grooves=600, batch=128):
    np.random.seed(0)
    net = Network([INPUT_SIZE, 128, 64, N_INST])
    net.learningRate = 0.5
    x, y = make_dataset(n_grooves)
    tx, ty = make_dataset(60)
    for epoch in range(epochs):
        order = np.random.permutation(len(x))
        for s in range(0, len(x), batch):
            idx = order[s:s + batch]
            net.train_step(x[idx], y[idx])
        test_loss = net.bce(net.predict(tx), ty)
        print(f"epoch {epoch + 1}: test loss {test_loss:.3f}")
    net.save(WEIGHTS_PATH)
    print(f"saved weights to {WEIGHTS_PATH}")
    return net


def load():
    return Network.load(WEIGHTS_PATH)


def test(net=None):
    """Compare against copying the previous bar, check musical sense, and print some generated beats."""
    net = net or load()
    np.random.seed(123)
    grooves = [make_groove(8) for _ in range(60)]

    tp = fp = fn = btp = bfp = bfn = 0
    for grid in grooves:
        for t in range(BAR, len(grid)):
            pred = net.predict(make_input(grid, t))[0] > 0.5
            base = grid[t - BAR] > 0.5           # baseline: "same as one bar ago"
            true = grid[t] > 0.5
            tp += np.sum(pred & true); fp += np.sum(pred & ~true); fn += np.sum(~pred & true)
            btp += np.sum(base & true); bfp += np.sum(base & ~true); bfn += np.sum(~base & true)
    f1 = 2 * tp / max(1, 2 * tp + fp + fn)
    bf1 = 2 * btp / max(1, 2 * btp + bfp + bfn)
    print(f"next-slot F1 on unseen grooves: network {f1:.3f} vs copy-previous-bar {bf1:.3f}")

    np.random.seed(7)
    gen = encode_track(generate(net, None, 16 * 4), 16 * BAR)   # 16 bars from silence
    snare_on_backbeat = gen[:, col(SNARE)].reshape(-1, BAR)[:, [4, 12]].mean()
    kick_on_one = gen[:, col(KICK)].reshape(-1, BAR)[:, 0].mean()
    hits_per_bar = gen.sum() / 16
    print(f"16 generated bars: snare on 2 & 4 {snare_on_backbeat:.0%}, kick on 1 {kick_on_one:.0%}, "
          f"{hits_per_bar:.1f} hits per bar")

    np.random.seed(1)
    show(decode_grid(grooves[0][:2 * BAR]), 2 * BAR, "\nseed groove (2 bars):")
    show(respond(net, decode_grid(grooves[0][:2 * BAR]), 2), 2 * BAR, "bandmate's answer (2 bars):")
    show(generate(net, None, 8), 2 * BAR, "\nfrom silence (2 bars):")

    try:
        from Durhack2026.levels import Chp1
        print()
        for level in Chp1.levels:
            print(f"{level.name}: difficulty (mean surprise) {surprise(net, level).mean():.2f}")
    except ImportError:
        pass
    return net


if __name__ == "__main__":
    if "test" in sys.argv:
        test()
    elif "play" in sys.argv:
        track = generate(load(), None, 16)
        show(track, title="playing:")
        SoundEngine.play_sound_from_track(track)
    else:
        test(train())
