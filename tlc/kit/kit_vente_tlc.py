#!/usr/bin/env python3
"""
Kit visuel par vente — THE LIVE CORNER (gabarit validé par Joseph le 19/09/2026).

Hiérarchie : logo TLC en grand · « VENTE EXCLUSIVE » en petit · nom de la marque
en très grand (Fraunces) · « Jusqu'à −XX % » en petit (accent couleur) · filet ·
date · « En live sur Whatnot ». Fond papier #F3EEE3 (ou la couleur de la marque), sac(s)
détouré(s) posé(s) en bas avec une ombre douce.

Depuis le 05/10/2026 (Joseph, vente Lancaster 3) :
  - KIT 5 par défaut (« un peu moins de visuels, c'est trop ») : post annonce 4:5, story annonce, story veille
    (« Enregistre le live pour être prévenue », programmée J-1 12h), story « C'est ce soir », hero site, + 1 réel
    (tlc_reels.py --which r1, programmé J-1 12h). `--court` = l'ancien kit express (22 fichiers), `--complet` = intégral.
  - Wording : « VENTE EXCLUSIVE » / « Vente exclusive jusqu'à −XX % » (plus « vente privée »).
  - Texte CENTRÉ (Joseph, 05/10/2026 : « écrire le texte au centre et centré, c'est mieux ») : sur couverture et coin,
    le bloc remise · date · Whatnot · logo est centré horizontalement, bas du bloc à 86 % de la hauteur.
  - « sur Whatnot » est écrit sur TOUS les visuels : la ligne « En live » devient « En live sur Whatnot »
    (bloc typo, packshots, bandeau site, tuile prix) et une ligne « En live sur Whatnot » est ajoutée sous
    la date sur les pleines pages (sponso, coin, couverture, manchette).
  - KIT COURT par défaut (« moins de versions des posts, ça sert à rien ») : typo papier (post, story, carré)
    + couleur (post, story) ; packshots papier seulement ; manchette packshot sur couleur ; duo / vestiaire ;
    par photo portée : couverture (post + story) si la tête est entière, sinon coin ; sponso (post + story)
    seulement pour la photo héro ; bandeau site. Plus de « encre », plus de « portée », plus de packshot
    couleur. `--complet` rend l'ancien kit intégral (99 fichiers).

Usage :
  python3 kit_vente_tlc.py --marque Lancaster --date "Mercredi 7 octobre" \
      --heure 18h --remise 80 --couleur "#F5A11A" \
      --packshots ./packshots --portees ./portees --out ./kit_lancaster

--packshots : photos produit sur fond blanc (jpg/png/webp), une par sac.
--portees   : photos portées (mannequin), facultatif.
--remise    : entier ; 0 = pas de ligne « Jusqu'à ».
--prix      : CSV « fichier;modele;prix_tlc;prix_boutique[;ancrage] ».
--hero      : photo portée du bandeau site et de la sponso (défaut : la première).
--complet   : kit intégral (toutes les variantes) au lieu du kit court.
--retour    : « DE RETOUR AU CORNER » à la place de « VENTE EXCLUSIVE » sur la manchette (2e passage, à valider).
Pré-requis : fonts/Fraunces.ttf, fonts/Archivo.ttf, assets/A_vertical_transparent.svg,
assets/B_horizontal_transparent.svg (sponso). pip: pillow numpy cairosvg (+ rembg onnxruntime pour la couverture).
"""
import argparse, io, os, glob, csv
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import cairosvg

INK = "#1F1B17"; PAPER = "#F3EEE3"
DATE_PX = 60      # date + heure dans le bloc typo (30/09/2026 : « plus gros, surtout les horaires »)
LIVE_PX = 40      # « En live sur Whatnot » dans le bloc typo
PAGE_DATE_PX = 56 # date + heure sur les pleines pages sponso / coin / couverture / manchette
PAGE_LIVE_PX = 40 # « En live sur Whatnot » sur les pleines pages (05/10/2026)
LIVE_LINE = "En live sur Whatnot"   # Joseph, 05/10/2026 : « écris bien que c'est sur Whatnot »
VEILLE_LINE = "Enregistre le live pour être prévenue"   # story de la veille 12h (Joseph, 05/10/2026), programmée dans Postiz
SPONSO_LOGO_PX = 440  # logo B sur la sponso (Joseph, 30/09/2026 : 140 trop petit, 540 et 800 trop gros)
HERE = os.path.dirname(os.path.abspath(__file__))
FONT_F = os.path.join(HERE, "fonts", "Fraunces.ttf")
FONT_A = os.path.join(HERE, "fonts", "Archivo.ttf")
LOGO = os.path.join(HERE, "assets", "A_vertical_transparent.svg")
LOGO_B = os.path.join(HERE, "assets", "B_horizontal_transparent.svg")

# ---------- typo & logo ----------
def OPSZ_FIX(s):
    # 06/10/2026 : taille optique réelle sous 144 px (le « − » et les déliés disparaissaient en opsz 144)
    return max(9, min(144, s))
def fraunces(s, w=500):
    f = ImageFont.truetype(FONT_F, s); f.set_variation_by_axes([OPSZ_FIX(s), 0, w, 1]); return f   # opsz, SOFT, wght, WONK
def archivo(s, w=500):
    f = ImageFont.truetype(FONT_A, s); f.set_variation_by_axes([w, 100]); return f          # wght, wdth
def lockup(w):
    return Image.open(io.BytesIO(cairosvg.svg2png(url=LOGO, output_width=w))).convert("RGBA")
