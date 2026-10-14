#!/usr/bin/env python3
"""Synthétise la musique (120 BPM, ré majeur) et les effets sonores, calés sur
le découpage de data.json. Sorties : assets/audio/music.wav et assets/audio/sfx.wav.
Tout est généré ici : aucun échantillon tiers, aucun droit à gérer.
"""
import json
import wave
from pathlib import Path

import numpy as np
from scipy.signal import butter, sosfilt

HERE = Path(__file__).resolve().parent
SR = 48000
D = json.loads((HERE / "data.json").read_text())
T = D["T"]
END = T["end"]
N = int(END * SR)
BEAT = 0.5  # 120 BPM
rng = np.random.default_rng(2026)


def midi(m):
    return 440.0 * 2 ** ((m - 69) / 12)


def lp(x, fc, order=2):
    return sosfilt(butter(order, fc, "low", fs=SR, output="sos"), x)


def hp(x, fc, order=2):
    return sosfilt(butter(order, fc, "high", fs=SR, output="sos"), x)


def bp(x, lo, hi, order=2):
    return sosfilt(butter(order, [lo, hi], "band", fs=SR, output="sos"), x)


def saw(f, dur, detune=(0.0,), harm=40):
    t = np.arange(int(dur * SR)) / SR
    out = np.zeros_like(t)
    for d in detune:
        ff = f * 2 ** (d / 1200)
        k_max = int(min(harm, (SR / 2.2) / ff))
        ph = rng.uniform(0, 2 * np.pi)
        for k in range(1, k_max + 1):
            out += np.sin(2 * np.pi * k * ff * t + k * ph) / k
    return out / (len(detune) * 1.6)


def env(n, a=0.005, d=0.1, s=0.0, r=0.05, hold=None):
    t = np.arange(n) / SR
    hold = (n / SR - r) if hold is None else hold
    e = np.where(t < a, t / max(a, 1e-6), s + (1 - s) * np.exp(-(t - a) / max(d, 1e-6)))
    rel = np.clip((t - hold) / max(r, 1e-6), 0, 1)
    return e * (1 - rel)


def place(buf, x, at, gain=1.0, pan=0.0):
    i = int(round(at * SR))
    if i >= buf.shape[1] or i + len(x) <= 0:
        return
    j0 = max(0, -i)
    x = x[j0:]
    i = max(0, i)
    n = min(len(x), buf.shape[1] - i)
    l, r = np.cos((pan + 1) * np.pi / 4), np.sin((pan + 1) * np.pi / 4)
    buf[0, i:i + n] += x[:n] * gain * l * 1.414
    buf[1, i:i + n] += x[:n] * gain * r * 1.414


# ---------------- instruments ----------------
def kick():
    n = int(0.42 * SR)
    t = np.arange(n) / SR
    f = 46 + 120 * np.exp(-t * 32)
    ph = 2 * np.pi * np.cumsum(f) / SR
    x = np.sin(ph) * np.exp(-t * 7.5)
    x[: int(0.004 * SR)] += rng.uniform(-1, 1, int(0.004 * SR)) * 0.4
    return np.tanh(x * 1.6)


def clap():
    n = int(0.3 * SR)
    t = np.arange(n) / SR
    noise = bp(rng.uniform(-1, 1, n), 900, 3200)
    e = np.exp(-t * 18)
    for off in (0.0, 0.011, 0.022):
        e += (t >= off) * np.exp(-(t - off).clip(0) * 140) * 0.8
    return noise * e * 1.4


def hat(open_=False):
    n = int((0.22 if open_ else 0.06) * SR)
    t = np.arange(n) / SR
    return hp(rng.uniform(-1, 1, n), 7500, 4) * np.exp(-t * (14 if open_ else 70))


def crash(dur=2.2):
    n = int(dur * SR)
    t = np.arange(n) / SR
    return hp(rng.uniform(-1, 1, n), 3500, 2) * np.exp(-t * 2.2) * 0.8


def pluck(m, dur=0.22, cutoff=3800, detune=(-9, 0, 9)):
    x = saw(midi(m), dur, detune)
    x = lp(x, cutoff)
    return x * env(len(x), 0.003, 0.09, 0.0, 0.03)


