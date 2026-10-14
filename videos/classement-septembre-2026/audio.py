#!/usr/bin/env python3
"""Monte la musique (Cosmonkey – Old Sneakers) et synthétise les effets sonores,
calés sur le découpage de data.json.
Sorties : assets/audio/music_edit.wav et assets/audio/sfx.wav.
"""
import json
import subprocess
import wave
from pathlib import Path

import numpy as np
from scipy.signal import butter, sosfilt

HERE = Path(__file__).resolve().parent
SR = 48000
D = json.loads((HERE / "data.json").read_text())
T = D["T"]
B = T["beat"]
END = T["end"]
N = int(END * SR)
rng = np.random.default_rng(2026)


def lp(x, fc, order=2):
    return sosfilt(butter(order, fc, "low", fs=SR, output="sos"), x)


def bp(x, lo, hi, order=2):
    return sosfilt(butter(order, [lo, hi], "band", fs=SR, output="sos"), x)


def place(buf, x, at, gain=1.0, pan=0.0):
    i = int(round(at * SR))
    if i >= buf.shape[1]:
        return
    n = min(len(x), buf.shape[1] - i)
    l, r = np.cos((pan + 1) * np.pi / 4), np.sin((pan + 1) * np.pi / 4)
    buf[0, i:i + n] += x[:n] * gain * l * 1.414
    buf[1, i:i + n] += x[:n] * gain * r * 1.414


# ---------------- musique : montage sur la grille du morceau ----------------
raw = subprocess.run(
    ["ffmpeg", "-v", "error", "-i", str(HERE / "assets/music/old-sneakers.mp3"),
     "-f", "f32le", "-ac", "2", "-ar", str(SR), "-"],
    check=True, capture_output=True).stdout
song = np.frombuffer(raw, np.float32).reshape(-1, 2).T.astype(np.float64)

XF = int(0.03 * SR)  # fondu enchaîné de 30 ms au point de coupe (même position de phrase)
music = np.zeros((2, N))
pos = 0
for si, (a, b) in enumerate(D["music"]):
    seg = song[:, int(round(a * SR)):int(round(b * SR))].copy()
    if si == 0:
        seg[:, :int(0.02 * SR)] *= np.linspace(0, 1, int(0.02 * SR))
    if si > 0:
        pre = song[:, int(round(a * SR)) - XF:int(round(a * SR))]
        fade = np.linspace(0, 1, XF)
        music[:, pos - XF:pos] = music[:, pos - XF:pos] * (1 - fade) + pre * fade
    n = min(seg.shape[1], N - pos)
    music[:, pos:pos + n] = seg[:, :n]
    pos += n
t = np.arange(N) / SR
fade_end = END - 0.3
music *= np.clip((fade_end - t) / 2.4, 0, 1)  # fondu de sortie, silence sur la fin
music *= 0.89  # marge de crête pour le mixage avec les effets

# ---------------- effets sonores ----------------
sfx = np.zeros((2, N))


def whoosh(dur=0.6, up=True, lo=300, hi=6000):
    n = int(dur * SR)
    tt = np.arange(n) / SR
    noise = rng.uniform(-1, 1, n)
    out = np.zeros(n)
    chunks = 30
    for c in range(chunks):
        a, b = c * n // chunks, (c + 1) * n // chunks
        x = c / chunks
        fc = lo * (hi / lo) ** (x if up else 1 - x)
        out[a:b] = bp(noise[max(0, a - 1500):b], fc * 0.6, min(fc * 1.6, 20000))[-(b - a):]
    e = np.sin(np.pi * np.clip(tt / dur, 0, 1)) ** 2
    return out * e * 2.2


def pop(f0=880, f1=520, dur=0.14):
    n = int(dur * SR)
    tt = np.arange(n) / SR
    f = f1 + (f0 - f1) * np.exp(-tt * 40)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt * 28)


def tick(f=2600, dur=0.03):
    n = int(dur * SR)
    tt = np.arange(n) / SR
    return np.sin(2 * np.pi * f * tt) * np.exp(-tt * 180)


def bell(f=1318.5, dur=1.6):
    n = int(dur * SR)
    tt = np.arange(n) / SR
    return 0.5 * sum(a * np.sin(2 * np.pi * f * r * tt) * np.exp(-tt * d) for r, a, d in
                     ((1, 1, 3), (2.76, 0.4, 5), (5.4, 0.2, 8), (0.5, 0.3, 2.5)))


def impact(dur=1.4):
    n = int(dur * SR)
    tt = np.arange(n) / SR
    f = 38 + 60 * np.exp(-tt * 12)
    boom = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt * 3.2)
    hit = lp(rng.uniform(-1, 1, n), 2500) * np.exp(-tt * 14)
    return np.tanh((boom * 1.2 + hit * 0.6) * 1.4)


def sparkle(dur=1.4, seed=1):
    r = np.random.default_rng(seed)
    out = np.zeros(int(dur * SR))
    for _ in range(18):
        at = r.uniform(0, dur * 0.7)
        x = bell(r.uniform(2400, 4200), 0.5) * r.uniform(0.2, 0.5)
        i = int(at * SR)
        n = min(len(x), len(out) - i)
        out[i:i + n] += x[:n]
    return out


