#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Complément du KIT 5 quand il n'y a aucune photo portée (kit typo seul) :
story veille « Enregistre le live pour être prévenue » et hero site (1080² + 1920×1080) sur papier, bloc typo centré.

  python3 kit_typo_complement.py --marque Kouka --date "Mardi 20 octobre" --heure 18h --remise 70 --couleur "#F5A11A" --out ../kouka-2026-10-20
"""
import argparse
from PIL import Image, ImageDraw
from kit_vente_tlc import Kit, PAPER, INK, VEILLE_LINE, fraunces, center

ap = argparse.ArgumentParser()
ap.add_argument("--marque", required=True); ap.add_argument("--date", required=True); ap.add_argument("--heure", required=True)
ap.add_argument("--remise", type=int, default=0); ap.add_argument("--couleur", default="#F5A11A"); ap.add_argument("--out", required=True)
a = ap.parse_args()
k = Kit(a.marque, a.date, a.heure, a.remise, a.couleur, a.out)

# story veille : bloc typo remonté, ligne « Enregistre le live pour être prévenue » sous le bloc
W, H = 1080, 1920
im = Image.new("RGB", (W, H), PAPER); d = ImageDraw.Draw(im)
top = int(H * 0.13); k.block(im, d, W // 2, top - 60, H - top - 60, INK, k.couleur, logo_w=300, big=212, small=88)
f_e = fraunces(44, 400); center(d, W // 2, int(H * 0.80), VEILLE_LINE, f_e, INK)
k.save(im, "typo_papier_story_veille")

# hero site sans photo : bloc typo seul, centré
W, H = 1920, 1080
im = Image.new("RGB", (W, H), PAPER)
k.block(im, ImageDraw.Draw(im), W // 2, 60, H - 60, INK, k.couleur, logo_w=200, big=170, small=64, maxw=W - 400)
k.save(im, "hero_typo_1920x1080")
W = H = 1080
im = Image.new("RGB", (W, H), PAPER)
k.block(im, ImageDraw.Draw(im), W // 2, 60, H - 60, INK, k.couleur, logo_w=160, big=150, small=60)
k.save(im, "hero_typo_1080x1080")
print("OK complément typo →", a.out)
