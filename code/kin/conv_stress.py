import sys, os, argparse
sys.path.insert(0, "/home/claude/doctorgane/kin")
from chat import *
ap = argparse.ArgumentParser(); ap.add_argument("--out"); ap.add_argument("--preview"); args = ap.parse_args()

# (côté, texte, instant) — R = Léa (droite, corail), L = Doctorgane (gauche)
M = [("R", "Doctorgane, t'es là ? 😭", 0.6),
     ("R", "ma tante a un cancer du sein", 1.7),
     ("R", "elle dit que c'est le stress de son divorce qui lui a donné ça", 2.9),
     ("R", "c'est possible ???", 4.6),
     ("L", "Non.", 6.4),
     ("L", "On a suivi 106 000 femmes pendant des années.", 7.4),
     ("L", "Stress, séparations, deuils : aucun lien solide avec l'apparition d'un cancer du sein.", 9.2),
     ("R", "mais elle est persuadée que c'est sa faute", 12.0),
     ("L", "Alors dis-lui ça de ma part :", 14.2),
     ("L", "Elle n'y est pour rien.", 15.4, "SemiBold"),
     ("L", "Le stress, c'est ce qu'elle a vécu. Pas ce qui l'a rendue malade.", 16.6),
     ("R", "je lui envoie ça 🤍", 19.3),
     ("L", "Et sois là pour elle. Ça, ça compte vraiment.", 21.0)]
chat = Chat(M)
chat.add_typing(5.4, 6.4); chat.add_typing(13.3, 14.2); chat.add_typing(20.2, 21.0)
end = EndCard(24.2, [("Conversation imaginée, inspirée de vraies questions.", 34, GREY, "Regular"),
                     ("", 40, GREY, "Regular"),
                     ("POSE-MOI TA QUESTION", 96, CREAM, "anton"),
                     ("EN COMMENTAIRE.", 96, CORAL, "anton"),
                     ("", 30, GREY, "Regular"),
                     ("Je réponds ici, sans peur et sans jargon.", 40, CREAM, "Regular")])
film = Film([Scene(28.5, [chat, end])])
print("durée", film.dur)
if args.preview:
    os.makedirs("prev", exist_ok=True)
    import glob
    for f_ in glob.glob("prev/c_*.png"): os.remove(f_)
    for tt in [float(x) for x in args.preview.split(",")]: film.frame(tt).save(f"prev/c_{tt:05.2f}.png")
    sys.exit()
mus = load_music("/home/claude/doctorgane/kin/music_deliberate.mp3", film.dur, fade_out=2.5)
film.make_audio("sound_conv.wav", music=mus, music_gain=0.45)
film.encode(args.out or "conv_stress.mp4", "sound_conv.wav"); print("ok")
