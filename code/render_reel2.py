"""Reel Doctorgane n°2 — « Il y a 50 ans, on enlevait tout le sein » (sans voix, texte animé + sound design discret)
1080x1920, 30 fps, charte navy / crème / corail, Anton + Poppins. Aucun en-tête ni filigrane.
Usage: python3 render_reel2.py [--out reel2.mp4] [--frames dossier] [--no-audio]
"""
import sys, math, subprocess, os, argparse, wave
import numpy as np
from PIL import Image, ImageDraw, ImageFont

ap = argparse.ArgumentParser()
ap.add_argument("--out", default="reel2.mp4"); ap.add_argument("--frames"); ap.add_argument("--no-audio", action="store_true")
args = ap.parse_args()

W, H, FPS = 1080, 1920, 30
NAVY = (18, 33, 61); CREAM = (246, 241, 233); CORAL = (255, 111, 97)
GREY = (150, 160, 180); TRACK = (48, 68, 108)
FD = "/home/claude/fonts/"
ANTON = FD + "Anton-Regular.ttf"; POP = FD + "Poppins-SemiBold.ttf"; POPR = FD + "Poppins-Regular.ttf"

# ---------- minutage des scènes ----------
BOUNDS = [0.0, 3.6, 7.0, 12.0, 16.4, 21.0, 25.4, 30.0]   # 7 scènes
DUR = BOUNDS[-1]; NF = int(DUR * FPS)

# ---------- fond ----------
yy, xx = np.mgrid[0:H, 0:W]
d = np.sqrt(((xx - W / 2) / (W * 0.8)) ** 2 + ((yy - H * 0.45) / (H * 0.7)) ** 2)
k = np.clip(1 - d, 0, 1)[..., None]
BG = (np.array((12, 24, 48)) * (1 - k) + np.array((24, 44, 82)) * k).astype(np.uint8)
BGIMG = Image.fromarray(BG)
rng = np.random.default_rng(7)
GRAIN = [rng.normal(0, 3.2, (H, W, 1)).astype(np.float32) for _ in range(6)]

# ---------- outils ----------
_cache = {}
def layer(text, path, size, fill, maxw=None):
    key = (text, path, size, fill, maxw)
    if key in _cache: return _cache[key]
    f = ImageFont.truetype(path, size)
    if maxw:
        while f.getlength(text) > maxw and size > 20:
            size -= 4; f = ImageFont.truetype(path, size)
    l, t, r, b = f.getbbox(text)
    pad = 8
    im = Image.new("RGBA", (int(r - l) + 2 * pad, int(b - t) + 2 * pad), (0, 0, 0, 0))
    ImageDraw.Draw(im).text((pad - l, pad - t), text, font=f, fill=fill + (255,))
    _cache[key] = im; return im

def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))
def out_cubic(x): return 1 - (1 - x) ** 3
def out_back(x, s=1.5): x = x - 1; return 1 + (s + 1) * x ** 3 + s * x ** 2

def put(base, im, cx, cy, scale=1.0, alpha=1.0):
    if alpha <= 0.01 or scale <= 0.01: return
    if scale != 1.0:
        im = im.resize((max(1, int(im.width * scale)), max(1, int(im.height * scale))), Image.BILINEAR)
    if alpha < 1.0:
        im = im.copy(); im.putalpha(im.getchannel("A").point(lambda v: int(v * alpha)))
    base.alpha_composite(im, (int(cx - im.width / 2), int(cy - im.height / 2)))

def pop(base, im, cx, cy, lt, delay=0.0, dur=0.30, drift=0, fade_out=None):
    x = (lt - delay) / dur
    if x <= 0: return
    a = 1.0
    if fade_out is not None:  # (t_start, dur)
        a = 1 - clamp((lt - fade_out[0]) / fade_out[1])
    x = clamp(x)
    put(base, im, cx, cy + (1 - out_cubic(x)) * drift, 0.74 + 0.26 * out_back(x), clamp(x * 3) * a)

