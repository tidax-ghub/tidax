#!/usr/bin/env python3
"""Clash Neuf vs Ancien : voix (Kokoro TTS + effets), instru hip-hop synthétisée,
mixage final et données de timing pour la composition.
Entrée : lyrics.json. Sorties : assets/audio/mix.wav et src/data.js.
"""
import json
import subprocess
import wave
from pathlib import Path

import numpy as np
from scipy.signal import butter, sosfilt

HERE = Path(__file__).resolve().parent
SR = 44100
L = json.loads((HERE / "lyrics.json").read_text())
BPM = L["bpm"]
BEAT = 60 / BPM
BAR = 4 * BEAT
STEP = BEAT / 4
HALF = BAR / 2
VOICE_DIR = HERE / "assets" / "voice"
AUDIO_DIR = HERE / "assets" / "audio"
VOICE_DIR.mkdir(parents=True, exist_ok=True)
AUDIO_DIR.mkdir(parents=True, exist_ok=True)
rng = np.random.default_rng(2020)

# Timbre de chaque rappeur : décalage de hauteur (ratio) + couleur.
FX = {
    "ancien": "rubberband=pitch=0.76,highpass=f=90,lowpass=f=6500,acompressor=threshold=0.1:ratio=4:attack=5:release=80,volume=1.6",
    "neuf": "rubberband=pitch=0.9,highpass=f=110,treble=g=3,acompressor=threshold=0.1:ratio=4:attack=5:release=80,volume=1.5",
    "mc": "rubberband=pitch=0.68,highpass=f=80,acompressor=threshold=0.1:ratio=5:attack=5:release=80,aecho=0.8:0.6:90:0.25,volume=1.7",
}
MAX_LINE = {"ancien": 2.5, "neuf": 2.5, "mc": 3.6}


def lp(x, fc, order=2):
    return sosfilt(butter(order, fc, "low", fs=SR, output="sos"), x)


def hp(x, fc, order=2):
    return sosfilt(butter(order, fc, "high", fs=SR, output="sos"), x)


def bp(x, lo, hi, order=2):
    return sosfilt(butter(order, [lo, hi], "band", fs=SR, output="sos"), x)


def read_wav(p):
    with wave.open(str(p)) as w:
        a = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768
        if w.getnchannels() == 2:
            a = a.reshape(-1, 2).mean(1)
    return a


def write_wav(p, x):
    x = np.clip(x, -1, 1)
    st = (np.stack([x, x], 1) * 32767).astype(np.int16) if x.ndim == 1 else (x * 32767).astype(np.int16)
    with wave.open(str(p), "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(st.tobytes())


def trim(x, thr=0.02):
    idx = np.where(np.abs(x) > thr)[0]
    if not len(idx):
        return x
    return x[max(idx[0] - int(0.02 * SR), 0): idx[-1] + int(0.06 * SR)]


# ---------- Voix ----------
def make_voice(i, line):
    raw = VOICE_DIR / f"raw_{i:02d}.wav"
    out = VOICE_DIR / f"line_{i:02d}.wav"
    if not raw.exists():
        subprocess.run(["npx", "-y", "hyperframes", "tts", line["say"], "-v", "ff_siwis", "-l", "fr-fr",
                        "-s", "1.12", "-o", str(raw)], check=True, capture_output=True)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(raw), "-af",
                    FX[line["who"]], "-ar", str(SR), "-ac", "1", str(out)], check=True)
    v = trim(read_wav(out))
    dur = len(v) / SR
    lim = MAX_LINE[line["who"]]
    if dur > lim:  # on resserre le débit pour tenir dans la mesure
        tmp = VOICE_DIR / f"fit_{i:02d}.wav"
        write_wav(tmp, v)
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(tmp), "-af",
                        f"rubberband=tempo={min(dur / lim, 1.35):.3f}", "-ac", "1", str(out)], check=True)
        v = read_wav(out)
        tmp.unlink()
    return v


def chunk_times(show, start, dur):
    weights = [max(len(s.replace(" ", "")), 3) for s in show]
    tot = sum(weights)
    t, res = start, []
    for s, w in zip(show, weights):
        d = dur * w / tot
        res.append({"text": s, "start": round(t, 3), "end": round(t + d, 3)})
        t += d
    return res


