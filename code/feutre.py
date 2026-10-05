"""Moteur « dessin au feutre » Doctorgane : traits et écriture animés sur papier crème.
Rendu supersamplé x2, 1080x1920, 30 fps. Aucune voix. Sons synthétisés (frottement de feutre, tic, carillon).
"""
import math, random, subprocess, wave, os
import numpy as np
from PIL import Image, ImageDraw, ImageFont

W, H, FPS, SS = 1080, 1920, 30, 2
PAPER = (247, 243, 235)
NAVY = (20, 34, 64); CORAL = (240, 92, 80); GREY = (112, 122, 146); SKY = (70, 110, 180)
FD = "/home/claude/fonts/"
CAVEAT = FD + "PatrickHand.ttf"   # chiffres lisibles (le 5 de Caveat/Kalam ressemble à un S)
BOLDK = 0.022   # épaisseur de feutre ajoutée au contour des lettres

def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))
def ease_io(x): x = clamp(x); return 0.5 - 0.5 * math.cos(math.pi * x)
def ease_out(x): x = clamp(x); return 1 - (1 - x) ** 2

# ---------------------------------------------------------------- géométrie à main levée
def densify(pts, step=7.0):
    out = [tuple(pts[0])]
    for (x0, y0), (x1, y1) in zip(pts[:-1], pts[1:]):
        d = math.hypot(x1 - x0, y1 - y0); n = max(1, int(d / step))
        for k in range(1, n + 1):
            out.append((x0 + (x1 - x0) * k / n, y0 + (y1 - y0) * k / n))
    return out

def hand(pts, amp=1.5, seed=0, step=7.0):
    pts = densify(pts, step); r = random.Random(seed)
    p = [r.uniform(0, 6.28) for _ in range(4)]
    return [(x + amp * (math.sin(i * .21 + p[0]) + .5 * math.sin(i * .57 + p[1])),
             y + amp * (math.cos(i * .19 + p[2]) + .5 * math.sin(i * .49 + p[3]))) for i, (x, y) in enumerate(pts)]

def catmull(pts, n=14):
    P = [pts[0]] + list(pts) + [pts[-1]]; out = []
    for i in range(1, len(P) - 2):
        p0, p1, p2, p3 = P[i - 1], P[i], P[i + 1], P[i + 2]
        for k in range(n):
            t = k / n; t2 = t * t; t3 = t2 * t
            out.append(tuple(0.5 * ((2 * p1[j]) + (-p0[j] + p2[j]) * t + (2 * p0[j] - 5 * p1[j] + 4 * p2[j] - p3[j]) * t2 +
                                   (-p0[j] + 3 * p1[j] - 3 * p2[j] + p3[j]) * t3) for j in (0, 1)))
    out.append(tuple(pts[-1])); return out

def arc(cx, cy, rx, ry, a0, a1, n=24):
    return [(cx + rx * math.cos(math.radians(a0 + (a1 - a0) * k / n)), cy + ry * math.sin(math.radians(a0 + (a1 - a0) * k / n))) for k in range(n + 1)]

def rrect(x, y, w, h, r, over=0.07):
    p = [(x + r, y), (x + w - r, y)]
    p += arc(x + w - r, y + r, r, r, -90, 0, 6)[1:]
    p += [(x + w, y + h - r)]
    p += arc(x + w - r, y + h - r, r, r, 0, 90, 6)[1:]
    p += [(x + r, y + h)]
    p += arc(x + r, y + h - r, r, r, 90, 180, 6)[1:]
    p += [(x, y + r)]
    p += arc(x + r, y + r, r, r, 180, 270, 6)[1:]
    p += [(x + r + w * over, y)]
    return p

def check(cx, cy, s):
    return [(cx - .42 * s, cy + .02 * s), (cx - .10 * s, cy + .40 * s), (cx + .46 * s, cy - .40 * s)]

def ellipse(cx, cy, rx, ry, turns=1.08, a0=-110):
    return arc(cx, cy, rx, ry, a0, a0 + 360 * turns, 48)

