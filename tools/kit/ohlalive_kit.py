#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ohlalive — moteur commun du kit visuel de live.
Palette, schémas couleur, polices, lockup/emblème recolorés, texte tracké, grain.
Méthode : rendu 4x puis réduction LANCZOS, grain léger.
"""
import numpy as np
from PIL import Image, ImageDraw, ImageFont

# ------------------------------------------------------------------ palette
FRAMBOISE = (150, 58, 76)
MIMOSA    = (244, 200, 70)
IVOIRE    = (242, 240, 234)
CASSIS    = (72, 26, 42)
ENCRE     = (26, 26, 26)

# Le point prend toujours l'autre couleur du duo :
#  - sur Framboise / Encre  -> Mimosa
#  - sur Mimosa / Ivoire    -> Framboise
SCHEMES = {
    "framboise": {"bg": FRAMBOISE, "text": IVOIRE, "accent": MIMOSA},
    "mimosa":    {"bg": MIMOSA,    "text": ENCRE,  "accent": FRAMBOISE},
    "ivoire":    {"bg": IVOIRE,    "text": ENCRE,  "accent": FRAMBOISE},
}

import os as _os; _HERE=_os.path.dirname(_os.path.abspath(__file__))
FONT_DIR   = _os.environ.get("KIT_FONTS", _os.path.join(_HERE, "..", "fonts"))
UPLOAD_DIR = "/root/.claude/uploads/0c8422a9-5b9f-5b30-b210-cfeff47f4b1d"
LOCKUP_RGBA = f"{UPLOAD_DIR}/bcb793b7-ollockupencre.png"        # encre + point framboise, fond transparent
EMBLEM_SRC  = f"{UPLOAD_DIR}/db5ca437-olvignetteframboise.png"   # cintre-coeur ivoire + point mimosa sur framboise

SCALE = 4

# ------------------------------------------------------------------ polices
def playfair(weight, size):
    f = ImageFont.truetype(f"{FONT_DIR}/PlayfairDisplay.ttf", int(size))
    f.set_variation_by_name(weight)
    return f

def playfair_italic(weight, size):
    f = ImageFont.truetype(f"{FONT_DIR}/PlayfairDisplay-Italic.ttf", int(size))
    f.set_variation_by_name(weight)
    return f

def jost(weight, size):
    f = ImageFont.truetype(f"{FONT_DIR}/Jost.ttf", int(size))
    f.set_variation_by_name(weight)
    return f

# ------------------------------------------------------------------ texte
def text_w(draw, text, font, tracking=0):
    if tracking == 0:
        b = draw.textbbox((0, 0), text, font=font)
        return b[2] - b[0]
    w = 0
    for ch in text:
        b = draw.textbbox((0, 0), ch, font=font)
        w += (b[2] - b[0]) + tracking
    return w - tracking if text else 0

def draw_tracked(draw, y, text, font, fill, tracking=0, cx=None, x=None):
    total = text_w(draw, text, font, tracking)
    px = (cx - total / 2) if cx is not None else x
    for ch in text:
        draw.text((px, y), ch, font=font, fill=fill)
        b = draw.textbbox((0, 0), ch, font=font)
        px += (b[2] - b[0]) + tracking
    return total

def draw_centered(draw, y, text, font, fill, cx):
    b = draw.textbbox((0, 0), text, font=font)
    draw.text((cx - (b[2] - b[0]) / 2 - b[0], y), text, font=font, fill=fill)

def line_height(draw, font):
    b = draw.textbbox((0, 0), "Hxg", font=font)
    return b[3] - b[1]

def ink_height(draw, text, font):
    b = draw.textbbox((0, 0), text, font=font)
    return b[3] - b[1]

# ------------------------------------------------------------------ lockup & emblème recolorés
_lockup_cache = None
def _lockup_layers():
    """Retourne (alpha, dot_mask, bbox_full, bbox_wordmark) du lockup RGBA natif."""
    global _lockup_cache
    if _lockup_cache is None:
        a = np.array(Image.open(LOCKUP_RGBA).convert("RGBA"))
        alpha = a[..., 3].astype(np.float32) / 255.0
        rgb = a[..., :3].astype(int)
        dot = (rgb[..., 0] > 110) & (rgb[..., 1] < 90)          # pixels framboise = les points
        # bbox encre
        ys, xs = np.where(alpha > 0.04)
        bbox_full = (xs.min(), ys.min(), xs.max() + 1, ys.max() + 1)
        # le mot-marque commence après le trou entre coeur et "Oh"
        cols = (alpha > 0.04).sum(axis=0)
        ink = np.where(cols > 0)[0]
        start = ink[0]
        for c in ink[1:]:
            if c - start > 150:      # premier grand trou horizontal
                wm_x0 = c
                break
            start = c
        bbox_wm = (wm_x0, bbox_full[1], bbox_full[2], bbox_full[3])
        _lockup_cache = (alpha, dot, bbox_full, bbox_wm)
    return _lockup_cache

def _recolor(alpha, dot, text_col, accent_col):
    h, w = alpha.shape
    out = np.zeros((h, w, 4), dtype=np.float32)
    col = np.where(dot[..., None], np.array(accent_col, dtype=np.float32), np.array(text_col, dtype=np.float32))
    out[..., :3] = col
    out[..., 3] = alpha * 255
    return Image.fromarray(out.astype(np.uint8), "RGBA")

def lockup(scheme, width, wordmark_only=False):
    """Lockup (coeur + Oh là live !) ou mot-marque seul, recoloré au schéma, largeur d'encre = width px."""
    s = SCHEMES[scheme]
    alpha, dot, bb_full, bb_wm = _lockup_layers()
    bb = bb_wm if wordmark_only else bb_full
    img = _recolor(alpha, dot, s["text"], s["accent"]).crop(bb)
    h = int(round(width * img.height / img.width))
    return img.resize((int(width), h), Image.LANCZOS)

