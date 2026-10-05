import sys, os, argparse
sys.path.insert(0, "/home/claude/doctorgane/kin")
from kinetic import *
PH = "/home/claude/doctorgane/kin/photos/"
ap = argparse.ArgumentParser(); ap.add_argument("--out"); ap.add_argument("--preview"); ap.add_argument("--music"); ap.add_argument("--gain", type=float, default=0.5); args = ap.parse_args()
M = "Medium"

# S0 — couverture (image 1 = miniature Instagram/TikTok), statique 0,8 s
s0 = [Photo(PH + "cnhm.jpg", 600, w=1000, h=740, t0=-1.0, dur=0.01, zoom=1.06, dim=0.6, snd=None),
      Word("UN DINOSAURE", 540, 1120, 125, CREAM, -1.0, dur=0.01, anim="fade", snd=None),
      Word("A EU UN CANCER.", 540, 1260, 125, CORAL, -1.0, dur=0.01, anim="fade", snd=None),
      Word("il y a 76 millions d'années", 540, 1400, 54, GREY, -1.0, dur=0.01, anim="fade", font="pop", snd=None)]
S0 = Scene(0.8, s0, bg=DARK, flash=False)

# S1 — accroche : crâne de Centrosaurus + date vertigineuse
s1 = [Photo(PH + "cnhm.jpg", 520, w=1000, h=720, t0=0.0, dur=0.5, zoom=1.14, dim=0.65),
      Word("IL Y A", 540, 960, 70, GREY, 0.45, anim="up", font="pop", snd=None),
      Word("76 MILLIONS", 540, 1090, 170, CORAL, 0.7, anim="slam", snd="slam"),
      Word("D'ANNÉES,", 540, 1230, 110, CREAM, 0.95, anim="pop"),
      Word("UN DINOSAURE", 540, 1400, 96, CREAM, 1.6, anim="pop"),
      Word("A EU UN CANCER.", 540, 1510, 96, CORAL, 1.85, anim="pop"),
      Word("Centrosaurus · os de la jambe · Alberta, Canada", 540, 1660, 36, GREY, 2.6, anim="fade", font="Regular", snd=None)]
S1 = Scene(3.9, s1, bg=DARK)

# S2 — un vrai diagnostic
s2 = [Word("PAS UNE LÉGENDE.", 540, 430, 110, CREAM, 0.1, anim="pop"),
      Word("UN DIAGNOSTIC.", 540, 560, 110, CREAM, 0.4, anim="pop"),
      Word("Scanner, microscope, comparaison avec", 540, 760, 46, GREY, 1.0, anim="up", font=M, snd=None),
      Word("des tumeurs humaines. Comme pour un patient.", 540, 820, 46, GREY, 1.15, anim="up", font=M, snd=None),
      Word("VERDICT :", 540, 1020, 70, GREY, 1.8, anim="up", font="pop", snd=None),
      Word("OSTÉOSARCOME.", 540, 1180, 130, CREAM, 2.1, anim="slam", box=CORAL, snd="slam"),
      Word("Un cancer de l'os, agressif.", 540, 1340, 46, CREAM, 2.8, anim="up", font=M, snd=None),
      Word("Le même qu'on soigne chez l'humain.", 540, 1400, 46, CREAM, 2.95, anim="up", font=M, snd=None),
      Word("The Lancet Oncology · 2020", 540, 1560, 36, GREY, 3.3, anim="fade", font="Regular", snd=None)]
S2 = Scene(4.4, s2, bg=NAVY)

# S3 — et ce n'est pas le seul : la frise
s3 = [Photo(PH + "museum.jpg", 480, w=1000, h=680, t0=0.0, dur=0.5, zoom=1.12, dim=0.6),
      Word("ET CE N'EST PAS LE SEUL.", 540, 900, 84, CREAM, 0.5, anim="pop"),
      Word("– 1,7 million d'années", 80, 1060, 56, CORAL, 1.1, anim="up", font="pop", align="l", snd="pop"),
      Word("un ancêtre humain, Afrique du Sud", 80, 1125, 42, GREY, 1.2, anim="up", font=M, align="l", snd=None),
      Word("– 1600 av. J.-C.", 80, 1250, 56, CORAL, 1.9, anim="up", font="pop", align="l", snd="pop"),
      Word("un papyrus égyptien décrit des tumeurs du sein", 80, 1315, 42, GREY, 2.0, anim="up", font=M, align="l", snd=None),
      Word("– 400 av. J.-C.", 80, 1440, 56, CORAL, 2.7, anim="up", font="pop", align="l", snd="pop"),
      Word("Hippocrate lui donne un nom : karkinos, le crabe", 80, 1505, 42, GREY, 2.8, anim="up", font=M, align="l", snd=None),
      Word("Galerie de paléontologie, Paris", 540, 1660, 34, GREY, 3.4, anim="fade", font="Regular", snd=None)]
