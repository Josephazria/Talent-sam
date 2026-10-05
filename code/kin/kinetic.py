"""Moteur « kinetic » Doctorgane : typographie géante animée + photos plein cadre, 1080x1920 30 fps."""
import math, subprocess, wave, numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps, ImageEnhance
W, H, FPS = 1080, 1920, 30
F = "/home/claude/fonts/"
NAVY = (14, 24, 48); CREAM = (247, 242, 233); CORAL = (255, 111, 97); GREY = (168, 176, 192); DARK = (8, 14, 30)
def anton(s): return ImageFont.truetype(F + "Anton-Regular.ttf", int(s))
def pop(s, w="SemiBold"): return ImageFont.truetype(F + f"Poppins-{w}.ttf", int(s))
def clamp(x, a=0., b=1.): return max(a, min(b, x))
def ease_out(x): x = clamp(x); return 1 - (1 - x) ** 3
def overshoot(x, k=1.7):  # back-out
    x = clamp(x); return 1 + (k + 1) * (x - 1) ** 3 + k * (x - 1) ** 2
def ease_io(x): x = clamp(x); return 0.5 - 0.5 * math.cos(math.pi * x)

class Word:
    """Un bloc de texte (une ligne) qui apparaît avec une animation."""
    def __init__(s, text, cx, cy, size, col=CREAM, t0=0.0, dur=0.28, font="anton", anim="pop", box=None, align="c", maxw=980, t1=None, snd="pop"):
        f = anton(size) if font == "anton" else pop(size, "SemiBold" if font == "pop" else font)
        d0 = ImageDraw.Draw(Image.new("L", (1, 1)))
        while d0.textlength(text, font=f) > maxw and size > 24:
            size -= 3; f = anton(size) if font == "anton" else pop(size, "SemiBold" if font == "pop" else font)
        l, t, r, b = d0.textbbox((0, 0), text, font=f); pad = 36
        lay = Image.new("RGBA", (int(r - l) + 2 * pad, int(b - t) + 2 * pad), (0, 0, 0, 0)); dl = ImageDraw.Draw(lay)
        if box:  # bloc de couleur derrière le mot
            dl.rounded_rectangle([pad - 22, pad - 6, pad + (r - l) + 22, pad + (b - t) + 14], radius=14, fill=box)
        dl.text((pad - l, pad - t), text, font=f, fill=col)
        s.lay = lay; s.cx = cx; s.cy = cy; s.t0 = t0; s.dur = dur; s.anim = anim; s.t1 = t1; s.snd = snd; s.align = align
    def draw(s, fr, t):
        if t < s.t0 or (s.t1 is not None and t > s.t1): return
        p = clamp((t - s.t0) / s.dur)
        lay = s.lay; a = 1.0; dy = 0; sc = 1.0
        if s.anim == "pop": sc = 0.6 + 0.4 * overshoot(p); a = ease_out(min(1, p * 2))
        elif s.anim == "slam": sc = 1.0 + 0.7 * (1 - ease_out(p)); a = ease_out(min(1, p * 3))
        elif s.anim == "up": dy = int(60 * (1 - ease_out(p))); a = ease_out(p)
        elif s.anim == "fade": a = ease_out(p)
        if sc != 1.0:
            nw, nh = max(1, int(lay.width * sc)), max(1, int(lay.height * sc)); lay = lay.resize((nw, nh), Image.BILINEAR)
        if a < 1:
            al = lay.split()[3].point(lambda v: int(v * a)); lay = lay.copy(); lay.putalpha(al)
        x = s.cx - lay.width // 2 if s.align == "c" else (s.cx if s.align == "l" else s.cx - lay.width)
        fr.alpha_composite(lay, (int(x), int(s.cy - lay.height // 2 + dy)))

class Photo:
    """Photo : fond flou plein cadre + carte nette avec zoom lent (Ken Burns)."""
    def __init__(s, path, cy, w=1000, h=None, t0=0.0, dur=0.5, zoom=1.08, radius=44, card=True, dim=0.55, snd="whoosh"):
        im = Image.open(path).convert("RGB")
        s.h = h or int(w * im.height / im.width); s.w = w
        s.src = ImageOps.fit(im, (int(s.w * 1.15), int(s.h * 1.15)), Image.LANCZOS)
        bg = ImageOps.fit(im, (W // 4, H // 4), Image.LANCZOS).filter(ImageFilter.GaussianBlur(10)).resize((W, H), Image.BILINEAR)
        bg = ImageEnhance.Brightness(bg).enhance(1 - dim); s.bg = bg.convert("RGBA")
        s.cy = cy; s.t0 = t0; s.dur = dur; s.zoom = zoom; s.radius = radius; s.card = card; s.snd = snd; s.life = 6.0
    def draw(s, fr, t):
        if t < s.t0: return
        p = clamp((t - s.t0) / s.dur); z = 1 + (s.zoom - 1) * clamp((t - s.t0) / s.life)
        fr.alpha_composite(s.bg)
        cw, ch = int(s.src.width / 1.15 / z), int(s.src.height / 1.15 / z)
        x0, y0 = (s.src.width - cw) // 2, (s.src.height - ch) // 2
        card = s.src.crop((x0, y0, x0 + cw, y0 + ch)).resize((s.w, s.h), Image.BILINEAR).convert("RGBA")
        mask = Image.new("L", (s.w, s.h), 0); ImageDraw.Draw(mask).rounded_rectangle([0, 0, s.w - 1, s.h - 1], radius=s.radius, fill=int(255 * ease_out(p)))
        card.putalpha(mask)
        sc = 0.92 + 0.08 * ease_out(p); cw2, ch2 = int(s.w * sc), int(s.h * sc)
        if sc < 1: card = card.resize((cw2, ch2), Image.BILINEAR)
        fr.alpha_composite(card, ((W - cw2) // 2, int(s.cy - ch2 // 2)))

class Bar:
    def __init__(s, label, value, vmax, cy, col, t0, dur=0.6, x=80, w=920, h=58):
        s.label = label; s.value = value; s.vmax = vmax; s.cy = cy; s.col = col; s.t0 = t0; s.dur = dur; s.x = x; s.w = w; s.h = h; s.snd = "pop"
    def draw(s, fr, t):
        if t < s.t0: return
        p = ease_out((t - s.t0) / s.dur); d = ImageDraw.Draw(fr)
        d.text((s.x, s.cy - s.h - 58), s.label, font=pop(44), fill=CREAM)
        d.rounded_rectangle([s.x, s.cy - s.h // 2, s.x + s.w, s.cy + s.h // 2], radius=s.h // 2, fill=(40, 52, 84))
        fw = max(s.h, int(s.w * s.value / s.vmax * p))
        d.rounded_rectangle([s.x, s.cy - s.h // 2, s.x + fw, s.cy + s.h // 2], radius=s.h // 2, fill=s.col)

class Grid:
    """n carrés qui apparaissent en rafale."""
    def __init__(s, n, cols, cx, cy, cell, gap, col, t0, step=0.05, snd="tick"):
        s.n = n; s.cols = cols; s.cx = cx; s.cy = cy; s.cell = cell; s.gap = gap; s.col = col; s.t0 = t0; s.step = step; s.snd = snd
        s.ticks = [t0 + k * step for k in range(n)]
    def draw(s, fr, t):
        rows = math.ceil(s.n / s.cols); gw = s.cols * s.cell + (s.cols - 1) * s.gap; gh = rows * s.cell + (rows - 1) * s.gap
        x0, y0 = s.cx - gw // 2, s.cy - gh // 2; d = ImageDraw.Draw(fr)
        for k in range(s.n):
            tk = s.t0 + k * s.step
            if t < tk: break
            p = overshoot(clamp((t - tk) / 0.22)); sz = s.cell * p
            x = x0 + (k % s.cols) * (s.cell + s.gap) + s.cell / 2; y = y0 + (k // s.cols) * (s.cell + s.gap) + s.cell / 2
            d.rounded_rectangle([x - sz / 2, y - sz / 2, x + sz / 2, y + sz / 2], radius=max(2, int(sz * 0.22)), fill=s.col)

class Scene:
    def __init__(s, dur, items, bg=NAVY, flash=True): s.dur = dur; s.items = items; s.bg = bg; s.flash = flash

GRAIN = [np.random.default_rng(k).normal(0, 2.2, (H, W, 1)).astype(np.float32) for k in range(4)]
VIGN = None
def vignette():
    global VIGN
    if VIGN is None:
        yy, xx = np.mgrid[0:H, 0:W]; r = np.sqrt(((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2)
        VIGN = (1 - 0.32 * np.clip(r - 0.55, 0, 1) ** 1.5)[..., None].astype(np.float32)
    return VIGN

class Film:
    def __init__(s, scenes):
        s.scenes = scenes; s.bounds = [0.0]
        for sc in scenes: s.bounds.append(s.bounds[-1] + sc.dur)
        s.dur = s.bounds[-1]; s.nf = int(s.dur * FPS)
    def frame(s, t):
        i = min(max(j for j in range(len(s.scenes)) if t >= s.bounds[j] - 1e-9), len(s.scenes) - 1)
        lt = t - s.bounds[i]; sc = s.scenes[i]
        fr = Image.new("RGBA", (W, H), sc.bg + (255,))
        for it in sc.items: it.draw(fr, lt)
        arr = np.asarray(fr.convert("RGB"), dtype=np.float32) * vignette()
        if sc.flash and lt < 0.12: arr = arr + (1 - lt / 0.12) * 70  # flash blanc à la coupe
        out = arr + GRAIN[int(t * FPS) % 4]
        return Image.fromarray(np.clip(out, 0, 255).astype(np.uint8))
    def make_audio(s, path, music=None, music_gain=0.5):
        SR = 44100; n = int(s.dur * SR); mix = np.zeros(n); rg = np.random.default_rng(4); tt = lambda m: np.arange(m) / SR
        def add(at, sig, g):
            a = int(at * SR); e = min(n, a + len(sig))
            if 0 <= a < n: mix[a:e] += g * sig[:e - a]
        def pop_():
            m = int(0.12 * SR); x = tt(m); return np.sin(2 * np.pi * (180 + 120 * np.exp(-x * 40)) * x) * np.exp(-x * 28)
        def slam():
            m = int(0.5 * SR); x = tt(m); return np.sin(2 * np.pi * 55 * x) * np.exp(-x * 7) + 0.3 * rg.normal(0, 1, m) * np.exp(-x * 60)
        def whoosh():
            m = int(0.35 * SR); x = np.convolve(rg.normal(0, 1, m), np.ones(40) / 40, mode="same"); return x * np.sin(np.pi * np.arange(m) / m) ** 2
        def tick():
            m = int(0.05 * SR); x = tt(m); return np.sin(2 * np.pi * 2200 * x) * np.exp(-x * 90)
        for i, sc in enumerate(s.scenes):
            t0 = s.bounds[i]
            if i > 0: add(t0, whoosh(), 0.35)
            for it in sc.items:
                snd = getattr(it, "snd", None); ta = t0 + getattr(it, "t0", 0)
                if snd == "pop": add(ta, pop_(), 0.5)
                elif snd == "slam": add(ta, slam(), 0.9)
                elif snd == "whoosh": add(ta, whoosh(), 0.3)
                elif snd == "tick":
                    for tk in getattr(it, "ticks", []): add(t0 + tk, tick(), 0.25)
        if music is not None:
            mus = music[:n]; mix[:len(mus)] += music_gain * mus
        pk = max(1e-6, np.max(np.abs(mix))); mix = mix / pk * 0.85
        st = np.stack([mix, np.roll(mix, 9)], axis=1)
        with wave.open(path, "wb") as w:
            w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((st * 32767).astype(np.int16).tobytes())
    def encode(s, out, audio=None, crf=21):
        cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-"]
        if audio: cmd += ["-i", audio, "-c:a", "aac", "-b:a", "160k"]
        cmd += ["-c:v", "libx264", "-preset", "medium", "-crf", str(crf), "-pix_fmt", "yuv420p", "-movflags", "+faststart", "-t", f"{s.dur:.2f}", out]
        p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
        for k in range(s.nf): p.stdin.write(s.frame(k / FPS).tobytes())
        p.stdin.close(); p.wait()

def load_music(path, dur, fade_in=0.8, fade_out=2.0):
    """Charge un mp3 en mono float via ffmpeg, avec fondus."""
    raw = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", path, "-t", f"{dur:.2f}", "-ac", "1", "-ar", "44100", "-f", "f32le", "-"], capture_output=True).stdout
    x = np.frombuffer(raw, dtype=np.float32).astype(np.float64); n = len(x); SR = 44100
    env = np.ones(n); fi = int(fade_in * SR); fo = int(fade_out * SR)
    env[:fi] = np.linspace(0, 1, fi); env[-fo:] = np.linspace(1, 0, fo)
    return x * env / max(1e-6, np.max(np.abs(x)))