def ribbon(base, cx, cy, s, col, alpha=1.0):
    S = 3; ov = Image.new("RGBA", (int(s * 3 * S), int(s * 3 * S)), (0, 0, 0, 0)); dr = ImageDraw.Draw(ov)
    c = ov.width / 2; w = int(s * 0.24 * S); u = s * S
    dr.arc([c - .42 * u, c - 1.0 * u, c + .42 * u, c + .05 * u], 180, 360, fill=col + (255,), width=w)
    dr.line([(c - .40 * u, c - .48 * u), (c + .36 * u, c + .85 * u)], fill=col + (255,), width=w)
    dr.line([(c + .40 * u, c - .48 * u), (c - .36 * u, c + .85 * u)], fill=col + (255,), width=w)
    ov = ov.resize((ov.width // S, ov.height // S), Image.LANCZOS)
    put(base, ov, cx, cy, 1.0, alpha)

def T(text, font, size, col, y, delay, maxw=900): return dict(text=text, font=font, size=size, col=col, y=y, delay=delay, maxw=maxw)

# ---------- scènes : lignes de texte (aussi utilisées pour caler le son) ----------
SC = [
  # 1 accroche
  [T("IL Y A 50 ANS,", ANTON, 170, CREAM, 640, 0.00), T("ON ENLEVAIT", ANTON, 250, CREAM, 870, 0.38), T("TOUT LE SEIN.", ANTON, 270, CORAL, 1130, 0.85)],
  # 2 petite tumeur
  [T("MÊME POUR UNE TUMEUR", ANTON, 120, CREAM, 560, 0.0), T("DE MOINS DE 2 CM.", ANTON, 170, CORAL, 740, 0.45)],
  # 3 l'essai
  [T("ALORS DES MÉDECINS", ANTON, 120, CREAM, 450, 0.0), T("ONT COMPARÉ.", ANTON, 160, CORAL, 610, 0.3)],
  # 4 résultat
  [T("20 ANS PLUS TARD…", POP, 58, CREAM, 520, 0.0), T("LA MÊME", ANTON, 330, CREAM, 800, 0.8), T("SURVIE.", ANTON, 400, CORAL, 1120, 1.3)],
  # 5 radiothérapie
  [T("LE SECRET ?", POP, 62, CREAM, 520, 0.0), T("LA RADIOTHÉRAPIE.", ANTON, 190, CORAL, 740, 0.4), T("ELLE DIVISE PAR 2", ANTON, 150, CREAM, 1010, 1.4), T("LE RISQUE DE RECHUTE.", ANTON, 120, CREAM, 1170, 1.9)],
  # 6 aujourd'hui
  [T("AUJOURD'HUI,", POP, 66, CREAM, 560, 0.0), T("QUAND C'EST POSSIBLE,", ANTON, 130, CREAM, 760, 0.45), T("ON GARDE", ANTON, 250, CREAM, 1000, 1.1), T("LE SEIN.", ANTON, 330, CORAL, 1270, 1.5)],
  # 7 appel
  [T("ENVOIE-LE", ANTON, 300, CREAM, 1010, 0.35), T("À QUELQU'UN QUI A", ANTON, 130, CORAL, 1250, 0.85), T("UNE MAMMO À FAIRE.", ANTON, 130, CREAM, 1400, 1.2)],
]

def draw_lines(im, i, lt):
    for L in SC[i]:
        pop(im, layer(L["text"], L["font"], L["size"], L["col"], L["maxw"]), 540, L["y"], lt, L["delay"])

def scene_extra(im, i, lt):
    if i == 1:   # tumeur de 2 cm à l'échelle (1 cm = 150 px) : disque de 300 px
        PXCM = 150
        cx, cy, r = 540, 1130, PXCM
        x = clamp((lt - 1.0) / 0.5)
        if x > 0:
            ov = Image.new("RGBA", (W, H), (0, 0, 0, 0)); dr = ImageDraw.Draw(ov)
            rr = r * out_back(x, 1.2)
            dr.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], fill=CORAL + (255,))
            im.alpha_composite(ov)
        y2 = clamp((lt - 1.8) / 0.4)
        if y2 > 0:
            ov = Image.new("RGBA", (W, H), (0, 0, 0, 0)); dr = ImageDraw.Draw(ov)
            a = int(255 * y2); yb = cy + r + 70
            dr.line([(cx - r, yb), (cx + r, yb)], fill=CREAM + (a,), width=5)
            dr.line([(cx - r, yb - 18), (cx - r, yb + 18)], fill=CREAM + (a,), width=5)
            dr.line([(cx + r, yb - 18), (cx + r, yb + 18)], fill=CREAM + (a,), width=5)
            im.alpha_composite(ov)
            put(im, layer("2 CM", POP, 52, CREAM), cx, cy + r + 140, 1.0, y2)
            put(im, layer("Taille réelle d'une petite tumeur, à l'échelle", POPR, 30, GREY), cx, cy + r + 215, 1.0, y2)
    if i == 2:   # deux groupes de points (1 point ≈ 10 femmes)
        cols, rows, gap = 7, 5, 58
        for g, (cx0, col) in enumerate(((290, CREAM), (790, CORAL))):
            gw = (cols - 1) * gap; gh = (rows - 1) * gap
            ov = Image.new("RGBA", (W, H), (0, 0, 0, 0)); dr = ImageDraw.Draw(ov)
            for n in range(cols * rows):
                r_, c_ = divmod(n, cols)
                t0 = 1.0 + n * 0.035 + g * 0.0
                x = clamp((lt - t0) / 0.18)
                if x <= 0: continue
                px = cx0 - gw / 2 + c_ * gap; py = 960 - gh / 2 + r_ * gap
                rad = 20 * out_back(x, 1.2)
                dr.ellipse([px - rad, py - rad, px + rad, py + rad], fill=col + (255,))
            im.alpha_composite(ov)
        a = clamp((lt - 2.3) / 0.4)
        put(im, layer("ON ENLÈVE", POP, 40, CREAM), 290, 1190, 1.0, a)
        put(im, layer("TOUT LE SEIN", POP, 40, CREAM), 290, 1240, 1.0, a)
        put(im, layer("ON GARDE LE SEIN", POP, 40, CORAL), 790, 1190, 1.0, a)
        put(im, layer("+ radiothérapie", POPR, 38, CORAL), 790, 1240, 1.0, a)
        put(im, layer("701 femmes · tumeurs ≤ 2 cm · 1 point ≈ 10 femmes", POPR, 28, GREY), 540, 1390, 1.0, clamp((lt - 2.8) / 0.4))
        put(im, layer("Essai de Milan, 1973-1980", POPR, 28, GREY), 540, 1435, 1.0, clamp((lt - 3.1) / 0.4))
    if i == 3:
        pop(im, layer("Décès toutes causes à 20 ans : 41,7 % contre 41,2 %", POPR, 30, GREY), 540, 1420, lt, 2.3)
        pop(im, layer("Veronesi et al., NEJM 2002", POPR, 28, GREY), 540, 1470, lt, 2.6)
    if i == 4:
        ov = Image.new("RGBA", (W, H), (0, 0, 0, 0)); dr = ImageDraw.Draw(ov)
        for q in range(4):
            ph = (lt * 0.6 + q / 4) % 1.0; r = 100 + ph * 620
            dr.ellipse([540 - r, 1000 - r, 540 + r, 1000 + r], outline=CORAL + (int(70 * (1 - ph)),), width=6)
        im.alpha_composite(ov)
        pop(im, layer("Méta-analyse EBCTCG, Lancet 2011 · 10 801 femmes", POPR, 28, GREY), 540, 1470, lt, 2.6)
    if i == 5:
        pop(im, layer("Plus on détecte tôt, plus c'est possible.", POP, 44, CREAM, 900), 540, 1530, lt, 2.3)
    if i == 6:
        ribbon(im, 540, 560, 160, CORAL, clamp(lt / 0.3))
        pop(im, layer("ENREGISTRE-LE", POP, 46, GREY), 540, 1520, lt, 1.9)