def bass(m, dur=0.22):
    f = midi(m)
    t = np.arange(int(dur * SR)) / SR
    x = lp(saw(f, dur, (0,), 20), 700) * 0.8 + np.sin(2 * np.pi * f * t) * 0.7
    return x * env(len(x), 0.004, 0.25, 0.6, 0.04)


def pad(ms, dur):
    x = sum(saw(midi(m), dur, (-12, 0, 12), 24) for m in ms)
    x = lp(x, 1400)
    return x * env(len(x), 0.6, 10, 1.0, 0.8)


def riser(dur):
    n = int(dur * SR)
    t = np.arange(n) / SR
    noise = rng.uniform(-1, 1, n)
    out = np.zeros(n)
    chunks = 60
    for c in range(chunks):
        a, b = c * n // chunks, (c + 1) * n // chunks
        fc = 400 * (12000 / 400) ** (c / chunks)
        seg = bp(noise[max(0, a - 2000):b], fc * 0.7, min(fc * 1.4, 20000))[-(b - a):]
        out[a:b] = seg
    f = 220 * 2 ** (2.5 * t / dur)
    tone = np.sin(2 * np.pi * np.cumsum(f) / SR) * 0.25
    return (out * 1.6 + tone) * (t / dur) ** 2


# ---------------- musique ----------------
music = np.zeros((2, N))
chords = [  # ré majeur : I – V – vi – IV
    ([62, 66, 69, 74], 38),
    ([61, 64, 69, 73], 45),
    ([62, 66, 71, 74], 47),
    ([62, 67, 71, 74], 43),
]
DROP, OUT = T["figures"], T["outro"]
K, CL, HC, HO = kick(), clap(), hat(), hat(True)
sc = np.ones(N)  # side-chain (pompe) appliquée aux nappes et à la basse
melodic = np.zeros((2, N))

n_beats = int(END / BEAT)
for b in range(n_beats):
    t = b * BEAT
    bar, beat_in_bar = divmod(b, 4)
    ch, root = chords[bar % 4]
    groove = DROP <= t < OUT
    light = T["crawl"] <= t < T["crawl"] + 8  # respiration au début du défilé
    if groove or (2.0 <= t < DROP):
        if groove or t >= 3.0:
            place(music, K, t, 0.9)
            i = int(t * SR)
            k = np.arange(min(int(0.3 * SR), N - i)) / SR
            sc[i:i + len(k)] = np.minimum(sc[i:i + len(k)], 1 - 0.55 * np.exp(-k * 9))
        place(music, HC, t + 0.25, 0.22, 0.25)
        if groove:
            if beat_in_bar in (1, 3):
                place(music, CL, t, 0.42, -0.05)
            for s16 in (0.125, 0.375):
                place(music, HC, t + s16, 0.08, -0.3)
            if beat_in_bar == 3 and bar % 2 == 1:
                place(music, HO, t + 0.25, 0.16, 0.2)
    if groove:
        # basse en croches décalées
        for e in (0.25,):
            place(melodic, bass(root), t + e, 0.55)
        if beat_in_bar == 0:
            place(melodic, bass(root), t, 0.45)
        # accords plaqués syncopés : 1, 2&, 4
        for pos in ((0, 0.0), (1, 0.25), (3, 0.0)):
            if beat_in_bar == pos[0] and not light:
                for m in ch:
                    place(melodic, pluck(m, 0.24, 3200), t + pos[1], 0.11, (m % 5 - 2) * 0.12)
        # arpège en doubles croches (sections énergiques)
        if (T["top"] <= t < T["crawl"]) or (T["crawl"] + 16 <= t < OUT - 1):
            notes = [ch[0] + 12, ch[1] + 12, ch[2] + 12, ch[3] + 12]
            for s in range(4):
                m = notes[(b * 4 + s) % 4]
                place(melodic, pluck(m, 0.12, 5200, (-4, 4)), t + s * 0.125, 0.06, 0.35 if s % 2 else -0.35)

