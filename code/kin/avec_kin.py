import sys, os, argparse
sys.path.insert(0, "/home/claude/doctorgane/kin")
from kinetic import *
ap = argparse.ArgumentParser(); ap.add_argument("--out"); ap.add_argument("--preview"); ap.add_argument("--music"); ap.add_argument("--gain", type=float, default=0.5); args = ap.parse_args()
M = "Medium"; SLATE = (52, 66, 104)

# S0 — couverture (image 1 = miniature), statique 0,8 s
s0 = [Grid(100, 10, 540, 560, 48, 10, SLATE, -1.0, 0.0, snd=None),
      Grid(59, 10, 540, 560, 48, 10, CORAL, -1.0, 0.0, snd=None),
      Word("1 HOMME DE 80 ANS", 540, 980, 104, CREAM, -1.0, dur=0.01, anim="fade", snd=None),
      Word("SUR 2", 540, 1110, 150, CREAM, -1.0, dur=0.01, anim="fade", snd=None),
      Word("A UN CANCER DE LA PROSTATE.", 540, 1270, 84, CORAL, -1.0, dur=0.01, anim="fade", snd=None, maxw=1000),
      Word("et ne le saura jamais.", 540, 1390, 54, GREY, -1.0, dur=0.01, anim="fade", font="pop", snd=None)]
S0 = Scene(0.8, s0, bg=NAVY, flash=False)

# S1 — accroche
s1 = [Word("1 HOMME DE 80 ANS", 540, 420, 110, CREAM, 0.1, anim="pop"),
      Word("SUR 2", 540, 660, 320, CORAL, 0.5, anim="slam", snd="slam"),
      Word("A UN CANCER", 540, 900, 100, CREAM, 1.1, anim="pop"),
      Word("DE LA PROSTATE.", 540, 1010, 100, CREAM, 1.3, anim="pop"),
      Word("Et la plupart ne le sauront jamais.", 540, 1250, 60, GREY, 2.1, anim="up", font="pop", snd=None),
      Word("Je t'explique. C'est plus rassurant que ça en a l'air.", 540, 1400, 42, GREY, 2.9, anim="fade", font=M, snd=None)]
S1 = Scene(4.0, s1, bg=DARK)

# S2 — la grille des 100 hommes
s2 = [Word("ON A EXAMINÉ LA PROSTATE", 540, 300, 76, CREAM, 0.1, anim="pop"),
      Word("D'HOMMES MORTS D'AUTRE CHOSE.", 540, 390, 76, CREAM, 0.35, anim="pop", maxw=1000),
      Word("Accident, cœur, vieillesse… jamais de cancer connu.", 540, 480, 40, GREY, 0.8, anim="up", font=M, snd=None),
      Grid(100, 10, 540, 900, 56, 12, SLATE, 1.0, 0.018),
      Grid(59, 10, 540, 900, 56, 12, CORAL, 3.0, 0.03),
      Word("APRÈS 79 ANS :", 540, 1330, 56, GREY, 3.0, anim="up", font="pop", snd=None),
      Word("59 %", 540, 1460, 170, CORAL, 3.3, anim="slam", snd="slam"),
      Word("avaient un cancer. Sans le savoir.", 540, 1590, 50, CREAM, 3.8, anim="up", font="pop", snd=None),
      Word("29 études d'autopsie · Bell et al., 2015", 540, 1680, 32, GREY, 4.4, anim="fade", font="Regular", snd=None)]
S2 = Scene(5.6, s2, bg=NAVY)

# S3 — la thyroïde
s3 = [Word("LA THYROÏDE ?", 540, 440, 130, CREAM, 0.1, anim="pop"),
      Word("PAREIL.", 540, 600, 130, CORAL, 0.45, anim="slam", snd="slam"),
      Word("1 ADULTE SUR 10", 540, 880, 130, CREAM, 1.3, anim="slam", box=CORAL, snd="slam"),
      Word("a un micro-cancer de la thyroïde.", 540, 1030, 56, CREAM, 1.8, anim="up", font="pop", snd=None),
      Word("Sans symptôme. Sans conséquence.", 540, 1110, 48, GREY, 2.2, anim="up", font=M, snd=None),
      Word("Jusqu'à 1 sur 3 en Finlande.", 540, 1300, 60, GREY, 2.8, anim="up", font="pop", snd="pop"),
      Word("12 834 autopsies · Furuya-Kanamori et al., 2016", 540, 1480, 32, GREY, 3.4, anim="fade", font="Regular", snd=None)]