def pan_whoosh(at, dur, gain, up=True):
    w = whoosh(dur, up)
    n = len(w)
    pan = np.linspace(-0.7, 0.7, n)
    i = int(at * SR)
    gl, gr = np.cos((pan + 1) * np.pi / 4), np.sin((pan + 1) * np.pi / 4)
    sfx[0, i:i + n] += w * gl * gain * 1.414
    sfx[1, i:i + n] += w * gr * gain * 1.414


A, TOP, T6 = T["figures"], T["top"], T["t6"]
# intro
place(sfx, whoosh(0.6), 0.15, 0.12, -0.4)
place(sfx, pop(1100, 650), 1.0, 0.10, 0.2)
place(sfx, pop(1300, 800), 1.1, 0.08, 0.3)
for i in range(3):
    place(sfx, whoosh(0.35), 1.2 + i * 0.32, 0.07, -0.2 + i * 0.2)
# iris
place(sfx, whoosh(0.8, True, 200, 4000), A - 0.75, 0.2)
# compteurs : petits tics
for i, val in enumerate((D["stats"]["count"], D["stats"]["total"], D["stats"]["max"])):
    at = A + 2 * B + i * 2 * B
    for k in range(14):
        place(sfx, tick(2300 + 400 * i), at + 1.4 * (1 - (1 - k / 14) ** 2), 0.05, -0.5 + 0.5 * i)
# plongée dans le 8
place(sfx, whoosh(0.9, True, 150, 9000), TOP - 0.9, 0.24)
place(sfx, impact(1.0), TOP, 0.3)
# top
top = D["tiers"][0]["people"]
gap = 4 * B if len(top) > 2 else 8 * B
for i in range(len(top)):
    at = TOP + 4 * B + i * gap
    place(sfx, impact(0.6), at, 0.18)
    place(sfx, pop(950, 560, 0.18), at + 2 * B, 0.22)
    place(sfx, bell(1760, 1.0), at + 2 * B + 0.05, 0.06, 0.2)
if len(top) > 1:
    st = TOP + 4 * B + len(top) * gap
    place(sfx, impact(0.9), st, 0.3)
    place(sfx, sparkle(1.6, 3), st + 0.05, 0.12, 0.4)
# volets obliques
pan_whoosh(T6 - 0.55, 0.9, 0.24)
# paliers : roulement du badge + cartes
starts = [T["t6"], T["t5"], T["t4"], T["t3"], T["crawlA"], T["crawlB"]]
for i, S in enumerate(starts):
    if i == 0:
        place(sfx, pop(800, 450, 0.16), S + 0.15, 0.16)
    else:
        place(sfx, whoosh(0.4, False, 600, 5000), S - 0.3, 0.08, -0.5)
        place(sfx, pop(700, 420, 0.14), S + 0.3, 0.12, -0.5)
for ti, tier in enumerate(D["tiers"][1:5]):
    S = starts[ti]
    n = len(tier["people"])
    if n > 6:
        h = (n + 1) // 2
        for k in range(h):
            place(sfx, tick(3000, 0.025), S + 0.25 + k * B / 2, 0.04, -0.4 + 0.8 * (k % 3) / 2)
        place(sfx, whoosh(0.45, up=False), T["t3page2"] - 0.6, 0.08, 0.3)
        for k in range(n - h):
            place(sfx, tick(3000, 0.025), T["t3page2"] + 0.05 + k * B / 2, 0.04, -0.4 + 0.8 * (k % 3) / 2)
    else:
        stg = 0 if n == 1 else B
        for k in range(n):
            place(sfx, pop(1000 + 60 * k, 620, 0.14), S + 0.3 + k * stg, 0.1, -0.4 + 0.8 * (k % 3) / 2)
# retour de la musique sur le second défilé
place(sfx, whoosh(1.0, True, 150, 8000), T["crawlB"] - 1.0, 0.16)
place(sfx, impact(1.2), T["crawlB"], 0.26)
# outro
O = T["outro"]
place(sfx, whoosh(0.7, True, 200, 8000), O - 0.7, 0.16)
place(sfx, impact(1.6), O, 0.3)
place(sfx, sparkle(1.8, 5), O + 4 * B + 0.5, 0.14)
place(sfx, bell(1174.7, 2.0), T["tail"] + 0.5, 0.08)

sfx *= np.clip((END - 0.3 - t) / 0.6, 0, 1)
peak = np.max(np.abs(sfx))
sfx *= min(1.0, 0.5 / peak)

mix_peak = np.max(np.abs(music + sfx))
if mix_peak > 0.97:
    music *= 0.97 / mix_peak
    sfx *= 0.97 / mix_peak


def write(path, x):
    path.parent.mkdir(parents=True, exist_ok=True)
    pcm = (np.clip(x.T, -1, 1) * 32767).astype("<i2")
    with wave.open(str(path), "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())


write(HERE / "assets/audio/music_edit.wav", music)
write(HERE / "assets/audio/sfx.wav", sfx)
old = HERE / "assets/audio/music.wav"
if old.exists():
    old.unlink()
print("ok", END, "s")