_emblem_cache = None
def _emblem_layers():
    global _emblem_cache
    if _emblem_cache is None:
        v = np.array(Image.open(EMBLEM_SRC).convert("RGB")).astype(np.float32)
        bg = v[2, 2]
        dist = np.abs(v - bg).sum(axis=-1)
        alpha = np.clip((dist - 40.0) / 200.0, 0, 1)             # 0 = fond (grain ignoré), 1 = trait plein
        dot = (v[..., 0] > 200) & (v[..., 1] > 150) & (v[..., 2] < 130)
        ys, xs = np.where(alpha > 0.1)
        bbox = (xs.min(), ys.min(), xs.max() + 1, ys.max() + 1)
        _emblem_cache = (alpha, dot, bbox)
    return _emblem_cache

def emblem(scheme, width):
    """Cintre-coeur en fil continu, trait = couleur texte, pointe de crosse = accent."""
    s = SCHEMES[scheme]
    alpha, dot, bb = _emblem_layers()
    img = _recolor(alpha, dot, s["text"], s["accent"]).crop(bb)
    h = int(round(width * img.height / img.width))
    return img.resize((int(width), h), Image.LANCZOS)

def paste_rgba(canvas, img, x, y):
    canvas.paste(img, (int(x), int(y)), img)

# ------------------------------------------------------------------ finition
def add_grain(img, amount=5, opacity=0.045):
    arr = np.array(img).astype(np.float32)
    noise = np.random.normal(0, amount, arr.shape[:2])
    noise = np.stack([noise] * 3, axis=-1)
    arr[..., :3] = arr[..., :3] * (1 - opacity) + (arr[..., :3] + noise) * opacity
    return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))

def finish(canvas, out_w, out_h):
    img = canvas.resize((out_w, out_h), Image.LANCZOS)
    return add_grain(img)

def contact_sheet(paths, labels, cols, thumb_w, gap=40, bg=IVOIRE, label_col=ENCRE):
    """Planche de comparaison : vignettes + étiquettes."""
    ims = [Image.open(p).convert("RGB") for p in paths]
    ratio = ims[0].height / ims[0].width
    tw, th = thumb_w, int(thumb_w * ratio)
    f = jost("Medium", 22)
    rows = (len(ims) + cols - 1) // cols
    W = cols * tw + (cols + 1) * gap
    H = rows * (th + 44) + (rows + 1) * gap
    sheet = Image.new("RGB", (W, H), bg)
    d = ImageDraw.Draw(sheet)
    for i, (im, lab) in enumerate(zip(ims, labels)):
        r, c = divmod(i, cols)
        x = gap + c * (tw + gap)
        y = gap + r * (th + 44 + gap)
        sheet.paste(im.resize((tw, th), Image.LANCZOS), (x, y))
        draw_tracked(d, y + th + 12, lab, f, label_col, tracking=2, cx=x + tw / 2)
    return sheet