voices, timing = [], []
t = 0.45
prev = None
for i, line in enumerate(L["lines"]):
    v = make_voice(i, line)
    if prev is not None:
        t = prev
        if line["who"] != L["lines"][i - 1]["who"]:
            t += HALF  # respiration entre deux intervenants
        t = np.ceil((t - 0.02) / HALF) * HALF  # cale sur la demi-mesure
    dur = len(v) / SR
    voices.append((t, v, line["who"]))
    timing.append({"who": line["who"], "start": round(float(t), 3), "end": round(float(t + dur), 3),
                   "chunks": chunk_times(line["show"], float(t), dur)})
    prev = t + dur + 0.08
    print(f"{i:02d} {line['who']:6s} {t:6.2f}s → {t + dur:6.2f}s  {line['say']}")

END = timing[-1]["end"] + 2 * BAR
END = float(np.ceil(END / BAR) * BAR)
N = int(END * SR)


# ---------- Instru (Am – F – G – Em, 90 BPM) ----------
def env(n, a, d):
    e = np.exp(-np.arange(n) / (d * SR))
    k = int(a * SR)
    if k:
        e[:k] *= np.linspace(0, 1, k)
    return e


def kick():
    n = int(0.45 * SR)
    tt = np.arange(n) / SR
    f = 45 + 95 * np.exp(-tt * 28)
    s = np.sin(2 * np.pi * np.cumsum(f) / SR) * env(n, 0.002, 0.18)
    s[:200] += rng.normal(0, 0.3, 200) * np.linspace(1, 0, 200)
    return np.tanh(s * 1.6)


def snare():
    n = int(0.3 * SR)
    noise = bp(rng.normal(0, 1, n), 1200, 7000) * env(n, 0.001, 0.07)
    tt = np.arange(n) / SR
    body = np.sin(2 * np.pi * 190 * tt) * env(n, 0.001, 0.05)
    return 0.8 * noise + 0.6 * body


def hat(open_=False):
    n = int((0.25 if open_ else 0.06) * SR)
    return hp(rng.normal(0, 1, n), 7500) * env(n, 0.0005, 0.08 if open_ else 0.018)


def clap():
    n = int(0.25 * SR)
    x = bp(rng.normal(0, 1, n), 900, 5000)
    e = np.zeros(n)
    for o in (0, 0.012, 0.024):
        k = int(o * SR)
        e[k:] += env(n - k, 0.0005, 0.03 if o < 0.02 else 0.09)
    return x * e * 0.7


ROOTS = [55.0, 43.65, 49.0, 41.2]  # A1 F1 G1 E1
CHORDS = [[220.0, 261.63, 329.63], [174.61, 220.0, 261.63], [196.0, 246.94, 293.66], [164.81, 196.0, 246.94]]


def keys(freqs, dur):
    n = int(dur * SR)
    tt = np.arange(n) / SR
    s = np.zeros(n)
    for f in freqs:
        for h, a in ((1, 1), (2, 0.35), (3, 0.12)):
            s += a * np.sin(2 * np.pi * f * h * tt) * np.exp(-tt * (1.5 + h))
    return s * env(n, 0.005, 10) / len(freqs)


def bass(f, dur):
    n = int(dur * SR)
    tt = np.arange(n) / SR
    s = np.sin(2 * np.pi * f * tt) + 0.25 * np.sin(2 * np.pi * 2 * f * tt)
    return np.tanh(2.2 * s * env(n, 0.004, 0.9)) * 0.9


def place(buf, x, at, g=1.0):
    k = int(at * SR)
    if k >= len(buf):
        return
    m = min(len(x), len(buf) - k)
    buf[k:k + m] += g * x[:m]


drums = np.zeros(N)
music = np.zeros(N)
K, S, CL = kick(), snare(), clap()
KICK_STEPS = [0, 7, 10]
bars = int(END / BAR)
mc_windows = [(l["start"] - 0.2, l["end"] + 0.3) for l in timing if l["who"] == "mc"]


def in_mc(tt):
    return any(a <= tt <= b for a, b in mc_windows)