# nappes : intro, respiration du défilé, outro
for bar in range(int(END / 2)):
    t = bar * 2.0
    ch, _ = chords[bar % 4]
    if t < DROP:
        place(melodic, pad(ch, 2.2), t, 0.11 if t >= 2 else 0.08)
    elif T["crawl"] <= t < T["crawl"] + 8:
        place(melodic, pad(ch, 2.2), t, 0.07)
# accord final tenu (fondu terminé avant la fin)
fin = pad([50, 62, 66, 69, 74], END - OUT)
fin *= np.clip((END - 0.25 - OUT - np.arange(len(fin)) / SR) / 2.5, 0, 1)
place(melodic, fin, OUT, 0.13)
place(melodic, bass(38, 2.5) * np.linspace(1, 0, int(2.5 * SR)), OUT, 0.5)
for m in [62, 66, 69, 74, 78]:
    place(melodic, pluck(m, 1.2, 4200), OUT, 0.08)

# montées et crashs
place(music, riser(2.0), DROP - 2.0, 0.22)
place(music, crash(), DROP, 0.28)
place(music, riser(1.5), T["top"] - 1.5, 0.18)
place(music, crash(), T["top"], 0.3)
place(music, riser(1.5), OUT - 1.5, 0.2)
place(music, crash(3.0), OUT, 0.32)
place(music, K, OUT, 1.0)
# roulement de clap avant le drop
for i in range(8):
    place(music, CL, DROP - 1.0 + i * 0.125, 0.12 + i * 0.03)

music += melodic * sc
# fondu de sécurité sur la fin : silence total sur la dernière image
tail = np.clip((END - 0.15 - np.arange(N) / SR) / 0.6, 0, 1)
music *= tail
music = np.tanh(music * 1.1)
music *= 0.5 / np.max(np.abs(music))

# ---------------- effets sonores ----------------
sfx = np.zeros((2, N))


def whoosh(dur=0.6, up=True):
    n = int(dur * SR)
    t = np.arange(n) / SR
    noise = rng.uniform(-1, 1, n)
    out = np.zeros(n)
    chunks = 30
    for c in range(chunks):
        a, b = c * n // chunks, (c + 1) * n // chunks
        x = c / chunks
        fc = 300 * (6000 / 300) ** (x if up else 1 - x)
        out[a:b] = bp(noise[max(0, a - 1500):b], fc * 0.6, min(fc * 1.6, 20000))[-(b - a):]
    e = np.sin(np.pi * np.clip(t / dur, 0, 1)) ** 2
    return out * e * 2.2


def pop(f0=880, f1=520, dur=0.14):
    n = int(dur * SR)
    t = np.arange(n) / SR
    f = f1 + (f0 - f1) * np.exp(-t * 40)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 28)


def tick(f=2600, dur=0.03):
    n = int(dur * SR)
    t = np.arange(n) / SR
    return np.sin(2 * np.pi * f * t) * np.exp(-t * 180)


def bell(f=1318.5, dur=1.6):
    n = int(dur * SR)
    t = np.arange(n) / SR
    x = sum(a * np.sin(2 * np.pi * f * r * t) * np.exp(-t * d) for r, a, d in
            ((1, 1, 3), (2.76, 0.4, 5), (5.4, 0.2, 8), (0.5, 0.3, 2.5)))
    return x * 0.5


def impact(dur=1.4):
    n = int(dur * SR)
    t = np.arange(n) / SR
    f = 38 + 60 * np.exp(-t * 12)
    boom = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 3.2)
    hit = lp(rng.uniform(-1, 1, n), 2500) * np.exp(-t * 14)
    return np.tanh((boom * 1.2 + hit * 0.6) * 1.4)


def wipe_sfx(at, kind):
    lead = 0.5 if kind == "orange" else 0.42
    w = whoosh(0.75 if kind == "orange" else 0.6)
    # léger panoramique gauche -> droite, comme les volets
    n = len(w)
    pan = np.linspace(-0.7, 0.7, n)
    i = int((at - lead - 0.05) * SR)
    gl, gr = np.cos((pan + 1) * np.pi / 4), np.sin((pan + 1) * np.pi / 4)
    g = 0.5 if kind == "orange" else 0.34
    sfx[0, i:i + n] += w * gl * g * 1.414
    sfx[1, i:i + n] += w * gr * g * 1.414


