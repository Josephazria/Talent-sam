#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ohlalive — RÉELS TEASING typographiques animés (code), sans son.
R1 « Montée »   : les éléments de la carte apparaissent un à un (fondu + glissé), carte finale tenue.
R2 « Battements »: un mot géant par battement, le fond alterne Framboise / Mimosa / Ivoire, carte finale.
Chaque réel sort en 9:16 (story / réel) et en 4:5 (post).
"""
import os, subprocess
import numpy as np
from PIL import Image, ImageDraw
from ohlalive_kit import *

FPS = 30
S = SCALE

# ------------------------------------------------------------------ calques (RGBA 1x, rendus en 4x)
def text_layer(text, font, fill, tracking=0):
    tmp = Image.new("RGBA", (10, 10))
    d = ImageDraw.Draw(tmp)
    w = text_w(d, text, font, tracking) + 8 * S
    b = d.textbbox((0, 0), "Hxgé", font=font)
    h = (b[3] - b[1]) + 12 * S + b[1]
    layer = Image.new("RGBA", (int(w), int(h)), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    if tracking:
        draw_tracked(d, 0, text, font, fill, tracking=tracking, x=4 * S)
    else:
        d.text((4 * S, 0), text, font=font, fill=fill)
    bb = layer.getbbox()
    layer = layer.crop(bb)
    return layer.resize((max(1, layer.width // S), max(1, layer.height // S)), Image.LANCZOS)

def rect_layer(w, h, fill):
    return Image.new("RGBA", (int(w), int(h)), fill + (255,))

def down(img_rgba):
    return img_rgba.resize((max(1, img_rgba.width // S), max(1, img_rgba.height // S)), Image.LANCZOS)

# ------------------------------------------------------------------ composition d'une frame
def ease_out(t):
    t = min(max(t, 0.0), 1.0)
    return 1 - (1 - t) ** 3

def composite(bg_col, size, items):
    """items: list of (layer, cx, cy, opacity, scale). Retourne un ndarray RGB."""
    W, H = size
    frame = Image.new("RGBA", (W, H), bg_col + (255,))
    for layer, cx, cy, op, sc in items:
        if op <= 0: continue
        L = layer
        if abs(sc - 1.0) > 1e-3:
            L = L.resize((max(1, int(L.width * sc)), max(1, int(L.height * sc))), Image.LANCZOS)
        if op < 1.0:
            a = L.getchannel("A").point(lambda v: int(v * op))
            L = L.copy(); L.putalpha(a)
        frame.alpha_composite(L, (int(cx - L.width / 2), int(cy - L.height / 2)))
    return frame.convert("RGB")

def grain_frame(img, amount=4, opacity=0.04):
    arr = np.array(img).astype(np.float32)
    n = np.random.normal(0, amount, arr.shape[:2])[..., None]
    arr = arr * (1 - opacity) + (arr + n) * opacity
    return np.clip(arr, 0, 255).astype(np.uint8)

def encode(frames_iter, size, out_path):
    W, H = size
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
           "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
           "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18", "-preset", "medium",
           "-movflags", "+faststart", out_path]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for f in frames_iter:
        p.stdin.write(f.tobytes())
    p.stdin.close(); p.wait()
    return out_path

# ------------------------------------------------------------------ R1 « Montée »
def reel_montee(scheme, size, live, out_path, duration=6.5):
    sc = SCHEMES[scheme]
    W, H = size
    portrait_tall = H / W > 1.5
    k = 1.0 if portrait_tall else 0.86          # 4:5 un peu plus compact

    logo  = down(lockup(scheme, 880 * S * k))
    eye   = text_layer(live["date_label"], jost("SemiBold", 34 * S * k), sc["accent"], tracking=int(6 * S * k))
    head  = text_layer(live["title"], playfair("Bold", 150 * S * k), sc["text"])
    ital  = text_layer(live["title_italic"], playfair_italic("Medium Italic", 185 * S * k), sc["text"])
    div   = rect_layer(100 * k, 3, sc["accent"])
    foot1 = text_layer("EN LIVE SUR WHATNOT", jost("Medium", 24 * S), sc["text"], tracking=int(4 * S))
    foot2 = text_layer("@OHLALIVEPARIS", jost("Medium", 22 * S), sc["accent"], tracking=int(3 * S))

    gaps = [0, 90 * k, 46 * k, 20 * k, 70 * k]
    hs = [logo.height, eye.height, head.height, ital.height, div.height]
    block = sum(hs) + sum(gaps)
    top_safe, bottom_safe = (250, 330) if portrait_tall else (60, 150)
    y0 = top_safe + (H - top_safe - bottom_safe - block) // 2
    ys, y = [], y0
    for h, g in zip(hs, gaps):
        y += g; ys.append(y + h / 2); y += h
    cx = W / 2
    fy = H - bottom_safe + 40

    # timings (s) : début d'apparition de chaque élément
    t0 = [0.15, 0.95, 1.55, 2.15, 2.85]
    dur = 0.7
    n = int(duration * FPS)
    for i in range(n):
        t = i / FPS
        items = []
        for L, cy, ts in zip((logo, eye, head, ital), ys[:4], t0[:4]):
            p = ease_out((t - ts) / dur)
            items.append((L, cx, cy + (1 - p) * 40, p, 1.0))
        pd = ease_out((t - t0[4]) / 0.5)
        items.append((div, cx, ys[4], 1.0 if pd > 0 else 0.0, max(pd, 0.01)))
        pf = ease_out((t - 3.3) / dur)
        items.append((foot1, cx, fy + foot1.height / 2, pf, 1.0))
        items.append((foot2, cx, fy + foot1.height + 14 + foot2.height / 2, pf, 1.0))
        yield grain_frame(composite(sc["bg"], size, items))

# ------------------------------------------------------------------ R2 « Battements »
def reel_battements(size, live, out_path, beat=0.75, hold=2.4):
    W, H = size
    portrait_tall = H / W > 1.5
    k = 1.0 if portrait_tall else 0.86
    order = ["framboise", "mimosa", "ivoire"]
    words = live["beats"]                      # ex. ["MARDI 22", "12H", "Sélection", "de luxe", "en live", "sur Whatnot"]
    cx, cy = W / 2, H / 2

    # calques des mots, par schéma (la couleur du texte dépend du fond)
    def word_layer(word, scheme, italic):
        sc = SCHEMES[scheme]
        base = 200 if italic else 165
        mk = (lambda sz: playfair_italic("Medium Italic", sz * S * k)) if italic else (lambda sz: playfair("Bold", sz * S * k))
        L = text_layer(word, mk(base), sc["text"])
        target = W * 0.82
        f = target / L.width
        size = min(max(base * f, base), 420)           # les mots courts grossissent, plafond 420
        L = text_layer(word, mk(size), sc["text"])
        if L.width > target:
            L = L.resize((int(target), int(L.height * target / L.width)), Image.LANCZOS)
        return L

    beats = []
    for i, w in enumerate(words):
        scheme = order[i % 3]
        italic = w.islower() or w.startswith("de ")
        beats.append((scheme, word_layer(w, scheme, italic)))

    # carte finale (schéma du dernier battement + 1)
    final_scheme = order[len(words) % 3]
    sc = SCHEMES[final_scheme]
    logo = down(lockup(final_scheme, 880 * S * k))
    eye  = text_layer(live["date_label"], jost("SemiBold", 34 * S * k), sc["accent"], tracking=int(6 * S * k))
    head = text_layer(live["title"], playfair("Bold", 150 * S * k), sc["text"])
    ital = text_layer(live["title_italic"], playfair_italic("Medium Italic", 185 * S * k), sc["text"])
    div  = rect_layer(100 * k, 3, sc["accent"])
    foot = text_layer("EN LIVE SUR WHATNOT  ·  @OHLALIVEPARIS", jost("Medium", 22 * S), sc["accent"], tracking=int(3 * S))
    gaps = [0, 90 * k, 46 * k, 20 * k, 70 * k]
    hs = [logo.height, eye.height, head.height, ital.height, div.height]
    block = sum(hs) + sum(gaps)
    top_safe, bottom_safe = (250, 330) if portrait_tall else (60, 150)
    y0 = top_safe + (H - top_safe - bottom_safe - block) // 2
    ys, y = [], y0
    for h, g in zip(hs, gaps):
        y += g; ys.append(y + h / 2); y += h
    fy = H - bottom_safe + 40

    total = len(beats) * beat + hold
    n = int(total * FPS)
    for i in range(n):
        t = i / FPS
        bi = int(t // beat)
        if bi < len(beats):
            scheme, L = beats[bi]
            tb = (t - bi * beat) / 0.22
            p = ease_out(tb)
            frame = composite(SCHEMES[scheme]["bg"], size, [(L, cx, cy, p, 0.94 + 0.06 * p)])
        else:
            tf = (t - len(beats) * beat)
            p = ease_out(tf / 0.5)
            items = [(logo, cx, ys[0], p, 1.0), (eye, cx, ys[1], p, 1.0), (head, cx, ys[2], p, 1.0),
                     (ital, cx, ys[3], p, 1.0), (div, cx, ys[4], p, 1.0), (foot, cx, fy + foot.height / 2, p, 1.0)]
            frame = composite(sc["bg"], size, items)
        yield grain_frame(frame)

# ------------------------------------------------------------------ production
LIVE = {
    "slug": "2026-09-22",
    "date_label": "MARDI 22 SEPTEMBRE  ·  12H",
    "title": "Sélection",
    "title_italic": "de luxe",
    "beats": ["Mardi 22", "12H", "Sélection", "de luxe", "en live", "sur Whatnot"],
}

if __name__ == "__main__":
    out_dir = f"{os.environ.get('KIT_OUT','kit')}/{LIVE['slug']}/reels"
    os.makedirs(out_dir, exist_ok=True)
    formats = {"story": (1080, 1920), "post": (1080, 1350)}
    for fmt, size in formats.items():
        p = f"{out_dir}/{LIVE['slug']}_reel-R1-montee_framboise_{fmt}.mp4"
        encode(reel_montee("framboise", size, LIVE, p), size, p); print("saved", p)
        p = f"{out_dir}/{LIVE['slug']}_reel-R2-battements_{fmt}.mp4"
        encode(reel_battements(size, LIVE, p), size, p); print("saved", p)
