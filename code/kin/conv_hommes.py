import sys, os, argparse
sys.path.insert(0, "/home/claude/doctorgane/kin")
from chat import *
ap = argparse.ArgumentParser(); ap.add_argument("--out"); ap.add_argument("--preview"); args = ap.parse_args()
M = [("R", "Doctorgane, question bizarre 😅", 0.6),
     ("R", "mon père a une boule sous le téton", 1.7),
     ("R", "il dit que c'est impossible, le cancer du sein c'est pour les femmes", 2.9),
     ("R", "il a raison non ?", 4.8),
     ("L", "Non.", 6.5),
     ("L", "Environ 1 cancer du sein sur 100 touche un homme.", 7.5),
     ("L", "Et chez eux, on le trouve souvent plus tard. Justement parce que personne n'y pense.", 9.4),
     ("R", "ok mais c'est sûrement rien", 12.3),
     ("L", "Probablement. Mais « probablement », ça ne se vérifie pas en rigolant.", 14.4),
     ("L", "Une boule derrière le mamelon, un mamelon qui rentre, une plaie qui ne guérit pas : on fait examiner.", 16.6),
     ("L", "Prends-lui rendez-vous cette semaine. Chez son médecin, c'est 10 minutes.", 19.6, "SemiBold"),
     ("R", "ok je l'appelle ce soir 🙏", 22.4),
     ("L", "Et si c'est rien, vous aurez perdu 10 minutes. Ça vaut le coup.", 23.6)]
chat = Chat(M)
chat.add_typing(5.5, 6.5); chat.add_typing(13.4, 14.4); chat.add_typing(22.9, 23.6)
end = EndCard(27.0, [("Conversation imaginée, inspirée de vraies questions.", 34, GREY, "Regular"), ("", 40, GREY, "Regular"),
                     ("LES HOMMES AUSSI.", 96, CREAM, "anton"), ("ENVOIE-LE À UN HOMME QUE TU AIMES.", 60, CORAL, "anton"),
                     ("", 30, GREY, "Regular"), ("Pose-moi ta question en commentaire.", 40, CREAM, "Regular")])
film = Film([Scene(31.5, [chat, end])])
print("durée", film.dur)
if args.preview:
    os.makedirs("prev", exist_ok=True)
    for tt in [float(x) for x in args.preview.split(",")]: film.frame(tt).save(f"prev/h_{tt:05.2f}.png")
    sys.exit()
mus = load_music("/home/claude/doctorgane/kin/music_deliberate.mp3", film.dur, fade_out=2.5)
film.make_audio("sound_h.wav", music=mus, music_gain=0.45)
film.encode(args.out or "conv_hommes.mp4", "sound_h.wav"); print("ok")