def spaced_w(d, t, f, sp): return sum(d.textlength(c, font=f) for c in t) + sp * (len(t) - 1)
def spaced(d, cx, y, t, f, fill, sp):
    x = cx - spaced_w(d, t, f, sp) / 2
    for c in t: d.text((x, y), c, font=f, fill=fill); x += d.textlength(c, font=f) + sp
def center(d, cx, y, t, f, fill): d.text((cx - d.textlength(t, font=f) / 2, y), t, font=f, fill=fill)

# ---------- images ----------
def cutout(path, thresh=10, gain=10):
    """Détoure un packshot sur fond blanc (blanc -> transparent, bord doux). Un PNG déjà détouré est gardé tel quel."""
    im0 = Image.open(path)
    if im0.mode in ("RGBA", "LA") and np.array(im0.split()[-1]).min() < 10:
        out = im0.convert("RGBA"); bb = out.getbbox()
        return out.crop(bb) if bb else out
    im = im0.convert("RGB"); a = np.array(im).astype(int)
    h, w, _ = a.shape; k = max(8, min(h, w) // 25)
    corners = np.concatenate([a[:k, :k].reshape(-1, 3), a[:k, -k:].reshape(-1, 3), a[-k:, :k].reshape(-1, 3), a[-k:, -k:].reshape(-1, 3)])
    bg = np.median(corners, axis=0)   # blanc pur, ou gris clair de studio (Missoni : ~232)
    dist = np.abs(a - bg).max(axis=2); alpha = np.clip((dist - thresh) * gain, 0, 255).astype(np.uint8)
    out = Image.fromarray(np.dstack([a, alpha]).astype(np.uint8), "RGBA"); bb = out.getbbox()
    if bb:
        x0, y0, x1, y1 = bb; mw = int((x1 - x0) * 0.03); mh = int((y1 - y0) * 0.03)
        out = out.crop((max(0, x0 - mw), max(0, y0 - mh), min(out.width, x1 + mw), min(out.height, y1 + mh)))
    return out
def fit(bag, maxw, maxh):
    r = min(maxw / bag.width, maxh / bag.height)
    return bag.resize((int(bag.width * r), int(bag.height * r)), Image.LANCZOS)
def shadow(im, bag, bx, by):
    sh = Image.new("RGBA", (bag.width + 120, 120), (0, 0, 0, 0))
    ImageDraw.Draw(sh).ellipse((40, 30, bag.width + 80, 90), fill=(0, 0, 0, 55))
    sh = sh.filter(ImageFilter.GaussianBlur(22)); im.paste(sh, (bx - 60, by + bag.height - 70), sh)

# ---------- le bloc typographique (le cœur du gabarit) ----------
class Kit:
    def __init__(self, marque, date, heure, remise, couleur, out, court=True, retour=False):
        self.marque, self.date, self.heure, self.remise, self.couleur, self.out = marque, date, heure, remise, couleur, out
        self.court, self.retour = court, retour
        self.when_comma = f"{date}, {heure}" if heure else date
        self.when_dot = f"{date} · {heure}" if heure else date
        os.makedirs(out, exist_ok=True)

    def big_size(self, d, base, maxw):
        s = base
        while s > 60 and d.textlength(self.marque, font=fraunces(s)) > maxw: s -= 4
        return s

    def block(self, im, d, cx, y0, y1, ink, accent, logo_w=120, big=140, small=54, maxw=None, date_px=None, live_px=None):
        W = im.width; maxw = maxw or W - 120
        DATE_PX_ = date_px or DATE_PX; LIVE_PX_ = live_px or LIVE_PX
        big = self.big_size(d, big, maxw)
        fk = archivo(26 if logo_w >= 250 else 24, 600); f_b = fraunces(big, 500); f_p = fraunces(small, 400)
        f_d = fit_archivo(d, self.when_comma, DATE_PX_, maxw, w=500, sp=0); f_l = fit_archivo(d, LIVE_LINE, LIVE_PX_, maxw, w=500, sp=0)
        lk = lockup(logo_w)
        bb = d.textbbox((0, 0), self.marque, font=f_b); bh = bb[3] - bb[1]
        promo = f"Jusqu’à −{self.remise} %" if self.remise else ""
        pb = d.textbbox((0, 0), promo, font=f_p) if promo else (0, 0, 0, 0); ph = (pb[3] - pb[1]) if promo else 0
        total = lk.height + 48 + 24 + 34 + bh + (40 + ph if promo else 0) + 46 + 2 + 40 + DATE_PX_ + 22 + LIVE_PX_
        y = y0 + (y1 - y0 - total) // 2
        im.paste(lk, (cx - lk.width // 2, y), lk); y += lk.height + 48
        spaced(d, cx, y, "VENTE EXCLUSIVE", fk, ink, 7); y += 58
        center(d, cx, y - bb[1], self.marque, f_b, ink); y += bh + 40
        if promo: center(d, cx, y - pb[1], promo, f_p, accent); y += ph + 46
        else: y += 6
        d.line((cx - 40, y, cx + 40, y), fill=ink, width=2); y += 40
        center(d, cx, y, self.when_comma, f_d, ink); y += DATE_PX_ + 22
        center(d, cx, y, LIVE_LINE, f_l, ink)

    def _fit_name(self, d, base, maxw, weight=500):
        s = base
        while s > 60 and d.textlength(self.marque, font=fraunces(s, weight)) > maxw: s -= 4
        return s

    # --- pleines pages (validées le 19/09/2026 ; ligne Whatnot ajoutée le 05/10/2026) ---
    def sponso(self, photo, key, anchor=0.0, ty=0.40):
        """« Sponso » : photo assombrie, nom centré, « Vente exclusive jusqu'à −XX % », date, « En live sur Whatnot »,
        logo B horizontal à 440 px centré en bas."""
        for tag, W, H in (("post", 1080, 1350), ("story", 1080, 1920)):
            s = W / 1080; im = darken(cover_img(photo, W, H, anchor), band_y=0.60); d = ImageDraw.Draw(im); cx = W // 2
            f_b = fraunces(self._fit_name(d, int(190 * s), W - 140)); f_p = fraunces(int(62 * s), 400)
            l2 = f"Vente exclusive jusqu’à −{self.remise} %" if self.remise else "Vente exclusive"
            l3 = self.when_dot; f_d = fit_archivo(d, l3, int(PAGE_DATE_PX * s), W - 120)
            f_l = fit_archivo(d, LIVE_LINE, int(PAGE_LIVE_PX * s), W - 120, w=500, sp=1.5)
            bb = d.textbbox((0, 0), self.marque, font=f_b); bh = bb[3] - bb[1]; pb = d.textbbox((0, 0), l2, font=f_p); ph = pb[3] - pb[1]
            y = int(ty * H) - (bh + int(34 * s) + ph + int(48 * s) + int(PAGE_DATE_PX * s) + int(16 * s) + int(PAGE_LIVE_PX * s)) // 2
            center(d, cx, y - bb[1], self.marque, f_b, PAPER); y += bh + int(34 * s)
            center(d, cx, y - pb[1], l2, f_p, PAPER); y += ph + int(48 * s)
            spaced(d, cx, y, l3, f_d, PAPER, 1.0); y += int(PAGE_DATE_PX * s) + int(16 * s)
            spaced(d, cx, y, LIVE_LINE, f_l, PAPER, 1.5)
            lk = logo_b_col(int(SPONSO_LOGO_PX * s), PAPER); by = H - int((250 if tag == "story" else 70) * s)
            im.paste(lk, (cx - lk.width // 2, by - lk.height), lk)
            self.save(im, f"sponso_{key}_{tag}")

    def _bottom_lines(self, d, m, H, col, s=1.0, W=1080):
        """Bloc bas commun (coin, couverture, manchette) : remise, date · heure, « En live sur Whatnot ». Retourne le y du haut."""
        f_l = fit_archivo(d, LIVE_LINE, int(PAGE_LIVE_PX * s), W - 2 * m, w=500, sp=1.5)
        y = H - m - int(PAGE_LIVE_PX * s); tracked(d, m, y, LIVE_LINE, f_l, col, 1.5)
        f_d = fit_archivo(d, self.when_dot, int(PAGE_DATE_PX * s), W - 2 * m)
        y -= int(PAGE_DATE_PX * s) + int(14 * s); tracked(d, m, y, self.when_dot, f_d, col, 1.0)
        return y

    def _bloc_centre(self, d, W, H, col, bottom_frac=0.86):
        """Bloc texte centré (Joseph, 05/10/2026 : « le texte au centre et centré, c'est mieux ») :
        « Vente exclusive jusqu'à −XX % » · date · heure · « En live sur Whatnot » · logo, le tout centré,
        bas du bloc à bottom_frac × H. Retourne le y du haut du bloc."""
        cx = W // 2; m = 64
        f_p = fraunces(62, 400); f_d = fit_archivo(d, self.when_dot, PAGE_DATE_PX, W - 2 * m)
        f_l = fit_archivo(d, LIVE_LINE, PAGE_LIVE_PX, W - 2 * m, w=500, sp=1.5)
        l2 = f"Vente exclusive jusqu’à −{self.remise} %" if self.remise else "Vente exclusive"
        pb = d.textbbox((0, 0), l2, font=f_p); ph = pb[3] - pb[1]
        lk = logo_col(120, col)
        extra = getattr(self, "extra", None); f_e = fraunces(44, 400) if extra else None
        eb = d.textbbox((0, 0), extra, font=f_e) if extra else (0, 0, 0, 0); eh = (eb[3] - eb[1] + 30) if extra else 0
        total = ph + 36 + PAGE_DATE_PX + 14 + PAGE_LIVE_PX + eh + 40 + lk.height
        y = int(H * bottom_frac) - total; top = y
        center(d, cx, y - pb[1], l2, f_p, col); y += ph + 36
        spaced(d, cx, y, self.when_dot, f_d, col, 1.0); y += PAGE_DATE_PX + 14
        spaced(d, cx, y, LIVE_LINE, f_l, col, 1.5); y += PAGE_LIVE_PX
        if extra: y += 30; center(d, cx, y - eb[1], extra, f_e, col); y += eb[3] - eb[1]
        y += 40
        return top, lk, y

    def couverture(self, photo, key, mask, anchor=0.0, W=1080, H=1350, ext=0.16, tag="post"):
        """« Couverture » : nom en manchette tout en haut, la mannequin passe devant les lettres, photo claire."""
        g = np.array(photo.convert("L")).astype(float); mk0 = np.array(mask).astype(float) / 255
        n0 = max(4, int(g.shape[0] * 0.06)); bgpix = g[:n0][mk0[:n0] < 0.2]
        patterned = bgpix.size > 100 and bgpix.std() > 10
        if patterned: ext = 0
        photo2, mask2 = extend_top(photo, mask, ext)
        base = cover_img(photo2, W, H, anchor); mk = cover_img(mask2, W, H, anchor)
        txt = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(txt)
        f_b = fraunces(self._fit_name(d, 280, W - 96)); bb = d.textbbox((0, 0), self.marque, font=f_b)
        top = 48
        if patterned:
            rows = np.array(mk).astype(float).mean(axis=1) / 255
            idx = np.where(rows > 0.02)[0]; head_top = int(idx[0]) if len(idx) else int(H * 0.3)
            bh = bb[3] - bb[1]; top = int(min(max(40, head_top - 0.62 * bh), H * 0.45 - bh))
        d.text(((W - (bb[2] - bb[0])) / 2 - bb[0], top - bb[1]), self.marque, font=f_b, fill=INK)
        out = Image.alpha_composite(base.convert("RGBA"), txt); out.paste(base, (0, 0), mk)
        zone = np.array(base.crop((0, int(H * 0.60), W, int(H * 0.88))).convert("L"))
        studio_clair = bgpix.size > 100 and bgpix.mean() > 170
        block_top = int(H * 0.86) - 400
        if studio_clair or (zone.mean() > 150 and np.percentile(zone, 15) > 110):
            out = out.convert("RGB"); col = INK
            mkz = np.array(mk.crop((160, block_top, W - 160, int(H * 0.86)))).astype(float) / 255
            if mkz.mean() > 0.06: out = veil_bottom(out, from_y=block_top - 60)
        else:
            g0 = int(H * 0.46)
            out = Image.composite(Image.new("RGBA", (W, H), (14, 12, 10, 255)), out, vgrad_img(W, H, lambda y: (y - g0) / (H - g0) * 215)).convert("RGB"); col = PAPER
        d = ImageDraw.Draw(out)
        top_y, lk, y_logo = self._bloc_centre(d, W, H, col)
        out.paste(lk, (W // 2 - lk.width // 2, y_logo), lk)
        self.save(out, f"couverture_{key}_{tag}")

    def coin(self, photo, key, anchor=0.0):
        """« Coin » : nom + bloc centrés dans le bas de l'image (centré depuis le 05/10/2026)."""
        for tag, W, H in (("post", 1080, 1350), ("story", 1080, 1920)):
            s = W / 1080; base = cover_img(photo, W, H, anchor); g0 = int(H * 0.40)
            out = Image.composite(Image.new("RGB", (W, H), (14, 12, 10)), base, vgrad_img(W, H, lambda y: (y - g0) / (H - g0) * 215))
            d = ImageDraw.Draw(out); m = int(64 * s); cx = W // 2
            f_b = fraunces(self._fit_name(d, int(210 * s), W - 2 * m)); fk = archivo(int(30 * s), 600)
            bb = d.textbbox((0, 0), self.marque, font=f_b)
            top_y, lk, y_logo = self._bloc_centre(d, W, H, PAPER)
            out.paste(lk, (cx - lk.width // 2, y_logo), lk)
            y = top_y - int(26 * s) - (bb[3] - bb[1]); center(d, cx, y - bb[1], self.marque, f_b, PAPER)
            y -= int(66 * s); spaced(d, cx, y, "VENTE EXCLUSIVE", fk, PAPER, 8)
            self.save(out, f"coin_{key}_{tag}")

    def coin_clair(self, photo, key, anchor=0.0):
        """« Coin clair » (proposition du 30/09/2026) : photo intacte, voile papier qui monte du bas, texte en encre."""
        for tag, W, H in (("post", 1080, 1350), ("story", 1080, 1920)):
            s = W / 1080; base = cover_img(photo, W, H, anchor)
            out = veil_bottom(base, from_y=int(H * 0.50))
            d = ImageDraw.Draw(out); m = int(64 * s)
            f_b = fraunces(self._fit_name(d, int(210 * s), W - 2 * m)); f_p = fraunces(int(60 * s), 400); fk = archivo(int(30 * s), 600)
            l2 = f"Vente exclusive jusqu’à −{self.remise} %" if self.remise else "Vente exclusive"
            bb = d.textbbox((0, 0), self.marque, font=f_b)
            y = self._bottom_lines(d, m, H, INK, s, W)
            if self.remise: y -= int(96 * s); d.text((m, y), l2, font=f_p, fill=INK)
            else: y -= int(34 * s)
            y -= (bb[3] - bb[1]) + int(26 * s); d.text((m - bb[0], y - bb[1]), self.marque, font=f_b, fill=INK)
            y -= int(66 * s); tracked(d, m, y, "VENTE EXCLUSIVE", fk, INK, 8)
            top = np.array(base.crop((W - 260, 40, W - 40, 260)).convert("L")).mean()
            lk = logo_col(int(130 * s), INK if top > 140 else PAPER); out.paste(lk, (W - m - lk.width, m - 8), lk)
            self.save(out, f"coinclair_{key}_{tag}")

    def manchette(self, bag, key):
        """« Manchette packshot » (proposée le 30/09/2026, Lancaster 2) : le nom en manchette géante, le sac détouré
        passe devant les lettres, sur la couleur de la vente (kit complet : aussi sur papier)."""
        fonds = [("couleur", self.couleur)] + ([] if self.court else [("papier", PAPER)])
        for tag, W, H in (("post", 1080, 1350), ("story", 1080, 1920)):
            for bg_name, bg in fonds:
                im = Image.new("RGB", (W, H), bg); d = ImageDraw.Draw(im)
                size = 300
                while size > 80 and d.textlength(self.marque, font=fraunces(size)) > W - 80: size -= 4
                f_b = fraunces(size); bb = d.textbbox((0, 0), self.marque, font=f_b)
                top = int(H * (0.08 if H < 1500 else 0.14))
                d.text(((W - (bb[2] - bb[0])) / 2 - bb[0], top - bb[1]), self.marque, font=f_b, fill=INK)
                name_bottom = top + (bb[3] - bb[1])
                b = fit(bag, int(W * 0.78), int(H * 0.50))
                bx = (W - b.width) // 2; by = name_bottom - int((bb[3] - bb[1]) * 0.42)
                shadow(im, b, bx, by); im.paste(b, (bx, by), b)
                m = 64; y = self._bottom_lines(d, m, H, INK, 1.0, W)
                l2 = f"Vente exclusive jusqu’à −{self.remise} %" if self.remise else "Vente exclusive"
                y -= 96; d.text((m, y), l2, font=fraunces(60, 400), fill=INK)
                y -= 58; tracked(d, m, y, "DE RETOUR AU CORNER" if self.retour else "VENTE EXCLUSIVE", archivo(26, 600), INK, 7)
                lk = lockup(130); im.paste(lk, (W - m - lk.width, H - m - lk.height + 8), lk)
                self.save(im, f"manchette_{key}_{bg_name}_{tag}")

    def hero_site(self, photo, key, anchor=0.0):
        """Bandeau site : bloc typo validé à gauche sur papier, photo à droite. 1920×1080 + carré 1080×1080 (mobile)."""
        W, H = 1920, 1080; out = Image.new("RGB", (W, H), PAPER); out.paste(cover_img(photo, W // 2, H, anchor), (W // 2, 0))
        self.block(out, ImageDraw.Draw(out), W // 4, 60, H - 60, INK, self.couleur, logo_w=200, big=170, small=64, maxw=W // 2 - 160)
        self.save(out, f"hero_{key}_1920x1080")
        W = H = 1080; top = int(H * 0.56); out = Image.new("RGB", (W, H), PAPER); out.paste(cover_img(photo, W, H - top, anchor if anchor > 0 else 0.35), (0, top))
        self.block(out, ImageDraw.Draw(out), W // 2, 24, top - 16, INK, self.couleur, logo_w=80, big=96, small=36, date_px=38, live_px=28)
        self.save(out, f"hero_{key}_1080x1080")

    def save(self, im, name):
        p = os.path.join(self.out, name + ".png"); im.save(p, optimize=True); return p

    # --- 1. cartes typo (sans photo) ---
    def typo(self):
        for (W, H, tag) in [(1080, 1350, "post"), (1080, 1920, "story"), (1080, 1080, "carre")]:
            variantes = [(PAPER, INK, self.couleur, "papier"), (self.couleur, INK, INK, "couleur"), (PAPER, INK, INK, "encre")]
            if self.court: variantes = [(PAPER, INK, self.couleur, "papier")] + ([(self.couleur, INK, INK, "couleur")] if tag != "carre" else [])
            for bg, ink, accent, v in variantes:
                im = Image.new("RGB", (W, H), bg); d = ImageDraw.Draw(im)
                top = int(H * 0.13) if H > W * 1.4 else int(H * 0.09)
                self.block(im, d, W // 2, top, H - top, ink, accent, logo_w=300, big=212, small=88)
                self.save(im, f"typo_{v}_{tag}")

    # --- 2. packshot : un sac détouré, bloc au-dessus ---
    def packshot(self, bag, key):
        for (W, H, tag) in [(1080, 1350, "post"), (1080, 1920, "story")]:
            variantes = [(PAPER, INK, self.couleur, "papier")] + ([] if self.court else [(self.couleur, INK, INK, "couleur")])
            for bg, ink, accent, v in variantes:
                im = Image.new("RGB", (W, H), bg); d = ImageDraw.Draw(im)
                b = fit(bag, int(W * 0.62), int(H * 0.40)); bx = (W - b.width) // 2; by = H - int(H * 0.07) - b.height
                shadow(im, b, bx, by); im.paste(b, (bx, by), b)
                top = int(H * 0.05) if H < 1500 else int(H * 0.12)
                self.block(im, d, W // 2, top, by - 20, ink, accent)
                self.save(im, f"packshot_{key}_{v}_{tag}")

    # --- 3. duo et vestiaire ---
    def duo(self, bags):
        W, H = 1080, 1350; im = Image.new("RGB", (W, H), PAPER); d = ImageDraw.Draw(im)
        b1, b2 = fit(bags[0], 440, 400), fit(bags[1], 440, 400); base = H - 95; gap = 40
        x = (W - (b1.width + gap + b2.width)) // 2
        for b in (b1, b2):
            by = base - b.height; shadow(im, b, x, by); im.paste(b, (x, by), b); x += b.width + gap
        self.block(im, d, W // 2, 50, base - max(b1.height, b2.height) - 30, INK, self.couleur)
        self.save(im, "duo")
    def vestiaire(self, bags):
        W, H = 1080, 1350; im = Image.new("RGB", (W, H), PAPER); d = ImageDraw.Draw(im)
        cw, ch = 420, 300; gx = (W - 2 * cw - 60) // 2; gy = H - 70 - 2 * ch - 40
        for n, b0 in enumerate(bags[:4]):
            i, j = n % 2, n // 2; b = fit(b0, cw - 40, ch - 40)
            x = gx + i * (cw + 60) + (cw - b.width) // 2; y = gy + j * (ch + 40) + (ch - b.height)
            shadow(im, b, x, y); im.paste(b, (x, y), b)
        self.block(im, d, W // 2, 40, gy - 20, INK, self.couleur, logo_w=110, big=130, small=50)
        self.save(im, "vestiaire")

    # --- 4. photo portée : photo en haut, bloc en bas (kit complet seulement) ---
    def portee(self, path, key, anchor=0.70, split=620):
        W, H = 1080, 1350
        im = Image.open(path).convert("RGB"); r = W / im.width; im = im.resize((W, int(im.height * r)), Image.LANCZOS)
        y0 = int(anchor * max(0, im.height - split)); im = im.crop((0, y0, W, y0 + split))
        out = Image.new("RGB", (W, H), PAPER); out.paste(im, (0, 0)); d = ImageDraw.Draw(out)
        self.block(out, d, W // 2, split + 10, H - 40, INK, self.couleur)
        self.save(out, f"portee_{key}")

    # --- 5. tuile prix (validée 19/09/2026) ---
    def prix(self, path, key, modele, p_tlc, p_btq, anchor=0.25):
        SOFT = (200, 194, 184)
        def strike(d, x, y, t, f, fill):
            d.text((x, y), t, font=f, fill=fill); bb = d.textbbox((x, y), t, font=f); ym = (bb[1] + bb[3]) // 2
            d.line((bb[0] - 4, ym, bb[2] + 4, ym), fill=fill, width=3)
        photo = Image.open(path).convert("RGB")
        for (W, H, tag) in [(1080, 1350, "post"), (1080, 1920, "story")]:
            s = W / 1080; im = cover_img(photo, W, H, anchor)
            g0 = int(H * 0.60); im = Image.composite(Image.new("RGB", (W, H), (20, 18, 16)), im, vgrad_img(W, H, lambda y: (y - g0) / (H - g0) * 220))
            g1 = int(H * 0.36); im = Image.composite(Image.new("RGB", (W, H), PAPER), im, vgrad_img(W, H, lambda y: (g1 - y) / g1 * 235))
            d = ImageDraw.Draw(im); m = int(60 * s); y = int(56 * s) if H < 1500 else int(130 * s)
            lk = lockup(int(110 * s)); im.paste(lk, (W - m - lk.width, y), lk)
            x = m
            for ch in "VENTE EXCLUSIVE": d.text((x, y), ch, font=archivo(int(34 * s), 600), fill=INK); x += d.textlength(ch, font=archivo(int(34 * s), 600)) + int(6 * s)
            y += int(50 * s)
            fb = fraunces(self.big_size(d, int(150 * s), W - 2 * m - int(150 * s))); bb = d.textbbox((0, 0), self.marque, font=fb)
            d.text((m - 4, y - bb[1]), self.marque, font=fb, fill=INK); y += (bb[3] - bb[1]) + int(28 * s)
            d.text((m, y), self.when_dot, font=archivo(int(54 * s), 600), fill=INK); y += int(72 * s)
            d.text((m, y), LIVE_LINE, font=archivo(int(40 * s)), fill=INK)
            bot = H - int(250 * s) if H < 1500 else H - int(330 * s)
            d.text((m, bot), modele, font=archivo(int(30 * s), 500), fill=PAPER)
            fp = fraunces(int(124 * s)); yp = bot + int(48 * s); d.text((m - 4, yp), f"{p_tlc} €", font=fp, fill=PAPER)
            px = m + d.textlength(f"{p_tlc} €", font=fp) + int(34 * s)
            strike(d, px, yp + int(64 * s), f"{p_btq} €", archivo(int(40 * s)), SOFT)
            d.text((px, yp + int(114 * s)), "prix boutique", font=archivo(int(20 * s)), fill=SOFT)
            self.save(im, f"prix_{key}_{tag}")


# ---------- outils ----------
def logo_col(w, col):
    svg = open(LOGO, encoding="utf-8").read().replace('fill="#1F1B17"', f'fill="{col}"')
    return Image.open(io.BytesIO(cairosvg.svg2png(bytestring=svg.encode(), output_width=w))).convert("RGBA")

def logo_b_col(w, col):
    svg = open(LOGO_B, encoding="utf-8").read().replace('fill="#1F1B17"', f'fill="{col}"')
    im = Image.open(io.BytesIO(cairosvg.svg2png(bytestring=svg.encode(), output_width=w * 3))).convert("RGBA")
    im = im.crop(im.getbbox()); return im.resize((w, int(w * im.height / im.width)), Image.LANCZOS)

def trim_border(im, maxfrac=0.03):
    a = np.array(im.convert("L")).astype(float); h, w = a.shape
    def flat(v): return v.std() < 3 and (v.mean() > 246 or v.mean() < 8)
    t = b = l = r = 0
    while t < h * maxfrac and flat(a[t]): t += 1
    while b < h * maxfrac and flat(a[h - 1 - b]): b += 1
    while l < w * maxfrac and flat(a[:, l]): l += 1
    while r < w * maxfrac and flat(a[:, w - 1 - r]): r += 1
    return im.crop((l, t, w - r, h - b)) if (t or b or l or r) else im

def cover_img(im, W, H, anchor=0.0):
    r = max(W / im.width, H / im.height)
    im = im.resize((int(im.width * r), int(im.height * r)), Image.LANCZOS)
    x0 = (im.width - W) // 2; y0 = int(anchor * max(0, im.height - H))
    return im.crop((x0, y0, x0 + W, y0 + H))

def vgrad_img(W, H, f):
    g = Image.new("L", (1, H)); px = g.load()
    for y in range(H): px[0, y] = int(max(0, min(255, f(y))))
    return g.resize((W, H))

def subject_mask(im):
    try:
        from rembg import remove, new_session
        sess = new_session("u2net")
        small = im.convert("RGB"); r = 640 / small.width
        small = small.resize((640, int(small.height * r)), Image.LANCZOS)
        return remove(small, session=sess, only_mask=True).resize(im.size, Image.LANCZOS).filter(ImageFilter.GaussianBlur(0.8))
    except Exception as e:
        print("rembg indisponible, masque couleur :", e)
        a = np.array(im.convert("RGB")).astype(float); h, w, _ = a.shape
        bg = np.concatenate([a[:h//12, :w//8].reshape(-1, 3), a[:h//12, -w//8:].reshape(-1, 3)]).mean(axis=0)
        dist = np.sqrt(((a - bg) ** 2).sum(axis=2))
        return Image.fromarray(np.clip((dist - 18) * 8, 0, 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(1.2))

def head_in_frame(mask, frac=0.01):
    a = np.array(mask).astype(float) / 255
    return a[: max(2, int(a.shape[0] * frac))].mean() < 0.05

def extend_top(im, mask, frac=0.16):
    if frac <= 0: return im, mask
    a = np.array(im.convert("RGB")).astype(float); mk = np.array(mask).astype(float) / 255
    h, w, _ = a.shape; n = int(h * frac); R = max(12, h // 12)
    def row_bg(r, cols):
        sub = a[r, cols]; wm = 1 - mk[r, cols]
        return (sub * wm[:, None]).sum(axis=0) / max(wm.sum(), 1) if wm.sum() > 5 else None
    L, Rr, idx = [], [], []
    for r in range(R):
        l = row_bg(r, slice(0, w // 5)); rr = row_bg(r, slice(-w // 5, None))
        if l is not None and rr is not None: L.append(l); Rr.append(rr); idx.append(r)
    L, Rr, idx = np.array(L), np.array(Rr), np.array(idx, dtype=float)
    def extrap(vals):
        k = np.polyfit(idx, vals, 1); slope = k[0] * 0.6; base = vals[:6].mean(axis=0)
        rows = -np.arange(n, 0, -1)[:, None]
        return base[None, :] + slope[None, :] * rows
    pl, pr = extrap(L), extrap(Rr)
    t = np.linspace(0, 1, w)[None, :, None]
    pad = pl[:, None, :] * (1 - t) + pr[:, None, :] * t + np.random.normal(0, 1.0, (n, w, 3))
    out = Image.fromarray(np.clip(np.concatenate([pad, a], axis=0), 0, 255).astype(np.uint8))
    mout = Image.new("L", (w, h + n), 0); mout.paste(mask, (0, n))
    return out, mout

def veil_bottom(im, from_y, strength=0.86):
    W, H = im.size; y = np.arange(H)
    t = np.clip((y - from_y) / max(1, (H - from_y) * 0.55), 0, 1); g = (t ** 1.4) * strength * 255
    mask = Image.fromarray(g.astype(np.uint8)).resize((1, H)).resize((W, H))
    return Image.composite(Image.new("RGB", (W, H), PAPER), im.convert("RGB"), mask)

def darken(im, base=0.30, band_y=0.60, band=0.32, band_h=0.24):
    W, H = im.size; y = np.arange(H) / H
    a = np.clip(base + band * np.exp(-((y - band_y) / band_h) ** 2 * 2.0), 0, 0.75)
    mask = Image.fromarray((a * 255).astype(np.uint8)).resize((1, H)).resize((W, H))
    return Image.composite(Image.new("RGB", (W, H), (14, 12, 10)), im, mask)

def tracked(d, x, y, t, f, fill, sp):
    for c in t: d.text((x, y), c, font=f, fill=fill); x += d.textlength(c, font=f) + sp

def fit_archivo(d, t, px, maxw, w=600, sp=1.0):
    while px > 28 and spaced_w(d, t, archivo(px, w), sp) > maxw: px -= 2
    return archivo(px, w)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--marque", required=True); ap.add_argument("--date", required=True)
    ap.add_argument("--heure", required=True); ap.add_argument("--remise", type=int, default=0)
    ap.add_argument("--couleur", default="#F5A11A")
    ap.add_argument("--packshots", default=None); ap.add_argument("--portees", default=None)
    ap.add_argument("--prix", default=None); ap.add_argument("--hero", default=None)
    ap.add_argument("--out", required=True)
    ap.add_argument("--coin-clair", dest="coin_clair", action="store_true")
    ap.add_argument("--complet", action="store_true", help="kit intégral (toutes les variantes) au lieu du kit 5")
    ap.add_argument("--court", action="store_true", help="kit court (22 fichiers) au lieu du kit 5")
    ap.add_argument("--retour", action="store_true", help="« DE RETOUR AU CORNER » sur la manchette (2e passage, à valider)")
    a = ap.parse_args()
    k = Kit(a.marque, a.date, a.heure, a.remise, a.couleur, a.out, court=not a.complet, retour=a.retour)
    if not (a.complet or a.court):
        return kit_cinq(k, a)
    k.typo()
    bags = []
    if a.packshots:
        for p in sorted(glob.glob(os.path.join(a.packshots, "*"))):
            key = os.path.splitext(os.path.basename(p))[0]
            try: b = cutout(p)
            except Exception as e: print("skip", p, e); continue
            bags.append(b); k.packshot(b, key); k.manchette(b, key)
        if len(bags) >= 2: k.duo(bags)
        if len(bags) >= 4: k.vestiaire(bags)
    anchors = {}
    if a.prix:
        with open(a.prix, encoding="utf-8") as f:
            for row in csv.reader(f, delimiter=";"):
                if len(row) > 4 and row[4].strip() and not row[0].startswith("#"): anchors[row[0].strip()] = float(row[4])
    if a.portees:
        files = sorted(glob.glob(os.path.join(a.portees, "*")))
        hero_key = a.hero or (os.path.splitext(os.path.basename(files[0]))[0] if files else None)
        for p in files:
            key = os.path.splitext(os.path.basename(p))[0]; anc = anchors.get(key, 0.0)
            photo = trim_border(Image.open(p).convert("RGB"))
            if not k.court: k.portee(p, key)
            if (not k.court) or key == hero_key: k.sponso(photo, key, anc)
            if a.coin_clair: k.coin_clair(photo, key, anc)
            mask = subject_mask(photo)
            if head_in_frame(mask):
                k.couverture(photo, key, mask, anc)
                k.couverture(photo, key, mask, anc, W=1080, H=1920, ext=0.20, tag="story")
                if not k.court: k.coin(photo, key, anc)
            else:
                print(f"couverture: tête coupée sur {key}, on passe (coin à la place)")
                k.coin(photo, key, anc)
            if key == hero_key: k.hero_site(photo, key, anc)
    if a.prix and a.portees:
        with open(a.prix, encoding="utf-8") as f:
            for row in csv.reader(f, delimiter=";"):
                if len(row) < 4 or row[0].startswith("#"): continue
                key, modele, p1, p2 = [c.strip() for c in row[:4]]; anc = float(row[4]) if len(row) > 4 and row[4].strip() else 0.25
                if not p1 or not p2: print("prix: pas encore de prix pour", key, "— pas de tuile prix"); continue
                cands = glob.glob(os.path.join(a.portees, key + ".*"))
                if not cands: print("prix: pas de photo portée pour", key); continue
                k.prix(cands[0], key, modele, p1, p2, anc)
    print("OK →", a.out, len(os.listdir(a.out)), "fichiers")

def kit_cinq(k, a):
    """KIT 5 (Joseph, 05/10/2026 : « un peu moins de visuels, c'est trop ») :
    1 post annonce (4:5) · 2 story annonce · 3 story « C'est ce soir » · 4 hero site (1080² + 1920×1080).
    Le réel (5e fichier) est produit par tlc_reels.py. Photo héro = --hero ou la première portée ;
    couverture si la tête est entière, sinon coin ; sans portée : typo papier."""
    hero = None
    if a.portees:
        files = sorted(glob.glob(os.path.join(a.portees, "*")))
        if files:
            hero = next((f for f in files if os.path.splitext(os.path.basename(f))[0] == a.hero), files[0]) if a.hero else files[0]
    cesoir_dot, cesoir_comma = f"C’est ce soir · {k.heure}" if k.heure else "C’est ce soir", f"Ce soir, {k.heure}" if k.heure else "Ce soir"
    if hero:
        key = os.path.splitext(os.path.basename(hero))[0]
        photo = trim_border(Image.open(hero).convert("RGB")); mask = subject_mask(photo)
        anc = 0.0
        if head_in_frame(mask):
            k.couverture(photo, key, mask, anc)                                              # 1 post
            k.couverture(photo, key, mask, anc, W=1080, H=1920, ext=0.20, tag="story")      # 2 story
            k.extra = VEILLE_LINE
            k.couverture(photo, key, mask, anc, W=1080, H=1920, ext=0.20, tag="story_veille")  # 2b story J-1 (programmée)
            k.extra = None
            k.when_dot, k.when_comma = cesoir_dot, cesoir_comma
            k.couverture(photo, key, mask, anc, W=1080, H=1920, ext=0.20, tag="story_cesoir")  # 3 story J-0
        else:
            print(f"kit 5 : tête coupée sur {key} → coin"); k.coin(photo, key, anc)
            k.when_dot, k.when_comma = cesoir_dot, cesoir_comma
            # coin ne produit que post+story : la story J-0 reprend la typo papier
            W, H = 1080, 1920; im = Image.new("RGB", (W, H), PAPER); d = ImageDraw.Draw(im)
            k.block(im, d, W // 2, int(H * 0.13), H - int(H * 0.13), INK, k.couleur, logo_w=300, big=212, small=88); k.save(im, "typo_papier_story_cesoir")
        k.when_dot, k.when_comma = f"{k.date} · {k.heure}" if k.heure else k.date, f"{k.date}, {k.heure}" if k.heure else k.date
        k.hero_site(photo, key, anc)                                                         # 4 hero site
    else:
        for (W, H, tag) in [(1080, 1350, "post"), (1080, 1920, "story")]:
            im = Image.new("RGB", (W, H), PAPER); d = ImageDraw.Draw(im)
            top = int(H * 0.13) if H > W * 1.4 else int(H * 0.09)
            k.block(im, d, W // 2, top, H - top, INK, k.couleur, logo_w=300, big=212, small=88); k.save(im, f"typo_papier_{tag}")
        k.when_dot, k.when_comma = cesoir_dot, cesoir_comma
        W, H = 1080, 1920; im = Image.new("RGB", (W, H), PAPER); d = ImageDraw.Draw(im)
        k.block(im, d, W // 2, int(H * 0.13), H - int(H * 0.13), INK, k.couleur, logo_w=300, big=212, small=88); k.save(im, "typo_papier_story_cesoir")
        print("kit 5 : pas de photo portée → pas de hero site photo ; typo papier seulement")
    print("OK (kit 5) →", a.out, sorted(os.listdir(a.out)))

if __name__ == "__main__":
    main()