def wavy(x0, x1, y, amp=6, waves=3):
    n = 40
    return [(x0 + (x1 - x0) * k / n, y + amp * math.sin(2 * math.pi * waves * k / n)) for k in range(n + 1)]

def arrow(x0, y0, x1, y1, head=44, bend=18):
    mx, my = (x0 + x1) / 2, (y0 + y1) / 2 - bend
    shaft = catmull([(x0, y0), (mx, my), (x1, y1)], 12)
    ang = math.atan2(y1 - my, x1 - mx)
    h1 = [(x1 - head * math.cos(ang - .55), y1 - head * math.sin(ang - .55)), (x1, y1)]
    h2 = [(x1, y1), (x1 - head * math.cos(ang + .55), y1 - head * math.sin(ang + .55))]
    return shaft, h1 + h2[1:]

def ribbon(cx, cy, u):
    pts = [(-.55, 1.25), (-.02, .22), (.40, -.50), (.36, -1.0), (0, -1.28), (-.36, -1.0), (-.40, -.50), (.02, .22), (.55, 1.25)]
    return catmull([(cx + a * u, cy + b * u) for a, b in pts], 12)

# ---------------------------------------------------------------- éléments animés
class Stroke:
    kind = "stroke"
    def __init__(s, pts, col=NAVY, w=9, t0=0.0, dur=0.5, snd="scratch", seed=0, amp=1.4, pen=True):
        pts = hand(pts, amp, seed) if amp else densify(pts)
        s.pts = np.array(pts, float) * SS; s.col = col; s.w = w * SS; s.t0 = t0; s.dur = dur; s.snd = snd; s.pen = pen
        seg = np.hypot(*np.diff(s.pts, axis=0).T); s.cum = np.concatenate([[0], np.cumsum(seg)]); s.total = float(s.cum[-1]); s.reset()
    def reset(s): s.drawn = 0.0
    def point_at(s, L):
        L = clamp(L, 0, s.total); i = int(np.searchsorted(s.cum, L, side="right") - 1); i = min(i, len(s.pts) - 2)
        seg = s.cum[i + 1] - s.cum[i]; f = 0 if seg <= 0 else (L - s.cum[i]) / seg
        return s.pts[i] + (s.pts[i + 1] - s.pts[i]) * f
    def target(s, lt): return ease_io((lt - s.t0) / s.dur) * s.total
    def advance(s, lt, canvas):
        if lt < s.t0: return
        tgt = s.target(lt)
        if tgt <= s.drawn and s.drawn > 0: return
        a = s.drawn; idx = [k for k in range(len(s.cum)) if a < s.cum[k] < tgt]
        path = [tuple(s.point_at(a))] + [tuple(s.pts[k]) for k in idx] + [tuple(s.point_at(tgt))]
        d = ImageDraw.Draw(canvas); r = s.w / 2
        if len(path) > 1: d.line(path, fill=s.col, width=int(s.w), joint="curve")
        for (x, y) in path: d.ellipse([x - r, y - r, x + r, y + r], fill=s.col)
        s.drawn = tgt
    def head(s, lt): return tuple(s.point_at(s.target(lt)))
    def active(s, lt): return s.t0 <= lt < s.t0 + s.dur