def frame(t):
    i = max(j for j in range(7) if t >= BOUNDS[j])
    lt = t - BOUNDS[i]
    im = BGIMG.convert("RGBA")
    scene_extra(im, i, lt)
    draw_lines(im, i, lt)
    # fondu court entre scènes (sortie du précédent masquée par un flash de fond)
    rgb = np.asarray(im.convert("RGB"), dtype=np.float32) + GRAIN[int(t * FPS) % 6]
    return Image.fromarray(np.clip(rgb, 0, 255).astype(np.uint8))

# ---------- sound design discret ----------
def make_audio(path):
    SR = 44100; n = int(DUR * SR); t = np.arange(n) / SR
    mix = np.zeros(n)
    # nappe très douce (La mineur) + léger tremolo
    for f, a in ((110.0, .5), (164.81, .35), (220.0, .30), (261.63, .22), (329.63, .12)):
        mix += a * np.sin(2 * np.pi * f * t) * (0.85 + 0.15 * np.sin(2 * np.pi * 0.17 * t + f))
    env = np.minimum(1, t / 1.8) * np.minimum(1, (DUR - t) / 2.0)
    mix *= 0.055 * env
    def add(at, sig, gain):
        s = int(at * SR); e = min(n, s + len(sig))
        if s < n: mix[s:e] += gain * sig[:e - s]
    def tick():
        m = int(0.12 * SR); tt = np.arange(m) / SR
        noise = np.random.default_rng(3).normal(0, 1, m) * np.exp(-tt * 70) * 0.4
        return np.sin(2 * np.pi * 1180 * tt) * np.exp(-tt * 38) * 0.6 + noise
    def thump():
        m = int(0.45 * SR); tt = np.arange(m) / SR
        return np.sin(2 * np.pi * (58 + 40 * np.exp(-tt * 18)) * tt) * np.exp(-tt * 9)
    def whoosh():
        m = int(0.5 * SR); tt = np.arange(m) / SR
        noise = np.random.default_rng(5).normal(0, 1, m)
        k = np.ones(40) / 40; noise = np.convolve(noise, k, mode="same")
        return noise * np.sin(np.pi * tt / 0.5) ** 2
    def chime():
        m = int(1.6 * SR); tt = np.arange(m) / SR
        return (np.sin(2 * np.pi * 880 * tt) + 0.5 * np.sin(2 * np.pi * 1320 * tt)) * np.exp(-tt * 2.6)
    for i in range(7):
        s0 = BOUNDS[i]
        if i > 0: add(s0 - 0.08, whoosh(), 0.10)
        for j, L in enumerate(SC[i]):
            add(s0 + L["delay"], tick(), 0.17)
        if i in (0, 3, 5): add(s0 + SC[i][-1]["delay"], thump(), 0.30)
    add(BOUNDS[6] + 1.3, chime(), 0.07)
    peak = np.max(np.abs(mix)); mix = mix / peak * 0.75
    stereo = np.stack([mix, np.roll(mix, 14)], axis=1)  # léger élargissement
    pcm = (stereo * 32767).astype(np.int16)
    with wave.open(path, "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())

if args.frames:
    os.makedirs(args.frames, exist_ok=True)
    for n_, i in enumerate(range(7)):
        t_end = BOUNDS[i + 1] - 0.15
        frame(t_end).save(f"{args.frames}/f{n_ + 1}.png")
    frame(0.5).save(f"{args.frames}/f0.png")
    sys.exit()

audio = None
if not args.no_audio:
    audio = "/home/claude/doctorgane/reel2/sound.wav"; make_audio(audio)
cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-"]
if audio: cmd += ["-i", audio, "-c:a", "aac", "-b:a", "192k"]
cmd += ["-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", "-movflags", "+faststart", "-t", f"{DUR:.2f}", args.out]
p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
for n in range(NF):
    p.stdin.write(frame(n / FPS).tobytes())
p.stdin.close(); p.wait()
print("ok", args.out, f"{DUR:.1f}s")