S3 = Scene(4.4, s3, bg=DARK)

# S4 — la phrase
s4 = [Word("BEAUCOUP DE CANCERS", 540, 400, 96, CREAM, 0.1, anim="pop"),
      Word("NE FERONT JAMAIS RIEN.", 540, 510, 96, CORAL, 0.35, anim="pop", maxw=1000),
      Word("Ils grandissent si lentement", 540, 700, 50, GREY, 1.0, anim="up", font=M, snd=None),
      Word("qu'on meurt de tout autre chose, bien avant.", 540, 765, 50, GREY, 1.1, anim="up", font=M, snd=None),
      Word("ON MEURT AVEC.", 540, 1060, 150, CREAM, 2.0, anim="slam", snd="slam"),
      Word("PAS DE.", 540, 1250, 200, CREAM, 2.5, anim="slam", box=CORAL, snd="slam")]
S4 = Scene(4.4, s4, bg=NAVY)

# S5 — la nuance qui compte
s5 = [Word("ALORS ON ARRÊTE", 540, 360, 96, CREAM, 0.1, anim="pop"),
      Word("DE CHERCHER ?", 540, 470, 96, CREAM, 0.3, anim="pop"),
      Word("NON.", 540, 680, 220, CORAL, 0.8, anim="slam", snd="slam"),
      Word("Pour certains cancers, chercher tôt sauve des vies :", 540, 900, 44, GREY, 1.5, anim="up", font=M, snd=None),
      Word("SEIN · CÔLON · COL DE L'UTÉRUS", 540, 990, 60, CREAM, 1.9, anim="pop", maxw=1000),
      Word("Là, on dépiste tout le monde.", 540, 1080, 48, CREAM, 2.3, anim="up", font="pop", snd=None),
      Word("Pour la prostate, c'est plus subtil :", 540, 1300, 44, GREY, 3.0, anim="up", font=M, snd=None),
      Word("on en parle d'abord avec ton médecin.", 540, 1370, 52, CREAM, 3.2, anim="up", font="pop", snd="pop"),
      Word("Chercher, oui. Mais au bon endroit, au bon moment.", 540, 1540, 40, GREY, 3.9, anim="fade", font=M, snd=None)]
S5 = Scene(5.2, s5, bg=DARK)

# S6 — chute
s6 = [Word("LE BUT DE LA MÉDECINE,", 540, 380, 84, CREAM, 0.1, anim="pop"),
      Word("CE N'EST PAS DE TROUVER", 540, 480, 84, CREAM, 0.35, anim="pop"),
      Word("TOUS LES CANCERS.", 540, 600, 110, GREY, 0.6, anim="pop"),
      Word("C'EST DE TROUVER", 540, 880, 110, CREAM, 1.5, anim="slam", snd="slam"),
      Word("CEUX QUI COMPTENT.", 540, 1030, 120, CREAM, 1.8, anim="slam", box=CORAL, snd="slam", maxw=1000),
      Word("Un cancer n'est pas toujours un drame.", 540, 1280, 48, GREY, 2.8, anim="up", font=M, snd=None),
      Word("Parfois, c'est juste de l'âge.", 540, 1350, 48, GREY, 2.95, anim="up", font=M, snd=None),
      Word("Pose-moi ta question en commentaire.", 540, 1560, 44, CREAM, 3.7, anim="up", font="pop", snd=None)]
S6 = Scene(5.2, s6, bg=NAVY)

film = Film([S0, S1, S2, S3, S4, S5, S6])
print("durée", round(film.dur, 2), [round(b, 2) for b in film.bounds])
if args.preview:
    os.makedirs("prev", exist_ok=True)
    import glob
    for f_ in glob.glob("prev/a_*.png"): os.remove(f_)
    for tt in [float(x) for x in args.preview.split(",")]: film.frame(tt).save(f"prev/a_{tt:05.2f}.png")
    sys.exit()
mus = load_music(args.music, film.dur) if args.music else None
film.make_audio("sound_avec.wav", music=mus, music_gain=args.gain)
film.encode(args.out or "avec_kin.mp4", "sound_avec.wav"); print("ok")