class Text:
    kind = "text"
    def __init__(s, text, x, yb, size, col=NAVY, t0=0.0, dur=None, cps=18.0, wght=700, rot=0.0, anchor="l", snd="scratch", pen=True, maxw=940):
        f = ImageFont.truetype(CAVEAT, int(size * SS))
        while f.getlength(text) / SS > maxw and size > 30:
            size -= 4; f = ImageFont.truetype(CAVEAT, int(size * SS))
        sw = max(1, int(size * SS * BOLDK))
        wlen = f.getlength(text) / SS + 2 * sw / SS
        if anchor == "c": x = x - wlen / 2
        l, t, r, b = f.getbbox(text, anchor="ls", stroke_width=sw); pad = 10
        im = Image.new("L", (int(r - l) + 2 * pad, int(b - t) + 2 * pad), 0)
        ImageDraw.Draw(im).text((pad - l, pad - t), text, font=f, fill=255, anchor="ls", stroke_width=sw, stroke_fill=255)
        s.mask = np.asarray(im); s.ox = int(x * SS + l - pad); s.oy = int(yb * SS + t - pad); s.col = col; s.t0 = t0
        s.dur = dur if dur else max(0.35, len(text) / cps); s.snd = snd; s.pen = pen; s.size = size; s.baked = False; s.x = x; s.w = wlen; s.yb = yb
    def reset(s): s.baked = False
    def prog(s, lt): return ease_io(clamp((lt - s.t0) / s.dur)) if False else clamp((lt - s.t0) / s.dur)
    def layer(s, lt):
        p = s.prog(lt)
        if p <= 0: return None
        w = s.mask.shape[1]
        if p >= 1: return s.mask
        edge = p * (w + 30); xs = np.arange(w)
        ramp = np.clip((edge - xs) / 30.0, 0, 1)
        return (s.mask * ramp[None, :]).astype(np.uint8)
    def paste(s, canvas, lt):
        m = s.layer(lt)
        if m is None: return
        canvas.paste(s.col, (s.ox, s.oy), Image.fromarray(m))
    def advance(s, lt, canvas):
        if not s.baked and lt >= s.t0 + s.dur:
            s.paste(canvas, lt); s.baked = True
    def head(s, lt):
        p = s.prog(lt); w = s.mask.shape[1]
        return (s.ox + min(w, p * (w + 30)) - 8, s.oy + s.mask.shape[0] * 0.66)
    def active(s, lt): return s.t0 <= lt < s.t0 + s.dur

class Counter:
    """Gros chiffre qui change de valeur (décompte). values/times : valeur affichée à partir de times[i]."""
    kind = "counter"; pen = False; dur = 0.0; baked = True; snd = None
    def __init__(s, x, yb, size, values, times, cols, pop_dur=0.30, pop_amp=0.20):
        s.items = [Text(str(v), x, yb, size, c, 0.0, dur=0.001, anchor="c", pen=False) for v, c in zip(values, cols)]
        s.times = list(times); s.ticks = list(times[1:]); s.t0 = times[0]; s.pop_dur = pop_dur; s.pop_amp = pop_amp
    def reset(s): pass
    def advance(s, lt, canvas): pass
    def active(s, lt): return False
    def paste(s, canvas, lt):
        i = 0
        for k, tt in enumerate(s.times):
            if lt >= tt: i = k
        tx = s.items[i]; im = Image.fromarray(tx.mask)
        if i == len(s.items) - 1 and i > 0:
            x = clamp((lt - s.times[i]) / s.pop_dur); sc = 1 + s.pop_amp * (1 - x) ** 2
            if abs(sc - 1) > 1e-3:
                w, h = im.size; cx, cy = tx.ox + w / 2, tx.oy + h / 2
                im = im.resize((int(w * sc), int(h * sc)), Image.BICUBIC); canvas.paste(tx.col, (int(cx - im.width / 2), int(cy - im.height / 2)), im); return
        canvas.paste(tx.col, (tx.ox, tx.oy), im)

class Mark:
    kind = "mark"; pen = False; dur = 0.0; baked = True
    def __init__(s, t0, snd="chime"): s.t0 = t0; s.snd = snd
    def reset(s): pass
    def advance(s, lt, canvas): pass
    def active(s, lt): return False

