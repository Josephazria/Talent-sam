#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ohlalive — POST TEASING (feed, portrait 1080x1350).
6 dérivés : 3 couleurs (framboise, mimosa, ivoire) x 2 compositions (A typo, B emblème).
"""
import os, sys
from PIL import Image, ImageDraw
from ohlalive_kit import *

OUT_W, OUT_H = 1080, 1350
W, H = OUT_W * SCALE, OUT_H * SCALE
S = SCALE

def render(scheme, compo, live, s=1.0, dry=False):
    """s = facteur d'échelle global (auto-fit). dry=True -> ne retourne que la hauteur du bloc."""
    sc = SCHEMES[scheme]
    canvas = Image.new("RGB", (W, H), sc["bg"])
    d = ImageDraw.Draw(canvas)
    cx = W // 2

    # --- éléments
    if compo == "A":
        logo = lockup(scheme, 880 * S * s)
        head_size, it_size = 150, 185
    else:
        emb  = emblem(scheme, 250 * S * s)
        logo = lockup(scheme, 700 * S * s, wordmark_only=True)
        head_size, it_size = 138, 170

    f_date  = jost("SemiBold", 34 * S * s)
    f_head  = playfair("Bold", head_size * S * s)
    f_it    = playfair_italic("Medium Italic", it_size * S * s)
    f_foot  = jost("Medium", 24 * S)
    f_hand  = jost("Medium", 20 * S)

    date_txt = live["date_label"]           # ex. "MARDI 22 SEPTEMBRE  ·  12H"
    head_txt = live["title"]                # ex. "Sélection"
    it_txt   = live["title_italic"]         # ex. "de luxe"

    div_w, div_th = int(90 * S), max(int(3 * S), 2)

    g_emb_logo   = int(34 * S * s)
    g_logo_date  = int(64 * S * s)
    g_date_head  = int(40 * S * s)
    g_head_it    = int(18 * S * s)
    g_it_div     = int(64 * S * s)

    lh_date = line_height(d, f_date)
    lh_head = line_height(d, f_head)
    lh_it   = line_height(d, f_it)

    block = (logo.height + g_logo_date + lh_date + g_date_head + lh_head + g_head_it + lh_it + g_it_div + div_th)
    if compo == "B":
        block += emb.height + g_emb_logo

    footer_zone = int(150 * S)
    avail = H - footer_zone - int(60 * S)
    if dry:
        return block, avail

    y = int(60 * S) + (avail - block) // 2

    if compo == "B":
        paste_rgba(canvas, emb, cx - emb.width // 2, y)
        y += emb.height + g_emb_logo

    paste_rgba(canvas, logo, cx - logo.width // 2, y)
    y += logo.height + g_logo_date

    draw_tracked(d, y, date_txt, f_date, sc["accent"], tracking=int(6 * S * s), cx=cx)
    y += lh_date + g_date_head

    draw_centered(d, y, head_txt, f_head, sc["text"], cx)
    y += lh_head + g_head_it

    draw_centered(d, y, it_txt, f_it, sc["text"], cx)
    y += lh_it + g_it_div

    d.rectangle([cx - div_w // 2, y, cx + div_w // 2, y + div_th], fill=sc["accent"])

    # --- pied
    fy = H - int(112 * S)
    draw_tracked(d, fy, "EN LIVE SUR WHATNOT", f_foot, sc["text"], tracking=int(4 * S), cx=cx)
    fy += line_height(d, f_foot) + int(14 * S)
    draw_tracked(d, fy, "@OHLALIVEPARIS", f_hand, sc["accent"], tracking=int(3 * S), cx=cx)

    return finish(canvas, OUT_W, OUT_H)

def build(scheme, compo, live):
    block, avail = render(scheme, compo, live, dry=True)
    s = min(1.0, avail / block) if block > avail else 1.0
    return render(scheme, compo, live, s=s)

LIVE_22_09 = {
    "slug": "2026-09-22",
    "date_label": "MARDI 22 SEPTEMBRE  ·  12H",
    "title": "Sélection",
    "title_italic": "de luxe",
}

if __name__ == "__main__":
    live = LIVE_22_09
    out_dir = f"{os.environ.get('KIT_OUT','kit')}/{live['slug']}/post-teasing"
    os.makedirs(out_dir, exist_ok=True)
    paths, labels = [], []
    for compo, cname in (("A", "A-typo"), ("B", "B-embleme")):
        for scheme in ("framboise", "mimosa", "ivoire"):
            img = build(scheme, compo, live)
            p = f"{out_dir}/{live['slug']}_post-teasing_{cname}_{scheme}.png"
            img.save(p)
            paths.append(p); labels.append(f"{cname.upper()}  ·  {scheme.upper()}")
            print("saved", p)
    sheet = contact_sheet(paths, labels, cols=3, thumb_w=520)
    sp = f"{out_dir}/{live['slug']}_post-teasing_PLANCHE.png"
    sheet.save(sp); print("saved", sp)
