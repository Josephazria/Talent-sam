import sys, os, argparse
sys.path.insert(0, "/home/claude/doctorgane/kin")
from kinetic import *
PH = "/home/claude/doctorgane/reel6/photos/"
ap = argparse.ArgumentParser(); ap.add_argument("--out"); ap.add_argument("--preview"); args = ap.parse_args()

# S1 accroche — photo Masai + typo
s1 = [Photo(PH + "masai.jpg", 560, w=1000, t0=0.0, dur=0.5, zoom=1.10),
      Word("UN ÉLÉPHANT", 540, 1010, 150, CREAM, 0.55, anim="pop"),
      Word("A 100× PLUS", 540, 1160, 150, CORAL, 0.85, anim="pop"),
      Word("DE CELLULES QUE TOI.", 540, 1300, 110, CREAM, 1.15, anim="pop"),
      Word("Il devrait avoir 100× plus de cancers.", 540, 1480, 50, GREY, 2.0, anim="up", font="pop", snd=None)]
S1 = Scene(3.6, s1, bg=DARK)

# S2 il en a moins + barres
s2 = [Word("IL EN A", 540, 420, 130, CREAM, 0.1, anim="pop"),
      Word("MOINS.", 540, 640, 300, CORAL, 0.4, anim="slam", snd="slam"),
      Word("Meurent d'un cancer", 540, 900, 46, GREY, 1.1, anim="up", font="pop", snd=None),
      Bar("Éléphants : moins de 5 %", 5, 25, 1090, CORAL, 1.3),
      Bar("Humains : 11 à 25 %", 18, 25, 1330, CREAM, 1.9),
      Word("644 éléphants autopsiés · 2015", 540, 1500, 36, GREY, 2.6, anim="fade", font="Regular", snd=None)]
S2 = Scene(4.4, s2, bg=NAVY)

# S3 le gène : 1 copie vs 20
s3 = [Word("DANS CHAQUE CELLULE,", 540, 290, 90, CREAM, 0.1, anim="pop"),
      Word("UN GÈNE SURVEILLE LES ERREURS.", 540, 400, 72, CREAM, 0.4, anim="pop"),
      Word("TOI", 540, 560, 64, GREY, 1.0, anim="up", font="pop", snd=None),
      Grid(1, 1, 540, 665, 96, 0, CREAM, 1.1, 0.05),
      Word("1 COPIE", 540, 790, 80, CREAM, 1.35, anim="pop"),
      Word("L'ÉLÉPHANT", 540, 930, 64, GREY, 1.8, anim="up", font="pop", snd=None),
      Grid(20, 5, 540, 1180, 84, 14, CORAL, 1.9, 0.06),
      Word("20 COPIES", 540, 1470, 130, CORAL, 3.2, anim="slam", snd="slam")]
S3 = Scene(5.2, s3, bg=NAVY)

# S4 il élimine plus vite — photo œil
s4 = [Photo(PH + "memory.jpg", 480, w=1000, t0=0.0, dur=0.5, zoom=1.12, dim=0.6),
      Word("IL NE RÉPARE", 540, 930, 120, CREAM, 0.5, anim="pop"),
      Word("PAS MIEUX.", 540, 1050, 120, CREAM, 0.75, anim="pop"),
      Word("IL ÉLIMINE", 540, 1240, 130, CORAL, 1.3, anim="slam", snd="slam"),
      Word("PLUS VITE.", 540, 1370, 130, CORAL, 1.55, anim="slam", snd="slam"),
      Word("Une cellule abîmée reçoit l'ordre de mourir, 2× plus souvent que chez nous.", 540, 1500, 38, GREY, 2.3, anim="up", font="pop", snd=None)]
S4 = Scene(5.0, s4, bg=DARK)

# S5 vertige
s5 = [Word("CHEZ L'HUMAIN,", 540, 440, 90, GREY, 0.1, anim="pop"),
      Word("QUAND CE GÈNE", 540, 560, 110, CREAM, 0.35, anim="pop"),
      Word("EST EN PANNE,", 540, 680, 110, CREAM, 0.6, anim="pop"),
      Word("LE CANCER ARRIVE", 540, 900, 110, CORAL, 1.3, anim="pop"),
      Word("PRESQUE À COUP SÛR.", 540, 1020, 110, CORAL, 1.6, anim="pop"),
      Word("(syndrome de Li-Fraumeni, maladie génétique rare)", 540, 1120, 34, GREY, 2.2, anim="fade", font="Regular", snd=None),
      Word("C'EST DIRE CE QU'IL VAUT.", 540, 1330, 96, CREAM, 2.7, anim="slam", box=CORAL, snd="slam")]
S5 = Scene(4.6, s5, bg=NAVY)

# S6 chute — photo mère et petit
s6 = [Photo(PH + "calf.jpg", 520, w=1000, t0=0.0, dur=0.5, zoom=1.10),
      Word("DES CHERCHEURS TESTENT", 540, 960, 78, CREAM, 0.5, anim="pop"),
      Word("LA VERSION ÉLÉPHANT DE CE GÈNE", 540, 1050, 62, CREAM, 0.8, anim="pop"),
      Word("CONTRE DES CANCERS HUMAINS.", 540, 1140, 70, CORAL, 1.1, anim="pop"),
      Word("LA RÉPONSE ÉTAIT PEUT-ÊTRE", 540, 1330, 76, CREAM, 2.0, anim="pop"),
      Word("DANS LA SAVANE.", 540, 1440, 120, CORAL, 2.3, anim="slam", snd="slam"),
      Word("Partage-le à quelqu'un qui aime les éléphants", 540, 1580, 40, GREY, 3.2, anim="up", font="pop", snd=None)]
S6 = Scene(5.6, s6, bg=DARK)

film = Film([S1, S2, S3, S4, S5, S6])
print("durée", round(film.dur, 2), [round(b, 2) for b in film.bounds])
if args.preview:
    os.makedirs("prev", exist_ok=True)
    import glob
    for f_ in glob.glob("prev/p_*.png"): os.remove(f_)
    for tt in [float(x) for x in args.preview.split(",")]: film.frame(tt).save(f"prev/p_{tt:05.2f}.png")
    sys.exit()
mus = load_music("/home/claude/doctorgane/reel6/music_carefree.mp3", film.dur)
film.make_audio("sound.wav", music=mus, music_gain=0.55)
film.encode(args.out or "elephants_kin.mp4", "sound.wav"); print("ok")