# intro
place(sfx, whoosh(0.5), 0.15, 0.2, -0.4)
place(sfx, pop(700, 380), 0.25, 0.3)
place(sfx, pop(1100, 650), 0.7, 0.22, 0.3)
for i in range(3):
    place(sfx, whoosh(0.35), 0.82 + i * 0.2, 0.12, -0.2 + i * 0.2)
# volets
for at, kind in ((T["figures"], "orange"), (T["top"], "orange"), (T["t6"], "blue"),
                 (T["t5"], "blue"), (T["t4"], "blue"), (T["t3"], "blue"),
                 (T["crawl"], "orange"), (T["outro"], "orange")):
    wipe_sfx(at, kind)
# chiffres : tic à chaque incrément (espacement mini 40 ms)
F = T["figures"]
for i, val in enumerate((D["stats"]["count"], D["stats"]["total"], D["stats"]["max"])):
    at = F + 0.85 + i * 0.45 + 0.05
    last_v, last_t = 0, -1
    for s in range(int(1.7 * 1000)):
        tt = s / 1000
        v = round(val * (1 - (1 - tt / 1.7) ** 3))
        if v != last_v and tt - last_t >= 0.04:
            place(sfx, tick(2200 + 500 * i), at + tt, 0.10, -0.5 + 0.5 * i)
            last_v, last_t = v, tt
    place(sfx, pop(1300, 900, 0.18), at + 1.7, 0.18, -0.5 + 0.5 * i)
# top
TP = T["top"]
place(sfx, impact(), TP, 0.55)
top = D["tiers"][0]["people"]
gap = 1.1 if len(top) > 2 else 1.6
for i in range(len(top)):
    at = TP + 1.0 + i * gap
    place(sfx, whoosh(0.5), at - 0.1, 0.22, -0.3)
    place(sfx, pop(950, 560, 0.18), at + 0.45, 0.4)
    place(sfx, bell(1760, 1.0), at + 0.5, 0.1, 0.2)
if len(top) > 1:
    place(sfx, impact(0.8), TP + 1.0 + (len(top) - 1) * gap + 1.3, 0.35)
    place(sfx, bell(1318.5), TP + 1.0 + (len(top) - 1) * gap + 1.3, 0.16)
# paliers intermédiaires
starts = [T["t6"], T["t5"], T["t4"], T["t3"]]
for ti, tier in enumerate(D["tiers"][1:5]):
    S = starts[ti]
    n = len(tier["people"])
    place(sfx, pop(800, 450, 0.16), S + 0.3, 0.32)
    if n > 6:
        h = (n + 1) // 2
        for k in range(h):
            place(sfx, tick(3000, 0.025), S + 0.7 + k * 0.07, 0.07, -0.4 + 0.8 * (k % 3) / 2)
        place(sfx, whoosh(0.45, up=False), T["t3page2"] - 0.5, 0.16, 0.3)
        for k in range(n - h):
            place(sfx, tick(3000, 0.025), T["t3page2"] + k * 0.07, 0.07, -0.4 + 0.8 * (k % 3) / 2)
    else:
        stg = 0 if n == 1 else (0.3 if n <= 3 else 0.18)
        for k in range(n):
            place(sfx, pop(1000 + 60 * k, 620, 0.14), S + 0.75 + k * stg, 0.26, -0.4 + 0.8 * (k % 3) / 2)
# outro
O = T["outro"]
place(sfx, impact(1.8), O, 0.5)
place(sfx, bell(1174.7, 2.4), O + 0.65, 0.18)
place(sfx, pop(900, 600, 0.18), O + 1.2, 0.25)

sfx *= np.clip((END - 0.15 - np.arange(N) / SR) / 0.6, 0, 1)
sfx *= 0.55 / np.max(np.abs(sfx))


def write(path, x):
    path.parent.mkdir(parents=True, exist_ok=True)
    pcm = (np.clip(x.T, -1, 1) * 32767).astype("<i2")
    with wave.open(str(path), "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())


write(HERE / "assets/audio/music.wav", music)
write(HERE / "assets/audio/sfx.wav", sfx)
print("ok", END, "s")
