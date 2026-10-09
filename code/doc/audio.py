"""Mixage : voix (accélérée + timbre modifié) + musique ducking + effets sonores sur les coupes."""
import json, subprocess, wave, numpy as np, os
HERE = os.path.dirname(os.path.abspath(__file__)); M = HERE + "/media/"; SR = 48000
ev = json.load(open(HERE + "/events.json")); DUR = ev["dur"]

def run(*a): subprocess.run(list(a), check=True)
# 1) voix : x1.08, -1,4 demi-ton (timbre déplacé = moins reconnaissable), EQ chaleur/présence, compression
run("ffmpeg", "-y", "-loglevel", "error", "-i", M + "voice.mp3", "-af",
    "aresample=48000,rubberband=tempo=1.08:pitch=0.922:transients=crisp,highpass=f=70,"
    "equalizer=f=160:t=q:w=1:g=2.5,equalizer=f=3200:t=q:w=1.2:g=2,equalizer=f=7000:t=q:w=1:g=-1.5,"
    "acompressor=threshold=-20dB:ratio=3:attack=5:release=80:makeup=3,adelay=500|500,apad",
    "-t", f"{DUR:.3f}", "-ac", "1", "-ar", "48000", HERE + "/voice_fx.wav")

# 2) effets synthétiques
n = int(DUR * SR); fx = np.zeros(n); rg = np.random.default_rng(7)
def tt(m): return np.arange(m) / SR
def add(t, sig, g):
    a = int(t * SR); e = min(n, a + len(sig))
    if 0 <= a < n: fx[a:e] += g * sig[:e - a]
def lp(x, k): return np.convolve(x, np.ones(k) / k, mode="same")
def whoosh():
    m = int(0.45 * SR); x = lp(rg.normal(0, 1, m), 30); env = np.sin(np.pi * np.arange(m) / m) ** 2
    return x * env * np.linspace(0.6, 1.0, m)
def hit():
    m = int(0.9 * SR); x = tt(m)
    boom = np.sin(2 * np.pi * (48 + 40 * np.exp(-x * 18)) * x) * np.exp(-x * 4.5)
    click = lp(rg.normal(0, 1, m), 4) * np.exp(-x * 45) * 0.5
    return boom + click
def pop():
    m = int(0.12 * SR); x = tt(m); return np.sin(2 * np.pi * (300 + 260 * np.exp(-x * 40)) * x) * np.exp(-x * 30)
def tick():
    m = int(0.04 * SR); x = tt(m); return np.sin(2 * np.pi * 2400 * x) * np.exp(-x * 120)
def riser(d=1.6):
    m = int(d * SR); x = tt(m); f = 200 + 1600 * (x / d) ** 2
    s = lp(rg.normal(0, 1, m), 6) * (x / d) ** 2.2 * 0.6 + np.sin(2 * np.pi * np.cumsum(f) / SR) * (x / d) ** 3 * 0.25
    return s
for kind, t in ev["events"]:
    if kind == "whoosh": add(t - 0.18, whoosh(), 0.20)
    elif kind == "hit": add(t, hit(), 0.55)
    elif kind == "pop": add(t, pop(), 0.12)
    elif kind == "tick": add(t, tick(), 0.10)
    elif kind == "riser": pass
for t in ev["riser"]: add(t, riser(), 0.35)
fx = fx / max(1e-6, np.abs(fx).max()) * 0.5
with wave.open(HERE + "/fx.wav", "wb") as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((fx * 32767).astype(np.int16).tobytes())

# 3) mix : musique ducking sous la voix, puis loudness -14 LUFS
fo = DUR - 3.5
run("ffmpeg", "-y", "-loglevel", "error", "-i", HERE + "/voice_fx.wav", "-i", M + "music.mp3", "-i", HERE + "/fx.wav",
    "-filter_complex",
    f"[1:a]aresample=48000,atrim=0:{DUR:.3f},volume=0.55,afade=t=in:d=0.6,afade=t=out:st={fo:.2f}:d=3.5[mus];"
    "[0:a]asplit=2[v1][vsc];"
    "[mus][vsc]sidechaincompress=threshold=0.03:ratio=6:attack=20:release=350:makeup=1[duck];"
    "[v1]volume=1.0,aformat=channel_layouts=stereo[v];[2:a]aformat=channel_layouts=stereo[f];"
    "[duck][v][f]amix=inputs=3:normalize=0:weights=1 1 0.8,loudnorm=I=-14:TP=-1.2:LRA=11[out]",
    "-map", "[out]", "-ar", "48000", "-ac", "2", "-t", f"{DUR:.3f}", HERE + "/mix.wav")
print("ok", DUR)