for b in range(bars):
    t0 = b * BAR
    ci = b % 4
    place(music, keys(CHORDS[ci], BAR), t0, 0.32)
    place(music, keys([c * 2 for c in CHORDS[ci]], BEAT * 1.5), t0 + BEAT * 2.5, 0.12)
    full = b >= 1 and b < bars - 1
    for st in range(16):
        tt = t0 + st * STEP
        soft = in_mc(tt)
        if full and st in KICK_STEPS and not soft:
            place(drums, K, tt, 0.95)
            place(music, bass(ROOTS[ci], BEAT * (1.7 if st == 0 else 0.9)), tt, 0.55)
        if full and st in (4, 12):
            place(drums, S, tt, 0.6 if soft else 0.75)
            place(drums, CL, tt, 0.5)
        if st % 2 == 0 or (st in (13, 15) and b % 2):
            place(drums, hat(open_=(st == 14 and b % 2 == 1)), tt, 0.22 if st % 4 == 0 else 0.14)
    if b == 0:  # montée d'intro
        place(drums, K, t0, 0.8)


# Corne de brume (air horn) à chaque entrée de couplet + foule.
def air_horn():
    n = int(0.42 * SR)
    tt = np.arange(n) / SR
    s = np.zeros(n)
    for f in (311, 466, 622):
        ph = 2 * np.pi * f * tt * (1 + 0.004 * np.sin(2 * np.pi * 6 * tt))
        s += np.sign(np.sin(ph)) * 0.5 + (2 * ((f * tt) % 1) - 1) * 0.5
    s = lp(s, 3500) * env(n, 0.01, 1.0)
    s[-int(0.06 * SR):] *= np.linspace(1, 0, int(0.06 * SR))
    return np.tanh(s * 0.6) * 0.5


def crowd(dur):
    n = int(dur * SR)
    x = bp(rng.normal(0, 1, n), 300, 2500, 3)
    tt = np.arange(n) / SR
    mod = 0.6 + 0.4 * np.sin(2 * np.pi * 3.3 * tt) * np.sin(2 * np.pi * 0.7 * tt)
    shape = np.minimum(tt / 0.25, 1) * np.exp(-np.maximum(tt - 0.6, 0) * 1.8)
    return x * mod * shape * 0.5


sfx = np.zeros(N)
horns = []
for i, l in enumerate(timing):
    if l["who"] in ("ancien", "neuf") and (i == 0 or timing[i - 1]["who"] != l["who"]):
        at = l["start"] - HALF * 0.9
        horns.append(round(at, 3))
        for k, o in enumerate((0, 0.12, 0.24)):
            place(sfx, air_horn()[: int((0.1 if k < 2 else 0.42) * SR)], at + o, 0.8)
    if l["who"] == "mc":
        place(sfx, crowd(3.0), l["end"] - 0.3, 0.55)
place(sfx, crowd(3.5), 0.0, 0.35)

vox = np.zeros(N)
for t, v, _ in voices:
    place(vox, v, t, 1.0)

# Pompe légère de l'instru sous la voix (ducking).
venv = np.convolve(np.abs(vox), np.ones(int(0.05 * SR)) / int(0.05 * SR), "same")
duck = 1 - 0.35 * np.clip(venv * 8, 0, 1)
bed = (0.9 * drums + 0.8 * music) * duck
mix = 0.55 * bed + 0.95 * vox + 0.5 * sfx
fade = int(1.2 * SR)
mix[-fade:] *= np.linspace(1, 0, fade)
mix = np.tanh(mix * 1.1) / np.tanh(1.1)
mix *= 0.89 / np.max(np.abs(mix))
write_wav(AUDIO_DIR / "mix.wav", mix)

# Enveloppe de bouche par intervenant (15 i/s).
FPS = 15
mouth = {}
for who in ("ancien", "neuf", "mc"):
    track = np.zeros(N)
    for t, v, w in voices:
        if w == who:
            place(track, v, t)
    hop = SR // FPS
    frames = len(track) // hop
    rms = np.array([np.sqrt(np.mean(track[k * hop:(k + 1) * hop] ** 2)) for k in range(frames)])
    rms = rms / (np.percentile(rms[rms > 0.005], 90) if np.any(rms > 0.005) else 1)
    mouth[who] = [round(float(min(r, 1.0)), 2) for r in rms]

data = {"duration": round(END, 3), "bpm": BPM, "bar": BAR, "fps": FPS, "lines": timing,
        "horns": horns, "mouth": mouth}
(HERE / "src").mkdir(exist_ok=True)
(HERE / "src" / "data.js").write_text("window.CLASH = " + json.dumps(data, ensure_ascii=False) + ";\n")
print(f"durée {END:.2f}s, cornes {horns}")