# ---------------------------------------------------------------- feutre (sprite)
def draw_pen(img, x, y, col):
    ang = math.radians(-62)  # le feutre part vers le haut à droite
    ux, uy = math.cos(ang), math.sin(ang); nx, ny = -uy, ux
    def P(a, b): return (x + ux * a + nx * b, y + uy * a + ny * b)
    d = ImageDraw.Draw(img, "RGBA")
    k = SS
    shadow = [P(0, -6 * k), P(150 * k, -36 * k), P(150 * k, 36 * k), P(0, 6 * k)]
    d.polygon([(a + 10 * k, b + 14 * k) for a, b in shadow], fill=(0, 0, 0, 38))
    d.polygon([P(0, 0), P(40 * k, -14 * k), P(40 * k, 14 * k)], fill=col + (255,))              # pointe
    d.polygon([P(36 * k, -15 * k), P(150 * k, -26 * k), P(150 * k, 26 * k), P(36 * k, 15 * k)], fill=(236, 236, 240, 255), outline=NAVY + (255,))
    d.polygon([P(36 * k, -15 * k), P(62 * k, -17 * k), P(62 * k, 17 * k), P(36 * k, 15 * k)], fill=col + (255,))   # bague couleur
    d.polygon([P(150 * k, -26 * k), P(178 * k, -22 * k), P(178 * k, 22 * k), P(150 * k, 26 * k)], fill=col + (255,))  # bouchon