S3 = Scene(4.8, s3, bg=DARK)

# S4 — donc non
s4 = [Word("DONC NON.", 540, 420, 150, CREAM, 0.1, anim="slam", snd="slam"),
      Word("LE CANCER N'A PAS ÉTÉ", 540, 640, 86, CREAM, 0.7, anim="pop"),
      Word("INVENTÉ PAR", 540, 740, 86, CREAM, 0.9, anim="pop"),
      Word("LA VIE MODERNE.", 540, 870, 110, CORAL, 1.15, anim="slam", snd="slam"),
      Word("Ce qui a changé ?", 540, 1120, 56, GREY, 2.0, anim="up", font="pop", snd=None),
      Word("On vit deux fois plus longtemps.", 540, 1230, 60, CREAM, 2.4, anim="up", font="pop", snd="pop"),
      Word("Et on sait le chercher.", 540, 1320, 60, CREAM, 2.8, anim="up", font="pop", snd="pop")]
S4 = Scene(4.2, s4, bg=NAVY)

# S5 — le prix d'être vivant
s5 = [Word("C'EST LE PRIX", 540, 380, 120, CREAM, 0.1, anim="pop"),
      Word("D'ÊTRE VIVANT.", 540, 520, 120, CORAL, 0.4, anim="pop"),
      Word("Des milliers de milliards de cellules", 540, 700, 46, GREY, 1.0, anim="up", font=M, snd=None),
      Word("qui se copient, jour et nuit, depuis toujours.", 540, 760, 46, GREY, 1.1, anim="up", font=M, snd=None),
      Grid(48, 8, 540, 1080, 84, 16, (52, 66, 104), 1.4, 0.03),
      Grid(1, 1, 690, 1030, 84, 16, CORAL, 3.0, 0.05, snd="slam"),
      Word("Parfois, une copie se trompe.", 540, 1420, 60, CREAM, 3.2, anim="up", font="pop", snd=None),
      Word("Chez un dinosaure. Chez un pharaon. Chez nous.", 540, 1510, 46, GREY, 3.7, anim="up", font=M, snd=None)]
S5 = Scene(5.0, s5, bg=DARK)

# S6 — chute
s6 = [Word("CE QUI EST NOUVEAU,", 540, 360, 90, CREAM, 0.1, anim="pop"),
      Word("CE N'EST PAS LE CANCER.", 540, 470, 90, CREAM, 0.35, anim="pop"),
      Word("C'EST QU'ON SAIT", 540, 680, 110, CREAM, 1.0, anim="slam", snd="slam"),
      Word("LE SOIGNER.", 540, 820, 130, CREAM, 1.25, anim="slam", box=CORAL, snd="slam"),
      Word("Le papyrus disait : « il n'y a pas de traitement ».", 540, 1040, 44, GREY, 2.0, anim="up", font=M, snd=None),
      Word("Aujourd'hui, en France, survie à 5 ans :", 540, 1180, 46, CREAM, 2.5, anim="up", font=M, snd=None),
      Word("SEIN  88 %", 540, 1290, 84, CORAL, 2.9, anim="pop"),
      Word("PROSTATE  93 %", 540, 1390, 84, CORAL, 3.1, anim="pop"),
      Word("TESTICULE  96 %", 540, 1490, 84, CORAL, 3.3, anim="pop"),
      Word("Partage-le à quelqu'un qui aime les dinosaures.", 540, 1660, 42, GREY, 4.0, anim="up", font="pop", snd=None)]
S6 = Scene(5.6, s6, bg=NAVY)

film = Film([S0, S1, S2, S3, S4, S5, S6])
print("durée", round(film.dur, 2), [round(b, 2) for b in film.bounds])
if args.preview:
    os.makedirs("prev", exist_ok=True)
    import glob
    for f_ in glob.glob("prev/d_*.png"): os.remove(f_)
    for tt in [float(x) for x in args.preview.split(",")]: film.frame(tt).save(f"prev/d_{tt:05.2f}.png")
    sys.exit()
mus = load_music(args.music, film.dur) if args.music else None
film.make_audio("sound_dino.wav", music=mus, music_gain=args.gain)
film.encode(args.out or "dino_kin.mp4", "sound_dino.wav"); print("ok")