# ---------------------------------------------------------------- fond papier
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
_r = np.random.default_rng(5)
def _blur_noise(scale, amp):
    small = _r.normal(0, 1, (H // scale + 2, W // scale + 2)).astype(np.float32)
    im = Image.fromarray(((small - small.min()) / (small.max() - small.min()) * 255).astype(np.uint8)).resize((W, H), Image.BICUBIC)
    a = np.asarray(im, dtype=np.float32) / 255.0 - 0.5
    return a * amp
vig = 1 - 0.07 * (((xx - W / 2) / (W * .75)) ** 2 + ((yy - H * .48) / (H * .75)) ** 2)
TEX = (vig + _blur_noise(160, .04) + _blur_noise(26, .012))[..., None]
PAPER_FRAME = np.array(PAPER, np.float32)[None, None, :] * TEX
GRAIN = [_r.normal(0, 2.0, (H, W, 1)).astype(np.float32) for _ in range(6)]

# ---------------------------------------------------------------- moteur de scènes
class Scene:
    def __init__(s, dur, items, erase=0.45):
        s.dur = dur; s.items = items; s.erase = erase

class Film:
    def __init__(s, scenes):
        s.scenes = scenes; s.bounds = [0.0]
        for sc in scenes: s.bounds.append(s.bounds[-1] + sc.dur)
        s.dur = s.bounds[-1]; s.nf = int(s.dur * FPS)
        s.cur = -1; s.canvas = None
    def start_scene(s, i):
        s.cur = i; s.canvas = Image.new("RGB", (W * SS, H * SS), PAPER)
        for it in s.scenes[i].items: it.reset()
    def frame(s, t):
        i = max(j for j in range(len(s.scenes)) if t >= s.bounds[j] - 1e-9); i = min(i, len(s.scenes) - 1)
        lt = t - s.bounds[i]; sc = s.scenes[i]
        if i != s.cur or lt < getattr(s, "_last_lt", 0) - 1e-9: s.start_scene(i)
        s._last_lt = lt
        for it in sc.items: it.advance(lt, s.canvas)
        fr = s.canvas.copy()
        for it in sc.items:
            if it.kind == "text" and not it.baked: it.paste(fr, lt)
            elif it.kind == "counter": it.paste(fr, lt)
        act = [it for it in sc.items if it.pen and it.active(lt) and it.dur >= 0.16]
        if act:
            it = max(act, key=lambda q: q.t0); hx, hy = it.head(lt); draw_pen(fr, hx, hy, it.col)
        arr = np.asarray(fr.reduce(SS), dtype=np.float32) / 255.0 * TEX
        arr = arr * 1.0
        # effaceur : balayage diagonal en fin de scène (sauf dernière)
        if sc.erase and i < len(s.scenes) - 1 and lt > sc.dur - sc.erase:
            p = (lt - (sc.dur - sc.erase)) / sc.erase
            soft = 160.0; edge = ease_io(p) * (W + H * 0.25 + soft) - soft
            m = np.clip((edge - (xx + yy * 0.25)) / soft, 0, 1)[..., None]
            arr = arr * (1 - m) + (PAPER_FRAME / 255.0) * m
        out = arr * 255.0 + GRAIN[int(t * FPS) % 6]
        return Image.fromarray(np.clip(out, 0, 255).astype(np.uint8))

    # ------------------------------------------------------------ son
    def make_audio(s, path):
        SR = 44100; n = int(s.dur * SR); mix = np.zeros(n); rg = np.random.default_rng(9)
        t = np.arange(n) / SR
        for f, a in ((130.81, .5), (196.0, .35), (261.63, .3), (329.63, .2), (392.0, .12)):  # nappe Do majeur, très douce
            mix += a * np.sin(2 * np.pi * f * t) * (0.88 + 0.12 * np.sin(2 * np.pi * 0.13 * t + f))
        mix *= 0.05 * np.minimum(1, t / 1.5) * np.minimum(1, (s.dur - t) / 2.0)
        def add(at, sig, g):
            a = int(at * SR); e = min(n, a + len(sig))
            if 0 <= a < n: mix[a:e] += g * sig[:e - a]
        def scratch(d):
            m = max(8, int(d * SR)); x = rg.normal(0, 1, m)
            x = x - 0.96 * np.concatenate([[0], x[:-1]]); x = np.convolve(x, np.ones(3) / 3, mode="same")
            tt = np.arange(m) / SR; env = np.sin(np.pi * np.arange(m) / m) ** 0.6 * (0.7 + 0.3 * np.sin(2 * np.pi * 11 * tt + rg.uniform(0, 6)))
            return x * env
        def tick():
            m = int(0.09 * SR); tt = np.arange(m) / SR
            return np.sin(2 * np.pi * 1500 * tt) * np.exp(-tt * 55) * .6 + rg.normal(0, 1, m) * np.exp(-tt * 90) * .35
        def pop():
            m = int(0.2 * SR); tt = np.arange(m) / SR
            return np.sin(2 * np.pi * (330 + 260 * np.exp(-tt * 25)) * tt) * np.exp(-tt * 18)
        def whoosh(d=0.45):
            m = int(d * SR); x = np.convolve(rg.normal(0, 1, m), np.ones(60) / 60, mode="same"); return x * np.sin(np.pi * np.arange(m) / m) ** 2
        def chime():
            m = int(1.8 * SR); tt = np.arange(m) / SR
            return (np.sin(2 * np.pi * 784 * tt) + .5 * np.sin(2 * np.pi * 1175 * tt) + .25 * np.sin(2 * np.pi * 1568 * tt)) * np.exp(-tt * 2.4)
        for i, sc in enumerate(s.scenes):
            t0 = s.bounds[i]
            for it in sc.items:
                if it.snd == "scratch": add(t0 + it.t0, scratch(it.dur), 0.045 if it.dur > .16 else 0.03)
                elif it.snd == "tick": add(t0 + it.t0 + it.dur * .8, tick(), 0.22)
                elif it.snd == "pop": add(t0 + it.t0, pop(), 0.2)
                elif it.snd == "chime": add(t0 + it.t0, chime(), 0.10)
                if getattr(it, "ticks", None):
                    for tt in it.ticks: add(t0 + tt, tick(), 0.09)
            if i < len(s.scenes) - 1 and sc.erase: add(t0 + sc.dur - sc.erase, whoosh(sc.erase), 0.07)
        pk = np.max(np.abs(mix)); mix = mix / pk * 0.75
        st = np.stack([mix, np.roll(mix, 12)], axis=1)
        with wave.open(path, "wb") as w:
            w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((st * 32767).astype(np.int16).tobytes())

    def encode(s, out, audio=None, crf=23):
        cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-"]
        if audio: cmd += ["-i", audio, "-c:a", "aac", "-b:a", "160k"]
        cmd += ["-c:v", "libx264", "-preset", "medium", "-crf", str(crf), "-maxrate", "8M", "-bufsize", "16M", "-pix_fmt", "yuv420p", "-movflags", "+faststart", "-t", f"{s.dur:.2f}", out]
        p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
        for k in range(s.nf): p.stdin.write(s.frame(k / FPS).tobytes())
        p.stdin.close(); p.wait()
